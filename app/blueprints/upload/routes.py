"""
Upload Routes - Processamento temporário de novos arquivos
"""
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from app.blueprints.upload import upload_bp
from app.models import JournalEntry, BaseMarcacao, get_db_session
from app.blueprints.upload.processors import processar_fatura_itau, processar_extrato_itau, processar_mercado_pago
from app.blueprints.upload.classifiers import classificar_transacoes, regenerar_padroes
from app.utils import deduplicate_transactions, get_duplicados_temp, clear_duplicados_temp
from sqlalchemy import or_


# Constantes
UPLOAD_FOLDER = 'uploads_temp'


def identificar_tipo_arquivo(filename):
    """Identifica tipo de arquivo pelo nome"""
    filename_lower = filename.lower()
    
    if 'fatura_itau' in filename_lower or 'fatura itau' in filename_lower:
        return 'fatura_itau'
    elif 'extrato conta corrente' in filename_lower:
        return 'extrato_itau'
    elif 'account_statement' in filename_lower or 'mercado pago' in filename_lower:
        return 'mercado_pago'
    
    return None


@upload_bp.route('/', methods=['GET', 'POST'])
def upload():
    """Página de Upload de Arquivos"""
    
    if request.method == 'POST':
        # Limpa duplicados temporários de uploads anteriores
        clear_duplicados_temp()
        
        # Processar upload de arquivos
        if 'files[]' not in request.files:
            flash('Nenhum arquivo selecionado', 'danger')
            return redirect(request.url)
        
        files = request.files.getlist('files[]')
        
        if not files or all(f.filename == '' for f in files):
            flash('Nenhum arquivo selecionado', 'danger')
            return redirect(request.url)
        
        # Processa todos os arquivos
        todas_transacoes = []
        arquivos_processados = []
        
        for file in files:
            if file and file.filename:
                # Salva temporariamente
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                # Identifica tipo
                tipo = identificar_tipo_arquivo(filename)
                
                if not tipo:
                    flash(f'Arquivo {filename} não reconhecido. Use nomes: fatura_itau, Extrato Conta Corrente, ou account_statement', 'warning')
                    os.remove(filepath)
                    continue
                
                # Processa
                try:
                    if tipo == 'fatura_itau':
                        transacoes = processar_fatura_itau(filepath, filename)
                    elif tipo == 'extrato_itau':
                        transacoes = processar_extrato_itau(filepath, filename)
                    elif tipo == 'mercado_pago':
                        transacoes = processar_mercado_pago(filepath, filename)
                    
                    todas_transacoes.extend(transacoes)
                    arquivos_processados.append({
                        'nome': filename,
                        'tipo': tipo,
                        'transacoes': len(transacoes)
                    })
                    
                except Exception as e:
                    flash(f'Erro ao processar {filename}: {str(e)}', 'danger')
                
                # Remove arquivo temporário
                os.remove(filepath)
        
        if not todas_transacoes:
            flash('Nenhuma transação foi extraída dos arquivos', 'warning')
            return redirect(url_for('upload.upload'))
        
        # Remove transações futuras
        transacoes_atuais = [t for t in todas_transacoes if t.get('TransacaoFutura') == 'NÃO']
        futuras_removidas = len(todas_transacoes) - len(transacoes_atuais)
        
        # Deduplica contra journal_entries
        transacoes_unicas, duplicados_count = deduplicate_transactions(transacoes_atuais)
        
        # Classifica automaticamente
        transacoes_classificadas = classificar_transacoes(transacoes_unicas)
        
        # Armazena em sessão com namespace
        session['upload.transacoes'] = transacoes_classificadas
        session['upload.arquivos_processados'] = arquivos_processados
        session['upload.duplicados_count'] = duplicados_count
        session['upload.futuras_removidas'] = futuras_removidas
        
        flash(f'{len(transacoes_classificadas)} transações processadas com sucesso!', 'success')
        if duplicados_count > 0:
            flash(f'{duplicados_count} duplicados removidos', 'info')
        if futuras_removidas > 0:
            flash(f'{futuras_removidas} transações futuras removidas', 'info')
        
        return redirect(url_for('upload.revisao_upload'))
    
    # GET - Mostra formulário de upload
    return render_template('upload.html')


