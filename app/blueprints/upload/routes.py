"""
Upload Routes - Processamento temporário de novos arquivos

Versão: 2.1.0
Data: 27/12/2025
Status: stable

🔒 ARQUIVO CRÍTICO - Requer versionamento obrigatório

Gerencia o fluxo de upload, processamento e validação de arquivos financeiros.
Inclui auto-sync de parcelas e dedu plicação automática.

Histórico:
- 2.0.0: Implementação de auto-sync de BaseParcelas (linha ~580-610)
- 2.0.0: Correção IdParcela não sendo salvo (linha ~540)
- 2.1.0: Sistema de versionamento implementado
"""
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
import os
import pandas as pd
from datetime import datetime

from app.blueprints.upload import upload_bp
from app.models import JournalEntry, BaseMarcacao, BaseParcelas, get_db_session
from app.utils.processors.preprocessors import is_extrato_itau_xls, preprocessar_extrato_itau_xls
from app.blueprints.upload.processors import (
    processar_fatura_cartao, processar_extrato_conta
)
from app.blueprints.upload.utils import detectar_tipo_arquivo, detectar_colunas, mapear_colunas
from app.blueprints.upload.classifiers import classificar_transacoes, regenerar_padroes
from app.utils import deduplicate_transactions, get_duplicados_temp, clear_duplicados_temp
from app.utils.normalizer import normalizar_estabelecimento, detectar_parcela
from sqlalchemy import or_


# Constantes
UPLOAD_FOLDER = 'uploads_temp'


def ler_arquivo_para_dataframe(filepath, filename):
    """Lê arquivo CSV ou XLSX e retorna DataFrame"""
    extensao = filename.lower().split('.')[-1]
    
    try:
        if extensao == 'csv':
            # Tenta diferentes encodings
            try:
                df = pd.read_csv(filepath, encoding='utf-8')
            except:
                try:
                    df = pd.read_csv(filepath, encoding='latin-1')
                except:
                    df = pd.read_csv(filepath, encoding='iso-8859-1')
        
        elif extensao in ['xlsx', 'xls']:
            if extensao == 'xls':
                # Lê arquivo XLS bruto (sem assumir header)
                df_raw = pd.read_excel(filepath, engine='xlrd', header=None)
                
                # Verifica se é extrato Itaú XLS especial
                if is_extrato_itau_xls(df_raw, filename):
                    df, validacao = preprocessar_extrato_itau_xls(df_raw)
                    
                    # Armazenar informações de validação na sessão
                    session['validacao_extrato'] = {
                        'valido': validacao['valido'],
                        'mensagem': validacao['mensagem'],
                        'saldo_anterior': validacao.get('saldo_anterior'),
                        'saldo_final': validacao.get('saldo_final_arquivo'),
                        'soma_transacoes': validacao.get('soma_transacoes'),
                        'diferenca': validacao.get('diferenca'),
                        'periodo': validacao.get('periodo')
                    }
                else:
                    # Arquivo XLS normal - relê com header padrão
                    df = pd.read_excel(filepath, engine='xlrd')
            else:
                df = pd.read_excel(filepath, engine='openpyxl')
        else:
            return None
        
        return df
    except Exception as e:
        print(f"❌ Erro ao ler arquivo {filename}: {e}")
        return None


@upload_bp.route('/', methods=['GET', 'POST'])
def upload():
    """Página de Upload de Arquivos com Detecção Inteligente"""
    
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
        arquivos_info = []
        
        for file in files:
            if file and file.filename:
                # Salva temporariamente
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                # Lê arquivo
                df = ler_arquivo_para_dataframe(filepath, filename)
                
                if df is None:
                    flash(f'Erro ao ler {filename}. Formato não suportado.', 'danger')
                    os.remove(filepath)
                    continue
                
                # Verificar se foi preprocessado (extrato Itaú XLS)
                eh_extrato_itau = session.get('validacao_extrato') is not None
                
                # Detecta colunas
                mapeamento = detectar_colunas(df)
                
                if not all(mapeamento.values()):
                    # Não conseguiu detectar todas as colunas
                    # Salva info para permitir mapeamento manual
                    arquivos_info.append({
                        'nome': filename,
                        'filepath': filepath,
                        'colunas': list(df.columns),
                        'mapeamento_detectado': mapeamento,
                        'precisa_mapeamento': True,
                        'tipo_detectado': 'extrato' if eh_extrato_itau else None
                    })
                    continue
                
                # Detecta tipo (fatura vs extrato) - se não for Itaú XLS
                if eh_extrato_itau:
                    deteccao_tipo = {
                        'tipo': 'extrato',
                        'confianca': 1.0,
                        'indicadores_encontrados': ['Extrato Itaú XLS (preprocessado)']
                    }
                else:
                    deteccao_tipo = detectar_tipo_arquivo(df)
                
                # Salva info do arquivo para confirmação
                arquivos_info.append({
                    'nome': filename,
                    'filepath': filepath,
                    'colunas': list(df.columns),
                    'mapeamento': mapeamento,
                    'tipo_detectado': deteccao_tipo['tipo'],
                    'confianca': deteccao_tipo['confianca'],
                    'indicadores': deteccao_tipo['indicadores_encontrados'],
                    'precisa_mapeamento': False
                })
        
        if not arquivos_info:
            flash('Nenhum arquivo válido foi processado', 'warning')
            return redirect(url_for('upload.upload'))
        
        # Armazena info dos arquivos na sessão para confirmação
        session['upload.arquivos_pendentes'] = arquivos_info
        
        return redirect(url_for('upload.confirmar_upload'))
    
    # GET - Mostra formulário de upload
    return render_template('upload.html')


