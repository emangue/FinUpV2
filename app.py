"""
Aplicação Flask - Sistema de Gestão Financeira
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json

# Imports locais
from config import Config
from models import JournalEntry, BasePadrao, BaseMarcacao, AuditLog, GrupoConfig, EstabelecimentoLogo, get_db_session, init_db
from sqlalchemy import or_
from processors import processar_fatura_itau, processar_extrato_itau, processar_mercado_pago
from classifiers import classificar_transacoes, regenerar_padroes
from utils import deduplicate_transactions, get_duplicados_temp, clear_duplicados_temp, get_duplicados_count

# Inicializa Flask
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

# Configurar Flask-Session para usar filesystem
from flask_session import Session
Session(app)

# Pasta de uploads temporários
UPLOAD_FOLDER = 'uploads_temp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Pasta de logos
LOGOS_FOLDER = 'static/logos'
os.makedirs(LOGOS_FOLDER, exist_ok=True)
app.config['LOGOS_FOLDER'] = LOGOS_FOLDER
app.config['MAX_LOGO_SIZE'] = 2 * 1024 * 1024  # 2MB

# Inicializa banco de dados
init_db()

# Template helpers - Funções customizadas para Jinja2
@app.template_filter('get_group_icon')
def get_group_icon(grupo):
    """Retorna ícone Font Awesome para cada grupo (do banco ou padrão)"""
    if not grupo:
        return 'fa-tag'
    
    db = get_db_session()
    try:
        config = db.query(GrupoConfig).filter_by(nome=grupo, ativo=True).first()
        if config:
            return config.icone
    finally:
        db.close()
    
    # Fallback para ícones padrão
    icons = {
        'Alimentação': 'fa-utensils',
        'Transporte': 'fa-car',
        'Moradia': 'fa-home',
        'Saúde': 'fa-heartbeat',
        'Educação': 'fa-graduation-cap',
        'Lazer': 'fa-gamepad',
        'Assinaturas': 'fa-file-invoice',
        'Vestuário': 'fa-tshirt',
        'Investimentos': 'fa-chart-line',
        'Impostos': 'fa-landmark',
        'Seguros': 'fa-shield-alt',
        'Doações': 'fa-hand-holding-heart'
    }
    return icons.get(grupo, 'fa-tag')

@app.template_filter('get_group_color')
def get_group_color(grupo):
    """Retorna cor hexadecimal para cada grupo (do banco ou padrão)"""
    if not grupo:
        return '#6c757d'
    
    db = get_db_session()
    try:
        config = db.query(GrupoConfig).filter_by(nome=grupo, ativo=True).first()
        if config:
            return config.cor
    finally:
        db.close()
    
    # Fallback para cores padrão
    colors = {
        'Alimentação': '#FF6384',
        'Transporte': '#36A2EB',
        'Moradia': '#FFCE56',
        'Saúde': '#4BC0C0',
        'Educação': '#9966FF',
        'Lazer': '#FF9F40',
        'Assinaturas': '#E7E9ED',
        'Vestuário': '#C9CBCF',
        'Investimentos': '#4BC0C0',
        'Impostos': '#FF6384',
        'Seguros': '#36A2EB',
        'Doações': '#9966FF'
    }
    return colors.get(grupo, '#6c757d')

@app.template_filter('format_currency')
def format_currency(value):
    """Formata valor para moeda brasileira (R$ 1.234,56)"""
    if value is None:
        return "0,00"
    try:
        value = float(value)
        return "{:,.2f}".format(value).replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0,00"

@app.template_filter('get_estabelecimento_logo')
def get_estabelecimento_logo(estabelecimento):
    """Retorna caminho do logo se existir, senão None"""
    if not estabelecimento:
        return None
    
    # Normaliza o nome para busca
    estabelecimento_upper = estabelecimento.upper().strip()
    
    db = get_db_session()
    try:
        # Busca todos os logos ativos
        logos = db.query(EstabelecimentoLogo).filter(
            EstabelecimentoLogo.ativo == True
        ).all()
        
        # Procura por match em qualquer palavra de busca
        for logo in logos:
            # Separa palavras de busca por vírgula
            palavras_busca = [p.strip().upper() for p in logo.nome_busca.split(',')]
            
            # Verifica se alguma palavra está no estabelecimento
            for palavra in palavras_busca:
                if palavra in estabelecimento_upper:
                    return f'/static/logos/{logo.arquivo_logo}'
        
    finally:
        db.close()
    
    return None



def identificar_tipo_arquivo(filename):
    """Identifica tipo de arquivo pelo nome"""
    filename_lower = filename.lower()
    
    if 'fatura_itau' in filename_lower or 'fatura itau' in filename_lower:
        return 'fatura_itau'
    elif 'extrato conta corrente' in filename_lower or 'extrato_conta' in filename_lower:
        return 'extrato_itau'
    elif 'account_statement' in filename_lower or 'account statement' in filename_lower:
        return 'mercado_pago'
    
    return None


@app.route('/upload', methods=['GET', 'POST'])
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
            return redirect(url_for('upload'))
        
        # Remove transações futuras
        transacoes_atuais = [t for t in todas_transacoes if t.get('TransacaoFutura') == 'NÃO']
        futuras_removidas = len(todas_transacoes) - len(transacoes_atuais)
        
        # Deduplica contra journal_entries
        transacoes_unicas, duplicados_count = deduplicate_transactions(transacoes_atuais)
        
        # Classifica automaticamente
        transacoes_classificadas = classificar_transacoes(transacoes_unicas)
        
        # Armazena em sessão
        session['transacoes'] = transacoes_classificadas
        session['arquivos_processados'] = arquivos_processados
        session['duplicados_count'] = duplicados_count
        session['futuras_removidas'] = futuras_removidas
        
        flash(f'{len(transacoes_classificadas)} transações processadas com sucesso!', 'success')
        if duplicados_count > 0:
            flash(f'{duplicados_count} duplicados removidos', 'info')
        if futuras_removidas > 0:
            flash(f'{futuras_removidas} transações futuras removidas', 'info')
        
        return redirect(url_for('revisao_upload'))
    
    # GET - Mostra formulário de upload
    return render_template('upload.html')


@app.route('/revisao_upload')
def revisao_upload():
    """Dashboard com resumo das transações processadas (versão antiga baseada em sessão)"""
    
    transacoes = session.get('transacoes', [])
    
    if not transacoes:
        flash('Nenhuma transação em processamento. Faça upload de arquivos primeiro.', 'warning')
        return redirect(url_for('upload'))
    
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
    
    duplicados_count = session.get('duplicados_count', 0)
    
    return render_template(
        'revisao_upload.html',
        stats_por_origem=stats_por_origem,
        origens=list(por_origem.keys()),
        total_transacoes=len(transacoes),
        precisam_validacao=precisam_validacao,
        duplicados_count=duplicados_count
    )


@app.route('/duplicados')
def duplicados():
    """Visualizar duplicados temporários"""
    
    duplicados_list = get_duplicados_temp()
    
    return render_template('duplicados.html', duplicados=duplicados_list)


@app.route('/validar')
def validar():
    """Página simples para exibir transações não classificadas"""
    
    db_session = get_db_session()
    
    try:
        # Busca transações sem classificação
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        transacoes = db_session.query(JournalEntry).filter(
            or_(
                JournalEntry.GRUPO.is_(None),
                JournalEntry.GRUPO == '',
                JournalEntry.SUBGRUPO.is_(None),
                JournalEntry.SUBGRUPO == '',
                JournalEntry.TipoGasto.is_(None),
                JournalEntry.TipoGasto == ''
            )
        ).order_by(JournalEntry.Data.desc()).limit(per_page).offset((page-1) * per_page).all()
        
        # Total para paginação
        total = db_session.query(JournalEntry).filter(
            or_(
                JournalEntry.GRUPO.is_(None),
                JournalEntry.GRUPO == '',
                JournalEntry.SUBGRUPO.is_(None),
                JournalEntry.SUBGRUPO == '',
                JournalEntry.TipoGasto.is_(None),
                JournalEntry.TipoGasto == ''
            )
        ).count()
        
        total_pages = (total + per_page - 1) // per_page
        
        print(f"Transações não classificadas: {total}")
        
        return render_template('validar.html', 
                             transacoes=transacoes,
                             page=page,
                             total_pages=total_pages,
                             total=total)
    
    except Exception as e:
        app.logger.error(f"Erro na validação: {e}")
        flash(f"Erro ao carregar transações: {e}", 'error')
        return redirect(url_for('dashboard'))
    
    finally:
        db_session.close()


@app.route('/validar/lote', methods=['POST'])
def validar_lote():
    """Aplica classificação em lote para múltiplas transações"""
    try:
        data = request.get_json()
        indices = data.get('indices', [])
        grupo = data.get('grupo', '')
        subgrupo = data.get('subgrupo', '')
        tipo_gasto = data.get('tipo_gasto', '')
        
        transacoes = session.get('transacoes', [])
        
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
        
        session['transacoes'] = transacoes
        session.modified = True
        
        return jsonify({'success': True, 'message': f'{count} transações classificadas com sucesso'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/salvar', methods=['POST'])
def salvar():
    """Salva transações selecionadas no journal_entries"""
    
    transacoes = session.get('transacoes', [])
    
    if not transacoes:
        flash('Nenhuma transação para salvar', 'warning')
        return redirect(url_for('upload'))
    
    # Pega origens selecionadas
    origens_selecionadas = request.form.getlist('origens_selecionadas')
    
    if not origens_selecionadas:
        flash('Selecione pelo menos uma origem para salvar', 'warning')
        return redirect(url_for('dashboard'))
    
    # Filtra transações por origens selecionadas
    transacoes_salvar = [
        t for t in transacoes
        if t.get('origem') in origens_selecionadas
    ]
    
    if not transacoes_salvar:
        flash('Nenhuma transação das origens selecionadas', 'warning')
        return redirect(url_for('dashboard'))
    
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
        
        # Limpa sessão
        session.pop('transacoes', None)
        session.pop('arquivos_processados', None)
        session.pop('duplicados_count', None)
        
        # Regenera padrões
        regenerar_padroes()
        
        flash(f'{salvos} transações salvas com sucesso!', 'success')
        
    except Exception as e:
        db_session.rollback()
        flash(f'Erro ao salvar: {str(e)}', 'danger')
    finally:
        db_session.close()
    
    return redirect(url_for('upload'))


@app.route('/api/adicionar_marcacao', methods=['POST'])
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


@app.route('/api/marcacoes', methods=['GET'])
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


@app.route('/validarV2')
def validar_v2():
    """Nova página de validação baseada no teste que funciona"""
    
    print(f"\n=== VALIDAR V2 ===")
    
    # Busca transações sem grupo (precisam validação)
    db_session = get_db_session()
    
    # Filtros
    filtro_classificacao = request.args.get('classificacao', 'nao_classificadas')
    
    if filtro_classificacao == 'nao_classificadas':
        transacoes_validar = db_session.query(JournalEntry).filter(
            JournalEntry.GRUPO.is_(None)
        ).order_by(JournalEntry.Data.desc()).all()
    else:
        # Outras opções de filtro se necessário
        transacoes_validar = db_session.query(JournalEntry).filter(
            JournalEntry.GRUPO.is_(None)
        ).order_by(JournalEntry.Data.desc()).all()
    
    # Paginação
    page = int(request.args.get('page', 1))
    per_page = 10
    total = len(transacoes_validar)
    total_pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    transacoes_pagina = transacoes_validar[start:end]
    
    # Carrega marcações
    marcacoes = db_session.query(BaseMarcacao).all()
    db_session.close()
    
    print(f"Transações para validar: {total}")
    print(f"Marcações carregadas: {len(marcacoes)}")
    
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
    
    print(f"Grupos organizados: {len(grupos)}")
    print(f"==================")
    
    return render_template(
        'validarV2.html',
        transacoes=transacoes_pagina,
        page=page,
        total_pages=total_pages,
        total=total,
        grupos=grupos,
        grupos_dict=grupos_dict,
        tipo_gasto_dict=tipo_gasto_dict
    )


@app.route('/teste_dropdown')
def teste_dropdown():
    """Página simples para testar dropdowns"""
    
    print(f"\n=== TESTE DROPDOWN ===")
    
    # Carrega marcações
    db_session = get_db_session()
    marcacoes = db_session.query(BaseMarcacao).all()
    db_session.close()
    
    print(f"Marcações carregadas: {len(marcacoes)}")
    
    # Organiza dados
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
    
    print(f"Grupos encontrados: {grupos}")
    print(f"Alimentação tem subgrupos: {'Alimentação' in grupos_dict}")
    if 'Alimentação' in grupos_dict:
        print(f"Subgrupos da Alimentação: {grupos_dict['Alimentação']}")
    print(f"=====================")
    
    return render_template(
        'teste_dropdown.html',
        grupos=grupos,
        grupos_dict=grupos_dict,
        tipo_gasto_dict=tipo_gasto_dict
    )


@app.route('/admin/marcacoes')
def admin_marcacoes():
    """Administração de marcações (grupos/subgrupos)"""
    
    db_session = get_db_session()
    
    # Filtros
    grupo_filtro = request.args.get('grupo', '')
    tipo_gasto_filtro = request.args.get('tipo_gasto', '')
    busca = request.args.get('busca', '')
    
    # Query base
    query = db_session.query(BaseMarcacao)
    
    if grupo_filtro:
        query = query.filter(BaseMarcacao.GRUPO == grupo_filtro)
    
    if tipo_gasto_filtro:
        query = query.filter(BaseMarcacao.TipoGasto == tipo_gasto_filtro)
    
    if busca:
        query = query.filter(
            or_(
                BaseMarcacao.GRUPO.like(f'%{busca}%'),
                BaseMarcacao.SUBGRUPO.like(f'%{busca}%')
            )
        )
    
    # Paginação
    page = int(request.args.get('page', 1))
    per_page = 50
    
    marcacoes_paginadas = query.order_by(BaseMarcacao.GRUPO, BaseMarcacao.SUBGRUPO).limit(per_page).offset((page-1)*per_page).all()
    total = query.count()
    total_pages = (total + per_page - 1) // per_page
    
    # Obter grupos únicos para filtro
    grupos_unicos = db_session.query(BaseMarcacao.GRUPO).distinct().order_by(BaseMarcacao.GRUPO).all()
    grupos_lista = [g[0] for g in grupos_unicos]
    
    # Obter tipos de gasto únicos para filtro
    tipos_gasto_unicos = db_session.query(BaseMarcacao.TipoGasto).distinct().order_by(BaseMarcacao.TipoGasto).all()
    tipos_gasto_lista = [t[0] for t in tipos_gasto_unicos]
    
    db_session.close()
    
    return render_template(
        'admin_marcacoes.html',
        marcacoes=marcacoes_paginadas,
        page=page,
        total_pages=total_pages,
        total=total,
        grupos_lista=grupos_lista,
        tipos_gasto_lista=tipos_gasto_lista,
        grupo_filtro=grupo_filtro,
        tipo_gasto_filtro=tipo_gasto_filtro,
        busca=busca
    )


@app.route('/admin/padroes')
def admin_padroes():
    """Administração de padrões"""
    
    db_session = get_db_session()
    
    # Filtros
    confianca_filtro = request.args.get('confianca', '')
    grupo_filtro = request.args.get('grupo', '')
    busca = request.args.get('busca', '')
    
    # Query base
    query = db_session.query(BasePadrao)
    
    if confianca_filtro:
        query = query.filter(BasePadrao.confianca == confianca_filtro)
    
    if grupo_filtro:
        query = query.filter(BasePadrao.grupo_sugerido == grupo_filtro)
    
    if busca:
        query = query.filter(BasePadrao.padrao_estabelecimento.like(f'%{busca}%'))
    
    # Paginação
    page = int(request.args.get('page', 1))
    per_page = 50
    
    padroes_paginados = query.order_by(BasePadrao.contagem.desc()).limit(per_page).offset((page-1)*per_page).all()
    total = query.count()
    total_pages = (total + per_page - 1) // per_page
    
    db_session.close()
    
    return render_template(
        'admin_padroes.html',
        padroes=padroes_paginados,
        page=page,
        total_pages=total_pages,
        total=total
    )


@app.route('/admin/grupos')
def admin_grupos():
    """Administração de grupos (ícones e cores)"""
    db = get_db_session()
    grupos = db.query(GrupoConfig).order_by(GrupoConfig.ordem, GrupoConfig.nome).all()
    
    # Lista de ícones Font Awesome disponíveis
    icones_disponiveis = [
        'fa-utensils', 'fa-car', 'fa-home', 'fa-heartbeat', 'fa-graduation-cap',
        'fa-gamepad', 'fa-file-invoice', 'fa-tshirt', 'fa-chart-line', 'fa-landmark',
        'fa-shield-alt', 'fa-hand-holding-heart', 'fa-shopping-cart', 'fa-plane',
        'fa-coffee', 'fa-laptop', 'fa-mobile-alt', 'fa-tv', 'fa-book', 'fa-dumbbell',
        'fa-paw', 'fa-gift', 'fa-music', 'fa-camera', 'fa-bicycle', 'fa-bus'
    ]
    
    db.close()
    return render_template('admin_grupos.html', grupos=grupos, icones=icones_disponiveis)


@app.route('/admin/grupos/salvar', methods=['POST'])
def admin_grupos_salvar():
    """Salva/atualiza grupo"""
    try:
        data = request.form
        grupo_id = data.get('grupo_id')
        
        db = get_db_session()
        
        if grupo_id:
            # Atualizar existente
            grupo = db.query(GrupoConfig).filter_by(id=int(grupo_id)).first()
            if not grupo:
                return jsonify({'success': False, 'error': 'Grupo não encontrado'}), 404
            
            grupo.nome = data.get('nome')
            grupo.icone = data.get('icone')
            grupo.cor = data.get('cor')
            grupo.descricao = data.get('descricao', '')
            grupo.ordem = int(data.get('ordem', 0))
            grupo.ativo = data.get('ativo') == 'true'
        else:
            # Criar novo
            grupo = GrupoConfig(
                nome=data.get('nome'),
                icone=data.get('icone'),
                cor=data.get('cor'),
                descricao=data.get('descricao', ''),
                ordem=int(data.get('ordem', 0)),
                ativo=True
            )
            db.add(grupo)
        
        db.commit()
        db.close()
        
        flash('Grupo salvo com sucesso!', 'success')
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/admin/grupos/deletar/<int:grupo_id>', methods=['POST'])
def admin_grupos_deletar(grupo_id):
    """Deleta grupo"""
    try:
        db = get_db_session()
        grupo = db.query(GrupoConfig).filter_by(id=grupo_id).first()
        
        if not grupo:
            return jsonify({'success': False, 'error': 'Grupo não encontrado'}), 404
        
        db.delete(grupo)
        db.commit()
        db.close()
        
        flash('Grupo deletado com sucesso!', 'success')
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/admin/logos')
def admin_logos():
    """Administração de logos de estabelecimentos"""
    db = get_db_session()
    logos = db.query(EstabelecimentoLogo).order_by(EstabelecimentoLogo.nome_exibicao).all()
    db.close()
    return render_template('admin_logos.html', logos=logos)


@app.route('/admin/logos/upload', methods=['POST'])
def admin_logos_upload():
    """Upload de NOVO logo de estabelecimento"""
    try:
        nome_busca = request.form.get('nome_busca', '').strip()
        nome_exibicao = request.form.get('nome_exibicao', '').strip()
        
        if not nome_busca:
            return jsonify({'success': False, 'error': 'Nome de busca é obrigatório'}), 400
        
        if 'logo_file' not in request.files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['logo_file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado'}), 400
        
        # Validar tamanho
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        if file_length > app.config['MAX_LOGO_SIZE']:
            return jsonify({'success': False, 'error': 'Arquivo muito grande (máx 2MB)'}), 400
        file.seek(0)
        
        # Validar extensão
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'success': False, 'error': 'Formato não suportado'}), 400
        
        # Gerar nome seguro do arquivo
        nome_arquivo = secure_filename(f"{nome_busca.lower().replace(' ', '_').replace(',', '')}{file_ext}")
        caminho_completo = os.path.join(app.config['LOGOS_FOLDER'], nome_arquivo)
        
        # Salvar arquivo
        file.save(caminho_completo)
        
        # Criar novo logo
        db = get_db_session()
        logo = EstabelecimentoLogo(
            nome_busca=nome_busca,
            nome_exibicao=nome_exibicao or nome_busca,
            arquivo_logo=nome_arquivo,
            ativo=True
        )
        db.add(logo)
        db.commit()
        db.close()
        
        flash('Logo criado com sucesso!', 'success')
        return jsonify({'success': True, 'arquivo': nome_arquivo})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/admin/logos/update/<int:logo_id>', methods=['POST'])
def admin_logos_update(logo_id):
    """Atualizar logo existente"""
    try:
        nome_busca = request.form.get('nome_busca', '').strip()
        nome_exibicao = request.form.get('nome_exibicao', '').strip()
        
        if not nome_busca:
            return jsonify({'success': False, 'error': 'Nome de busca é obrigatório'}), 400
        
        db = get_db_session()
        logo = db.query(EstabelecimentoLogo).filter_by(id=logo_id).first()
        
        if not logo:
            return jsonify({'success': False, 'error': 'Logo não encontrado'}), 404
        
        # Atualizar nomes
        logo.nome_busca = nome_busca
        logo.nome_exibicao = nome_exibicao or nome_busca
        logo.updated_at = datetime.utcnow()
        
        # Se enviou novo arquivo, processar
        if 'logo_file' in request.files and request.files['logo_file'].filename:
            file = request.files['logo_file']
            
            # Validar tamanho
            file.seek(0, os.SEEK_END)
            file_length = file.tell()
            if file_length > app.config['MAX_LOGO_SIZE']:
                return jsonify({'success': False, 'error': 'Arquivo muito grande (máx 2MB)'}), 400
            file.seek(0)
            
            # Validar extensão
            allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'}
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                return jsonify({'success': False, 'error': 'Formato não suportado'}), 400
            
            # Gerar nome seguro do arquivo
            nome_arquivo = secure_filename(f"{nome_busca.lower().replace(' ', '_').replace(',', '')}{file_ext}")
            caminho_completo = os.path.join(app.config['LOGOS_FOLDER'], nome_arquivo)
            
            # Deletar arquivo antigo se diferente
            if logo.arquivo_logo != nome_arquivo:
                caminho_antigo = os.path.join(app.config['LOGOS_FOLDER'], logo.arquivo_logo)
                if os.path.exists(caminho_antigo):
                    os.remove(caminho_antigo)
            
            # Salvar novo arquivo
            file.save(caminho_completo)
            logo.arquivo_logo = nome_arquivo
        
        db.commit()
        db.close()
        
        flash('Logo atualizado com sucesso!', 'success')
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/admin/logos/deletar/<int:logo_id>', methods=['POST'])
def admin_logos_deletar(logo_id):
    """Deleta logo de estabelecimento"""
    try:
        db = get_db_session()
        logo = db.query(EstabelecimentoLogo).filter_by(id=logo_id).first()
        
        if not logo:
            return jsonify({'success': False, 'error': 'Logo não encontrado'}), 404
        
        # Deletar arquivo
        caminho_arquivo = os.path.join(app.config['LOGOS_FOLDER'], logo.arquivo_logo)
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)
        
        db.delete(logo)
        db.commit()
        db.close()
        
        flash('Logo deletado com sucesso!', 'success')
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/transacoes/toggle_dashboard/<string:id_transacao>', methods=['POST'])
def toggle_dashboard_status(id_transacao):
    """Alterna o status de IgnorarDashboard de uma transação"""
    try:
        print(f"🔄 Toggle Dashboard solicitado para ID: {id_transacao}")
        data = request.get_json()
        ignorar = data.get('ignorar', True) # Se True, IgnorarDashboard = True (Desligado/Cinza)
        
        print(f"📝 Novo status IgnorarDashboard: {ignorar}")
        
        db = get_db_session()
        transacao = db.query(JournalEntry).filter_by(IdTransacao=id_transacao).first()
        
        if not transacao:
            print(f"❌ Transação {id_transacao} não encontrada")
            return jsonify({'success': False, 'error': 'Transação não encontrada'}), 404
            
        transacao.IgnorarDashboard = bool(ignorar)
        db.commit()
        print(f"✅ Transação {id_transacao} atualizada com sucesso")
        db.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ Erro no toggle: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/test_chart')
def test_chart():
    """Página de teste para gráficos"""
    return render_template('test_chart.html')

@app.route('/dashboard2')
def dashboard2():
    """Dashboard simplificado para teste de gráficos"""
    try:
        # Dados simplificados para teste
        grupos_labels = ['Alimentação', 'Transporte', 'Saúde', 'Educação']
        grupos_valores = [1500.00, 800.00, 400.00, 300.00]
        grupos_cores = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
        
        evolucao_meses = ['Jul/25', 'Ago/25', 'Set/25', 'Out/25', 'Nov/25', 'Dez/25']
        evolucao_receitas = [5000, 5200, 4800, 5500, 5100, 5300]
        evolucao_despesas = [3200, 3500, 2800, 4100, 3600, 3900]
        
        print("📊 Dashboard2 - Dados preparados:")
        print(f"   Grupos: {grupos_labels}")
        print(f"   Valores: {grupos_valores}")
        print(f"   Meses: {evolucao_meses}")
        
        return render_template('dashboard2.html', 
                             grupos_labels=grupos_labels,
                             grupos_valores=grupos_valores,
                             grupos_cores=grupos_cores,
                             evolucao_meses=evolucao_meses,
                             evolucao_receitas=evolucao_receitas,
                             evolucao_despesas=evolucao_despesas)
    except Exception as e:
        print(f"❌ Erro no dashboard2: {e}")
        return f"Erro: {e}", 500

@app.route('/test_basic_chart')
def test_basic_chart():
    """Teste super básico de Chart.js"""
    return render_template('test_basic_chart.html')

@app.route('/api/transacao/<transacao_id>')
def api_transacao_detalhes(transacao_id):
    """API para buscar detalhes de uma transação"""
    try:
        transacao = db.query(JournalEntry).filter(
            JournalEntry.ID == transacao_id
        ).first()
        
        if not transacao:
            return jsonify({'error': 'Transação não encontrada'}), 404
        
        detalhes = {
            'ID': transacao.ID,
            'Data': transacao.Data.strftime('%d/%m/%Y') if transacao.Data else 'N/A',
            'Estabelecimento': transacao.Estabelecimento,
            'Valor': float(transacao.Valor),
            'GRUPO': transacao.GRUPO,
            'SubGrupo': transacao.SUBGRUPO,
            'Descricao': transacao.Descricao,
            'PixChaveDestino': transacao.PixChaveDestino,
            'CategoriaTransacao': transacao.CategoriaTransacao,
            'StatusTransacao': transacao.StatusTransacao,
            'IgnorarDashboard': transacao.IgnorarDashboard
        }
        
        return jsonify(detalhes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard3')
def dashboard3():
    """Dashboard 3 - Teste sem base.html"""
    try:
        # Dados simplificados para teste
        grupos_labels = ['Alimentação', 'Transporte', 'Saúde', 'Educação']
        grupos_valores = [1500.00, 800.00, 400.00, 300.00]
        grupos_cores = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
        
        evolucao_meses = ['Jul/25', 'Ago/25', 'Set/25', 'Out/25', 'Nov/25', 'Dez/25']
        evolucao_receitas = [5000, 5200, 4800, 5500, 5100, 5300]
        evolucao_despesas = [3200, 3500, 2800, 4100, 3600, 3900]
        
        print("🔬 Dashboard3 - Teste sem base.html:")
        print(f"   Grupos: {grupos_labels}")
        print(f"   Valores: {grupos_valores}")
        
        return render_template('dashboard3.html', 
                             grupos_labels=grupos_labels,
                             grupos_valores=grupos_valores,
                             grupos_cores=grupos_cores,
                             evolucao_meses=evolucao_meses,
                             evolucao_receitas=evolucao_receitas,
                             evolucao_despesas=evolucao_despesas)
    except Exception as e:
        print(f"❌ Erro no dashboard3: {e}")
        return f"Erro: {e}", 500


@app.route('/transacoes')
def transacoes():
    """Lista todas as transações de um mês específico"""
    from datetime import datetime
    
    mes_param = request.args.get('mes')
    if not mes_param:
        return redirect(url_for('dashboard'))
        
    mes_db = mes_param.replace('-', '')
    
    try:
        dt_obj = datetime.strptime(mes_db, "%Y%m")
        mes_exibicao = dt_obj.strftime("%B %Y").capitalize()
    except:
        mes_exibicao = mes_param
    
    db = get_db_session()
    try:
        transacoes = db.query(JournalEntry).filter(
            JournalEntry.DT_Fatura == mes_db
        ).order_by(JournalEntry.Data.desc()).all()
        
        return render_template('transacoes.html',
                             transacoes=transacoes,
                             mes_atual=mes_param,
                             mes_exibicao=mes_exibicao,
                             total_transacoes=len(transacoes))
    finally:
        db.close()


@app.route('/')
def dashboard():
    """Dashboard analítico com visão geral das finanças - PÁGINA INICIAL"""
    from sqlalchemy import func, extract, desc
    from datetime import datetime, timedelta
    from dateutil.relativedelta import relativedelta
    import calendar
    
    db = get_db_session()
    
    try:
        # 1. Determinar meses disponíveis (para o filtro)
        meses_query = db.query(JournalEntry.DT_Fatura).distinct().order_by(desc(JournalEntry.DT_Fatura)).all()
        meses_disponiveis = []
        for m in meses_query:
            if m[0] and len(m[0]) == 6:
                try:
                    dt_obj = datetime.strptime(m[0], "%Y%m")
                    meses_disponiveis.append({
                        'value': dt_obj.strftime("%Y-%m"), # Formato para o value do select (YYYY-MM)
                        'label': dt_obj.strftime("%B %Y").capitalize() # Formato para exibição
                    })
                except ValueError:
                    continue
        
        # 2. Determinar mês selecionado
        mes_param = request.args.get('mes') # Vem como YYYY-MM do input type="month"
        
        if mes_param:
            # Se veio do filtro, converte para formato do banco (YYYYMM)
            mes_atual_db = mes_param.replace('-', '')
            mes_atual_visual = mes_param
        else:
            # Se não veio, pega o mais recente do banco ou atual
            if meses_disponiveis:
                mes_atual_visual = meses_disponiveis[0]['value']
                mes_atual_db = mes_atual_visual.replace('-', '')
            else:
                hoje = datetime.now()
                mes_atual_visual = hoje.strftime('%Y-%m')
                mes_atual_db = hoje.strftime('%Y%m')
            
        # 3. Determinar mês anterior (para comparação)
        try:
            dt_atual = datetime.strptime(mes_atual_db, '%Y%m')
            dt_anterior = dt_atual - relativedelta(months=1)
            mes_anterior_db = dt_anterior.strftime('%Y%m')
        except:
            mes_anterior_db = None

        # === MÉTRICAS PRINCIPAIS ===
        
        # Total despesas mês atual
        total_despesas = db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.DT_Fatura == mes_atual_db,
            JournalEntry.Valor < 0,
            JournalEntry.IgnorarDashboard.isnot(True)
        ).scalar() or 0
        
        # Total despesas mês anterior
        total_despesas_anterior = db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.DT_Fatura == mes_anterior_db,
            JournalEntry.Valor < 0,
            JournalEntry.IgnorarDashboard.isnot(True)
        ).scalar() or 0
        
        # Total receitas mês atual
        total_receitas = db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.DT_Fatura == mes_atual_db,
            JournalEntry.Valor > 0,
            JournalEntry.IgnorarDashboard.isnot(True)
        ).scalar() or 0
        
        # Total receitas mês anterior
        total_receitas_anterior = db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.DT_Fatura == mes_anterior_db,
            JournalEntry.Valor > 0,
            JournalEntry.IgnorarDashboard.isnot(True)
        ).scalar() or 0
        
        # Saldo atual
        saldo = total_receitas + total_despesas
        saldo_anterior = total_receitas_anterior + total_despesas_anterior
        
        # Total de transações
        total_transacoes = db.query(func.count(JournalEntry.id)).filter(
            JournalEntry.DT_Fatura == mes_atual_db,
            JournalEntry.IgnorarDashboard.isnot(True)
        ).scalar() or 0
        
        # Transações classificadas
        transacoes_classificadas = db.query(func.count(JournalEntry.id)).filter(
            JournalEntry.DT_Fatura == mes_atual_db,
            JournalEntry.GRUPO.isnot(None),
            JournalEntry.IgnorarDashboard.isnot(True)
        ).scalar() or 0
        
        perc_classificadas = (transacoes_classificadas / total_transacoes * 100) if total_transacoes > 0 else 0
        
        # Variações percentuais
        variacao_despesas = ((total_despesas / total_despesas_anterior * 100) - 100) if total_despesas_anterior != 0 else 0
        variacao_receitas = ((total_receitas / total_receitas_anterior * 100) - 100) if total_receitas_anterior != 0 else 0
        variacao_saldo = ((saldo / saldo_anterior * 100) - 100) if saldo_anterior != 0 else 0
        
        # Média diária
        try:
            ano = int(mes_atual_db[:4])
            mes = int(mes_atual_db[4:])
            _, dias_no_mes = calendar.monthrange(ano, mes)
            
            hoje = datetime.now()
            if hoje.year == ano and hoje.month == mes:
                dias_considerados = hoje.day
            else:
                dias_considerados = dias_no_mes
                
            media_diaria = total_despesas / dias_considerados if dias_considerados > 0 else 0
        except:
            media_diaria = 0
        
        # Total de estabelecimentos únicos
        total_estabelecimentos = db.query(func.count(func.distinct(JournalEntry.Estabelecimento))).filter(
            JournalEntry.DT_Fatura == mes_atual_db,
            JournalEntry.IgnorarDashboard.isnot(True)
        ).scalar() or 0
        
        # === DISTRIBUIÇÃO POR GRUPO ===
        grupos_query = db.query(
            JournalEntry.GRUPO,
            func.sum(JournalEntry.Valor).label('total')
        ).filter(
            JournalEntry.DT_Fatura == mes_atual_db,
            JournalEntry.Valor < 0,
            JournalEntry.GRUPO.isnot(None),
            JournalEntry.IgnorarDashboard.isnot(True)
        ).group_by(JournalEntry.GRUPO).order_by(func.sum(JournalEntry.Valor).asc()).limit(8).all()
        
        grupos_labels = [g[0] for g in grupos_query]
        grupos_valores = [abs(g[1]) for g in grupos_query]
        grupos_cores = [get_group_color(g[0]) for g in grupos_query]
        
        # Maior aumento e maior economia
        maior_aumento = None
        maior_economia = None
        
        for grupo in grupos_labels:
            total_atual = db.query(func.sum(JournalEntry.Valor)).filter(
                JournalEntry.DT_Fatura == mes_atual_db,
                JournalEntry.GRUPO == grupo,
                JournalEntry.Valor < 0,
                JournalEntry.IgnorarDashboard.isnot(True)
            ).scalar() or 0
            
            total_anterior = db.query(func.sum(JournalEntry.Valor)).filter(
                JournalEntry.DT_Fatura == mes_anterior_db,
                JournalEntry.GRUPO == grupo,
                JournalEntry.Valor < 0,
                JournalEntry.IgnorarDashboard.isnot(True)
            ).scalar() or 0
            
            if total_anterior != 0:
                variacao = ((total_atual / total_anterior * 100) - 100)
                if variacao > 20 and (not maior_aumento or variacao > maior_aumento['variacao']):
                    maior_aumento = {'grupo': grupo, 'variacao': variacao}
                if variacao < -20 and (not maior_economia or variacao < maior_economia['variacao']):
                    maior_economia = {'grupo': grupo, 'variacao': variacao}
        
        # === TOP 10 SUBGRUPOS ===
        top_subgrupos_query = db.query(
            JournalEntry.SUBGRUPO,
            JournalEntry.GRUPO,
            func.sum(JournalEntry.Valor).label('total')
        ).filter(
            JournalEntry.DT_Fatura == mes_atual_db,
            JournalEntry.Valor < 0,
            JournalEntry.IgnorarDashboard.isnot(True),
            JournalEntry.SUBGRUPO.isnot(None)
        ).group_by(
            JournalEntry.SUBGRUPO,
            JournalEntry.GRUPO
        ).order_by(
            func.sum(JournalEntry.Valor).asc()
        ).limit(10).all()
        
        max_valor = abs(top_subgrupos_query[0][2]) if top_subgrupos_query else 1
        top_estabelecimentos = [
            {
                'estabelecimento': item[0],  # mantendo nome da variável para compatibilidade
                'grupo': item[1],
                'total': item[2],
                'percentual': (abs(item[2]) / max_valor * 100)
            }
            for item in top_subgrupos_query
        ]
        
        # === EVOLUÇÃO MENSAL (últimos 6 meses) ===
        evolucao_meses = []
        evolucao_despesas = []
        evolucao_receitas = []
        
        for i in range(5, -1, -1):
            dt_ref = dt_atual - relativedelta(months=i)
            mes_ref = dt_ref.strftime('%Y%m')
            
            evolucao_meses.append(dt_ref.strftime('%b/%y'))
            
            despesas_mes = abs(db.query(func.sum(JournalEntry.Valor)).filter(
                JournalEntry.DT_Fatura == mes_ref,
                JournalEntry.Valor < 0,
                JournalEntry.IgnorarDashboard.isnot(True)
            ).scalar() or 0)
            
            receitas_mes = db.query(func.sum(JournalEntry.Valor)).filter(
                JournalEntry.DT_Fatura == mes_ref,
                JournalEntry.Valor > 0,
                JournalEntry.IgnorarDashboard.isnot(True)
            ).scalar() or 0
            
            evolucao_despesas.append(despesas_mes)
            evolucao_receitas.append(receitas_mes)
        
        # === ÚLTIMAS 10 TRANSAÇÕES ===
        ultimas_transacoes = db.query(JournalEntry).filter(
            JournalEntry.DT_Fatura == mes_atual_db,
            JournalEntry.IgnorarDashboard.isnot(True)
        ).order_by(
            JournalEntry.Data.desc()
        ).limit(10).all()
        
        stats = {
            'total_despesas': total_despesas,
            'total_receitas': total_receitas,
            'saldo': saldo,
            'total_transacoes': total_transacoes,
            'perc_classificadas': round(perc_classificadas, 1),
            'variacao_despesas': variacao_despesas,
            'variacao_receitas': variacao_receitas,
            'variacao_saldo': variacao_saldo,
            'media_diaria': media_diaria,
            'total_estabelecimentos': total_estabelecimentos,
            'maior_aumento': maior_aumento,
            'maior_economia': maior_economia
        }
        
        return render_template('dashboard.html',
                             stats=stats,
                             grupos_labels=grupos_labels,
                             grupos_valores=grupos_valores,
                             grupos_cores=grupos_cores,
                             top_estabelecimentos=top_estabelecimentos,
                             evolucao_meses=evolucao_meses,
                             evolucao_despesas=evolucao_despesas,
                             evolucao_receitas=evolucao_receitas,
                             ultimas_transacoes=ultimas_transacoes,
                             meses_disponiveis=meses_disponiveis,
                             mes_atual=mes_atual_visual)
    
    finally:
        db.close()


if __name__ == '__main__':
    print("🚀 Iniciando aplicação...")
    print("📍 Acesse: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)