@upload_bp.route('/revisao_upload')
def revisao_upload():
    """Dashboard com resumo das transações processadas"""
    
    transacoes = session.get('upload.transacoes', [])
    
    if not transacoes:
        flash('Nenhuma transação em processamento. Faça upload de arquivos primeiro.', 'warning')
        return redirect(url_for('upload.upload'))
    
    # Agrupa por origem
    por_origem = {}
    for trans in transacoes:
        origem = trans.get('origem', 'Desconhecido')
        if origem not in por_origem:
            por_origem[origem] = []
        por_origem[origem].append(trans)
    
    # Calcula estatísticas por origem
    stats_por_origem = {}
    for origem, trans_list in por_origem.items():
        # Identifica se é fatura ou extrato
        eh_fatura = 'Fatura' in origem or 'Cartão' in trans_list[0].get('TipoTransacao', '')
        
        if eh_fatura:
            # Para faturas: total e breakdown por TipoGasto
            total = sum(t.get('Valor', 0) for t in trans_list)
            
            por_tipo_gasto = {}
            for t in trans_list:
                tipo = t.get('TipoGasto') or 'Não Classificado'
                valor = t.get('Valor', 0)
                por_tipo_gasto[tipo] = por_tipo_gasto.get(tipo, 0) + valor
            
            stats_por_origem[origem] = {
                'tipo': 'fatura',
                'total': total,
                'quantidade': len(trans_list),
                'breakdown': por_tipo_gasto
            }
        else:
            # Para extratos: despesas e receitas separadas
            despesas = sum(t.get('Valor', 0) for t in trans_list if t.get('Valor', 0) < 0)
            receitas = sum(t.get('Valor', 0) for t in trans_list if t.get('Valor', 0) > 0)
            
            stats_por_origem[origem] = {
                'tipo': 'extrato',
                'despesas': abs(despesas),
                'receitas': receitas,
                'saldo': receitas + despesas,
                'quantidade': len(trans_list)
            }
    
    # Conta transações que precisam validação
    precisam_validacao = sum(1 for t in transacoes if t.get('ValidarIA') == 'VALIDAR')
    
    duplicados_count = session.get('upload.duplicados_count', 0)
    
    return render_template(
        'revisao_upload.html',
        stats_por_origem=stats_por_origem,
        origens=list(por_origem.keys()),
        total_transacoes=len(transacoes),
        precisam_validacao=precisam_validacao,
        duplicados_count=duplicados_count
    )


@upload_bp.route('/duplicados')
def duplicados():
    """Visualizar duplicados temporários"""
    
    duplicados_list = get_duplicados_temp()
    
    return render_template('duplicados.html', duplicados=duplicados_list)


@upload_bp.route('/revisar/categoria/<tipo_gasto>')
def revisar_categoria(tipo_gasto):
    """Visualizar transações de uma categoria específica"""
    
    transacoes = session.get('upload.transacoes', [])
    
    if not transacoes:
        flash('Nenhuma transação em processamento. Faça upload de arquivos primeiro.', 'warning')
        return redirect(url_for('upload.upload'))
    
    # Filtra transações pela categoria com índice
    transacoes_categoria = []
    for idx, t in enumerate(transacoes):
        if t.get('TipoGasto') == tipo_gasto:
            transacoes_categoria.append({
                'indice': idx,
                'transacao': t
            })
    
    # Calcula total
    total_valor = sum(item['transacao'].get('Valor', 0) for item in transacoes_categoria)
    
    # Carrega marcações para dropdown
    db_session = get_db_session()
    marcacoes = db_session.query(BaseMarcacao).all()
    db_session.close()
    
    # Organiza dados para dropdowns
    grupos_dict = {}
    tipo_gasto_dict = {}
    
    for m in marcacoes:
        if m.GRUPO not in grupos_dict:
            grupos_dict[m.GRUPO] = set()
        grupos_dict[m.GRUPO].add(m.SUBGRUPO)
        
        chave = f"{m.GRUPO}|{m.SUBGRUPO}"
        tipo_gasto_dict[chave] = m.TipoGasto
    
    # Converte sets para listas
    grupos_dict = {k: sorted(list(v)) for k, v in grupos_dict.items()}
    grupos = sorted(grupos_dict.keys())
    
    return render_template(
        'revisar_categoria.html',
        transacoes=transacoes_categoria,
        tipo_gasto=tipo_gasto,
        total_valor=total_valor,
        grupos=grupos,
        grupos_dict=grupos_dict,
        tipo_gasto_dict=tipo_gasto_dict
    )