@upload_bp.route('/confirmar')
def confirmar_upload():
    """Tela de confirmação com detecção automática de tipo e colunas"""
    
    arquivos_info = session.get('upload.arquivos_pendentes', [])
    
    if not arquivos_info:
        flash('Nenhum arquivo pendente de confirmação', 'warning')
        return redirect(url_for('upload.upload'))
    
    return render_template('confirmar_upload.html', arquivos=arquivos_info)


@upload_bp.route('/processar_confirmados', methods=['POST'])
def processar_confirmados():
    """Processa arquivos após confirmação do usuário"""
    
    arquivos_info = session.get('upload.arquivos_pendentes', [])
    
    if not arquivos_info:
        flash('Nenhum arquivo para processar', 'warning')
        return redirect(url_for('upload.upload'))
    
    todas_transacoes = []
    arquivos_processados = []
    
    for idx, arquivo_info in enumerate(arquivos_info):
        filename = arquivo_info['nome']
        filepath = arquivo_info['filepath']
        
        # Pega confirmação do usuário (pode ter sido mudado)
        tipo_final = request.form.get(f'tipo_{idx}', arquivo_info.get('tipo_detectado'))
        
        # Pega mapeamento (pode ter sido ajustado ou vem do formulário)
        col_data_form = request.form.get(f'col_data_{idx}')
        col_estab_form = request.form.get(f'col_estabelecimento_{idx}')
        col_valor_form = request.form.get(f'col_valor_{idx}')
        
        if col_data_form and col_estab_form and col_valor_form:
            # Usa valores do formulário (sempre enviados agora via hidden inputs)
            mapeamento = {
                'data': col_data_form,
                'estabelecimento': col_estab_form,
                'valor': col_valor_form
            }
        else:
            # Fallback para mapeamento da sessão
            mapeamento = arquivo_info.get('mapeamento', {})
        
        # Lê arquivo novamente
        df = ler_arquivo_para_dataframe(filepath, filename)
        
        if df is None:
            flash(f'Erro ao processar {filename}', 'danger')
            os.remove(filepath)
            continue
        
        # Processa com processador apropriado
        try:
            if tipo_final == 'fatura':
                transacoes = processar_fatura_cartao(df, mapeamento, origem=f'Fatura - {filename}', file_name=filename)
            else:  # extrato
                transacoes = processar_extrato_conta(df, mapeamento, origem=f'Extrato - {filename}', file_name=filename)
            
            todas_transacoes.extend(transacoes)
            arquivos_processados.append({
                'nome': filename,
                'tipo': tipo_final,
                'transacoes': len(transacoes)
            })
            
        except Exception as e:
            flash(f'Erro ao processar {filename}: {str(e)}', 'danger')
        
        # Remove arquivo temporário
        os.remove(filepath)
    
    # Limpa sessão de arquivos pendentes
    session.pop('upload.arquivos_pendentes', None)
    
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
            # Para extratos: despesas e receitas separadas + breakdown por TipoGasto
            despesas = sum(t.get('Valor', 0) for t in trans_list if t.get('Valor', 0) < 0)
            receitas = sum(t.get('Valor', 0) for t in trans_list if t.get('Valor', 0) > 0)
            
            # Breakdown por TipoGasto
            por_tipo_gasto = {}
            for t in trans_list:
                tipo = t.get('TipoGasto') or 'Não Classificado'
                valor = t.get('Valor', 0)
                por_tipo_gasto[tipo] = por_tipo_gasto.get(tipo, 0) + valor
            
            stats_por_origem[origem] = {
                'tipo': 'extrato',
                'despesas': abs(despesas),
                'receitas': receitas,
                'saldo': receitas + despesas,
                'quantidade': len(trans_list),
                'breakdown': por_tipo_gasto
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
        # [PROTEÇÃO] Verifica duplicatas contra journal_entries antes de salvar
        ids_transacao_salvar = [t.get('IdTransacao') for t in transacoes_salvar]
        existing_ids = set(
            row[0] for row in db_session.query(JournalEntry.IdTransacao).filter(
                JournalEntry.IdTransacao.in_(ids_transacao_salvar)
            ).all()
        )
        
        # Filtra transações que já existem
        transacoes_novas = []
        duplicatas_encontradas = 0
        for t in transacoes_salvar:
            if t.get('IdTransacao') in existing_ids:
                duplicatas_encontradas += 1
                print(f"⚠️ Duplicata bloqueada: {t.get('Data')} - {t.get('Estabelecimento')} - R$ {t.get('Valor')}")
            else:
                transacoes_novas.append(t)
        
        if duplicatas_encontradas > 0:
            flash(f'{duplicatas_encontradas} duplicata(s) detectada(s) e bloqueada(s)', 'warning')
        
        if not transacoes_novas:
            flash('Todas as transações selecionadas já existem no banco de dados', 'warning')
            return redirect(url_for('upload.revisao_upload'))
        
        # [OTIMIZAÇÃO] Busca todos os contratos de parcelas de uma vez para evitar N+1 queries
        ids_parcela = [t.get('IdParcela') for t in transacoes_novas if t.get('IdParcela')]
        contratos_dict = {}
        if ids_parcela:
            contratos = db_session.query(BaseParcelas).filter(BaseParcelas.id_parcela.in_(ids_parcela)).all()
            contratos_dict = {c.id_parcela: c for c in contratos}
        
        salvos = 0
        for trans in transacoes_novas:
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
                IdParcela=trans.get('IdParcela'),  # [CRÍTICO] Salva IdParcela na transação
                IgnorarDashboard=ignorar,
                created_at=datetime.utcnow()
            )
            db_session.add(entry)
            
            # Atualiza BaseParcelas se for parcelado
            id_parcela = trans.get('IdParcela')
            if id_parcela:
                contrato = contratos_dict.get(id_parcela)  # [OTIMIZAÇÃO] Lookup O(1) ao invés de query
                
                if contrato:
                    # Atualiza contagem se ainda não finalizado
                    if contrato.status == 'ativo':
                        contrato.qtd_pagas += 1
                        if contrato.qtd_pagas >= contrato.qtd_parcelas:
                            contrato.status = 'finalizado'
                else:
                    # Cria novo contrato
                    info_parcela = detectar_parcela(trans.get('Estabelecimento'))
                    qtd_total = info_parcela['total'] if info_parcela else 0
                    
                    if qtd_total > 0:
                        novo_contrato = BaseParcelas(
                            id_parcela=id_parcela,
                            estabelecimento_base=normalizar_estabelecimento(trans.get('Estabelecimento')),
                            valor_parcela=abs(trans.get('Valor')),
                            qtd_parcelas=qtd_total,
                            grupo_sugerido=grupo,
                            subgrupo_sugerido=trans.get('SUBGRUPO'),
                            tipo_gasto_sugerido=trans.get('TipoGasto'),
                            qtd_pagas=1,
                            valor_total_plano=abs(trans.get('Valor')) * qtd_total,
                            data_inicio=trans.get('Data'),
                            status='finalizado' if qtd_total == 1 else 'ativo'
                        )
                        db_session.add(novo_contrato)
                        contratos_dict[id_parcela] = novo_contrato  # [OTIMIZAÇÃO] Adiciona ao cache
            
            salvos += 1
        
        db_session.commit()
        
        # [AUTO-SYNC] Sincroniza BaseParcelas automaticamente após salvar
        try:
            from collections import defaultdict
            
            # 1. Migra parcelas para BaseParcelas
            transacoes_parceladas = db_session.query(JournalEntry).filter(
                JournalEntry.IdParcela.isnot(None),
                JournalEntry.IdParcela != '',
                JournalEntry.TipoTransacao == 'Cartão de Crédito'
            ).all()
            
            grupos = defaultdict(list)
            for t in transacoes_parceladas:
                grupos[t.IdParcela].append(t)
            
            for id_parcela, items in grupos.items():
                contrato = db_session.query(BaseParcelas).filter_by(id_parcela=id_parcela).first()
                if contrato:
                    contrato.qtd_pagas = len(items)
                    if contrato.qtd_pagas >= contrato.qtd_parcelas:
                        contrato.status = 'finalizado'
            
            # 2. Remove órfãos
            used_ids = db_session.query(JournalEntry.IdParcela).distinct().all()
            used_ids = {id[0] for id in used_ids if id[0]}
            
            contratos = db_session.query(BaseParcelas).all()
            for c in contratos:
                if c.id_parcela not in used_ids:
                    db_session.delete(c)
            
            db_session.commit()
        except Exception as e:
            print(f"⚠️  Erro ao sincronizar BaseParcelas: {e}")
        
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