@upload_bp.route('/validar')
def validar():
    """Página para validar transações da sessão que não foram classificadas"""
    
    transacoes = session.get('upload.transacoes', [])
    
    if not transacoes:
        flash('Nenhuma transação em processamento. Faça upload de arquivos primeiro.', 'warning')
        return redirect(url_for('upload.upload'))
    
    # Filtra apenas as que precisam validação
    transacoes_validar = [t for t in transacoes if t.get('ValidarIA') == 'VALIDAR']
    
    # Carrega marcações para dropdown
    db_session = get_db_session()
    marcacoes = db_session.query(BaseMarcacao).all()
    db_session.close()
    
    # Organiza dados para dropdowns
    grupos_dict = {}
    tipo_gasto_dict = {}
    
    for m in marcacoes:
        if m.GRUPO not in grupos_dict:
            grupos_dict[m.GRUPO] = set()
        grupos_dict[m.GRUPO].add(m.SUBGRUPO)
        
        chave = f"{m.GRUPO}|{m.SUBGRUPO}"
        tipo_gasto_dict[chave] = m.TipoGasto
    
    # Converte sets para listas
    grupos_dict = {k: sorted(list(v)) for k, v in grupos_dict.items()}
    grupos = sorted(grupos_dict.keys())
    
    # Paginação
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    total = len(transacoes_validar)
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 1
    start = (page - 1) * per_page
    end = start + per_page
    transacoes_pagina = transacoes_validar[start:end]
    
    # Adiciona índice original para cada transação (para identificar na sessão)
    transacoes_com_indice = []
    for trans in transacoes_pagina:
        idx = transacoes.index(trans)
        transacoes_com_indice.append({
            'indice': idx,
            'transacao': trans
        })
    
    return render_template(
        'validar.html',
        transacoes=transacoes_com_indice,
        page=page,
        total_pages=total_pages,
        per_page=per_page,
        total=total,
        grupos=grupos,
        grupos_dict=grupos_dict,
        tipo_gasto_dict=tipo_gasto_dict
    )


@upload_bp.route('/validar/lote', methods=['POST'])
def validar_lote():
    """Aplica classificação em lote para múltiplas transações na sessão"""
    try:
        data = request.get_json()
        indices = data.get('indices', [])
        grupo = data.get('grupo', '')
        subgrupo = data.get('subgrupo', '')
        tipo_gasto = data.get('tipo_gasto', '')
        
        transacoes = session.get('upload.transacoes', [])
        
        if not indices:
            return jsonify({'success': False, 'message': 'Nenhuma transação selecionada'}), 400
        
        if not grupo or not subgrupo or not tipo_gasto:
            return jsonify({'success': False, 'message': 'Grupo, Subgrupo e Tipo de Gasto são obrigatórios'}), 400
        
        count = 0
        for idx in indices:
            idx = int(idx)
            if 0 <= idx < len(transacoes):
                transacoes[idx]['GRUPO'] = grupo
                transacoes[idx]['SUBGRUPO'] = subgrupo
                transacoes[idx]['TipoGasto'] = tipo_gasto
                transacoes[idx]['MarcacaoIA'] = 'Manual (Lote)'
                transacoes[idx]['ValidarIA'] = ''
                count += 1
        
        session['upload.transacoes'] = transacoes
        session.modified = True
        
        return jsonify({'success': True, 'message': f'{count} transações classificadas com sucesso'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@upload_bp.route('/salvar', methods=['POST'])
def salvar():
    """Salva transações selecionadas no journal_entries (ponte para dados permanentes)"""
    
    transacoes = session.get('upload.transacoes', [])
    
    if not transacoes:
        flash('Nenhuma transação para salvar', 'warning')
        return redirect(url_for('upload.upload'))
    
    # Pega origens selecionadas
    origens_selecionadas = request.form.getlist('origens_selecionadas')
    
    if not origens_selecionadas:
        flash('Selecione pelo menos uma origem para salvar', 'warning')
        return redirect(url_for('upload.revisao_upload'))
    
    # Filtra transações por origens selecionadas
    transacoes_salvar = [
        t for t in transacoes
        if t.get('origem') in origens_selecionadas
    ]
    
    if not transacoes_salvar:
        flash('Nenhuma transação das origens selecionadas', 'warning')
        return redirect(url_for('upload.revisao_upload'))
    
    # Salva no banco
    db_session = get_db_session()
    
    try:
        salvos = 0
        for trans in transacoes_salvar:
            # Verifica se deve ignorar no dashboard
            grupo = trans.get('GRUPO')
            ignorar = grupo in ['Transferências', 'Investimentos']
            
            entry = JournalEntry(
                IdTransacao=trans.get('IdTransacao'),
                Data=trans.get('Data'),
                Estabelecimento=trans.get('Estabelecimento'),
                Valor=trans.get('Valor'),
                ValorPositivo=trans.get('ValorPositivo'),
                TipoTransacao=trans.get('TipoTransacao'),
                TipoTransacaoAjuste=trans.get('TipoTransacaoAjuste'),
                TipoGasto=trans.get('TipoGasto'),
                GRUPO=grupo,
                SUBGRUPO=trans.get('SUBGRUPO'),
                Ano=trans.get('Ano'),
                DT_Fatura=trans.get('DT_Fatura'),
                NomeTitular=trans.get('NomeTitular'),
                DataPostagem=trans.get('DataPostagem'),
                origem=trans.get('origem'),
                MarcacaoIA=trans.get('MarcacaoIA'),
                ValidarIA=trans.get('ValidarIA'),
                CartaoCodigo8=trans.get('CartaoCodigo8'),
                FinalCartao=trans.get('FinalCartao'),
                TipoLancamento=trans.get('TipoLancamento'),
                TransacaoFutura=trans.get('TransacaoFutura'),
                IdOperacao=trans.get('IdOperacao'),
                IgnorarDashboard=ignorar,
                created_at=datetime.utcnow()
            )
            db_session.add(entry)
            salvos += 1
        
        db_session.commit()
        
        # Limpa duplicados temporários
        clear_duplicados_temp()
        
        # Limpa sessão do upload
        session.pop('upload.transacoes', None)
        session.pop('upload.arquivos_processados', None)
        session.pop('upload.duplicados_count', None)
        session.pop('upload.futuras_removidas', None)
        
        # Regenera padrões
        regenerar_padroes()
        
        flash(f'{salvos} transações salvas com sucesso!', 'success')
        
    except Exception as e:
        db_session.rollback()
        flash(f'Erro ao salvar: {str(e)}', 'danger')
    finally:
        db_session.close()
    
    return redirect(url_for('upload.upload'))


@upload_bp.route('/api/adicionar_marcacao', methods=['POST'])
def adicionar_marcacao():
    """API para adicionar nova combinação de grupo/subgrupo/tipogasto"""
    
    try:
        grupo = request.form.get('grupo', '').strip()
        subgrupo = request.form.get('subgrupo', '').strip()
        tipo_gasto = request.form.get('tipo_gasto', '').strip()
        
        if not grupo or not subgrupo or not tipo_gasto:
            return jsonify({'success': False, 'error': 'Todos os campos são obrigatórios'}), 400
        
        db_session = get_db_session()
        
        # Verifica se já existe
        existe = db_session.query(BaseMarcacao).filter_by(
            GRUPO=grupo,
            SUBGRUPO=subgrupo
        ).first()
        
        if existe:
            db_session.close()
            return jsonify({'success': False, 'error': 'Esta combinação já existe'}), 400
        
        # Cria nova marcação
        nova_marcacao = BaseMarcacao(
            GRUPO=grupo,
            SUBGRUPO=subgrupo,
            TipoGasto=tipo_gasto,
            created_at=datetime.utcnow()
        )
        
        db_session.add(nova_marcacao)
        db_session.commit()
        db_session.close()
        
        return jsonify({
            'success': True,
            'grupo': grupo,
            'subgrupo': subgrupo,
            'tipo_gasto': tipo_gasto
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@upload_bp.route('/api/marcacoes', methods=['GET'])
def listar_marcacoes():
    """API para listar todas as marcações"""
    
    try:
        db_session = get_db_session()
        marcacoes = db_session.query(BaseMarcacao).order_by(BaseMarcacao.GRUPO, BaseMarcacao.SUBGRUPO).all()
        
        resultado = []
        for m in marcacoes:
            resultado.append({
                'id': m.id,
                'grupo': m.GRUPO,
                'subgrupo': m.SUBGRUPO,
                'tipo_gasto': m.TipoGasto
            })
        
        db_session.close()
        
        return jsonify({'success': True, 'marcacoes': resultado})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
