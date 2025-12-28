"""
Admin Routes - Gestão de configurações
"""
from flask import render_template, request, flash, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from app.blueprints.admin import admin_bp
from app.models import BaseMarcacao, BasePadrao, BaseParcelas, JournalEntry, GrupoConfig, EstabelecimentoLogo, get_db_session
from app.models_ignorar import IgnorarEstabelecimento, get_ignorar_estabelecimentos
from sqlalchemy import or_, desc


# Ação em massa: deletar ou ajustar transações selecionadas
@admin_bp.route('/transacoes/acao_massa', methods=['POST'])
def transacoes_acao_massa():
    db_session = get_db_session()
    ids = request.form.getlist('ids[]')
    acao = request.form.get('acao')
    if not ids:
        flash('Nenhuma transação selecionada.', 'warning')
        return redirect(url_for('admin.transacoes'))
    if acao == 'deletar':
        deletadas = db_session.query(JournalEntry).filter(JournalEntry.id.in_(ids)).delete(synchronize_session=False)
        db_session.commit()
        flash(f'{deletadas} transações deletadas com sucesso.', 'success')
    elif acao == 'ajustar':
        # Exemplo: marcar como revisadas (pode ser customizado)
        ajustadas = db_session.query(JournalEntry).filter(JournalEntry.id.in_(ids)).update({JournalEntry.TipoGasto: 'Ajustado'}, synchronize_session=False)
        db_session.commit()
        flash(f'{ajustadas} transações ajustadas.', 'info')
    else:
        flash('Ação inválida.', 'danger')
    db_session.close()
    return redirect(url_for('admin.transacoes'))


@admin_bp.route('/marcacoes')
def marcacoes():
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


@admin_bp.route('/marcacoes/criar', methods=['POST'])
def marcacoes_criar():
    """Cria nova marcação"""
    try:
        data = request.get_json()
        grupo = data.get('grupo', '').strip()
        subgrupo = data.get('subgrupo', '').strip()
        tipo_gasto = data.get('tipo_gasto', '').strip()
        
        if not grupo or not subgrupo or not tipo_gasto:
            return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'}), 400
        
        db_session = get_db_session()
        
        # Verificar se já existe
        existe = db_session.query(BaseMarcacao).filter(
            BaseMarcacao.GRUPO == grupo,
            BaseMarcacao.SUBGRUPO == subgrupo
        ).first()
        
        if existe:
            db_session.close()
            return jsonify({'success': False, 'message': 'Esta combinação de Grupo e Subgrupo já existe!'}), 400
        
        # Criar nova marcação
        nova_marcacao = BaseMarcacao(
            GRUPO=grupo,
            SUBGRUPO=subgrupo,
            TipoGasto=tipo_gasto
        )
        
        db_session.add(nova_marcacao)
        db_session.commit()
        db_session.close()
        
        return jsonify({'success': True, 'message': 'Marcação criada com sucesso!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/padroes')
def padroes():
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


@admin_bp.route('/parcelas')
def parcelas():
    """Administração de parcelas (contratos)"""
    
    db_session = get_db_session()
    
    # Filtros
    status_filtro = request.args.get('status', '')
    busca = request.args.get('busca', '')
    
    # Query base
    query = db_session.query(BaseParcelas)
    
    if status_filtro:
        query = query.filter(BaseParcelas.status == status_filtro)
    
    if busca:
        query = query.filter(BaseParcelas.estabelecimento_base.like(f'%{busca}%'))
    
    # Paginação
    page = int(request.args.get('page', 1))
    per_page = 50
    
    parcelas_paginadas = query.order_by(BaseParcelas.status, BaseParcelas.estabelecimento_base).limit(per_page).offset((page-1)*per_page).all()
    total = query.count()
    total_pages = (total + per_page - 1) // per_page
    
    db_session.close()
    
    return render_template(
        'admin_parcelas.html',
        parcelas=parcelas_paginadas,
        page=page,
        total_pages=total_pages,
        total=total,
        status_filtro=status_filtro,
        busca=busca
    )


@admin_bp.route('/transacoes', methods=['GET'])
def transacoes():
    """Administração de todas as transações (JournalEntry)"""
    
    db_session = get_db_session()
    
    # Filtros
    busca = request.args.get('busca', '')
    id_parcela_filtro = request.args.get('id_parcela', '')
    grupo_filtro = request.args.get('grupo', '')
    origem_filtro = request.args.get('origem', '')
    
    # Query base
    query = db_session.query(JournalEntry)
    
    if busca:
        query = query.filter(JournalEntry.Estabelecimento.like(f'%{busca}%'))
    
    if id_parcela_filtro:
        query = query.filter(JournalEntry.IdParcela.like(f'%{id_parcela_filtro}%'))
        
    if grupo_filtro:
        query = query.filter(JournalEntry.GRUPO == grupo_filtro)
    
    if origem_filtro:
        query = query.filter(JournalEntry.origem.like(f'%{origem_filtro}%'))
    
    # Paginação
    page = int(request.args.get('page', 1))
    per_page = 50
    
    # Ordenação padrão: Data desc, ID desc
    # Como Data é string DD/MM/AAAA, a ordenação direta não funciona bem cronologicamente
    # Idealmente converteríamos, mas para admin simples vamos ordenar por ID desc (mais recentes inseridos)
    transacoes_paginadas = query.order_by(desc(JournalEntry.id)).limit(per_page).offset((page-1)*per_page).all()
    total = query.count()
    total_pages = (total + per_page - 1) // per_page
    
    # Grupos para filtro
    grupos_unicos = db_session.query(JournalEntry.GRUPO).distinct().order_by(JournalEntry.GRUPO).all()
    grupos_lista = [g[0] for g in grupos_unicos if g[0]]
    
    # Origens para filtro
    origens_unicas = db_session.query(JournalEntry.origem).distinct().order_by(JournalEntry.origem).all()
    origens_lista = [o[0] for o in origens_unicas if o[0]]
    
    # Calcular soma dos valores filtrados
    soma_filtrada = sum(t.Valor for t in transacoes_paginadas)
    
    db_session.close()
    
    # Usar template compartilhado com mesmas variáveis do dashboard
    return render_template(
        'transacoes.html',
        transacoes=transacoes_paginadas,
        mes_atual='admin',  # Indica que veio do admin
        mes_exibicao='Administração Geral',
        total_transacoes=total,
        soma_filtrada=soma_filtrada,
        grupos_lista=grupos_lista,
        filtro_estabelecimento=busca,
        filtro_categoria=grupo_filtro,
        filtros_tipos=[],  # Admin não usa filtro de tipo
        filtro_dashboard='todas',  # Admin mostra todas por padrão
        page=page,
        total_pages=total_pages,
        # Variáveis específicas do admin (extras)
        id_parcela_filtro=id_parcela_filtro,
        origem_filtro=origem_filtro,
        origens_lista=origens_lista
    )


@admin_bp.route('/grupos')
def grupos():
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


@admin_bp.route('/grupos/salvar', methods=['POST'])
def grupos_salvar():
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


@admin_bp.route('/grupos/deletar/<int:grupo_id>', methods=['POST'])
def grupos_deletar(grupo_id):
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


@admin_bp.route('/api/grupos-cores', methods=['GET'])
def api_grupos_cores_get():
    """API para obter cores dos grupos"""
    try:
        from app.models import BaseMarcacao
        from app.filters import get_group_color_helper
        
        db = get_db_session()
        
        # Busca grupos únicos da BaseMarcacao
        grupos_base = db.query(BaseMarcacao.GRUPO).distinct().order_by(BaseMarcacao.GRUPO).all()
        
        # Para cada grupo, busca config ou usa padrão
        grupos_data = []
        for (grupo_nome,) in grupos_base:
            if not grupo_nome:
                continue
                
            # Busca config existente
            config = db.query(GrupoConfig).filter_by(nome=grupo_nome, ativo=True).first()
            
            if config:
                grupo_id = config.id
                cor = config.cor or get_group_color_helper(grupo_nome)
                icone = config.icone or 'fa-folder'
            else:
                # Cria entrada temporária para permitir edição
                grupo_id = f"new_{grupo_nome}"  # ID temporário
                cor = get_group_color_helper(grupo_nome)
                icone = get_group_icon_default(grupo_nome)
            
            grupos_data.append({
                'id': grupo_id,
                'nome': grupo_nome,
                'cor': cor,
                'icone': icone
            })
        
        db.close()
        return jsonify({'success': True, 'grupos': grupos_data})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def get_group_icon_default(grupo):
    """Retorna ícone padrão para grupo"""
    icons = {
        'Alimentação': 'fa-utensils',
        'Transporte': 'fa-car',
        'Moradia': 'fa-home',
        'Casa': 'fa-home',
        'Saúde': 'fa-heartbeat',
        'Educação': 'fa-graduation-cap',
        'Lazer': 'fa-gamepad',
        'Entretenimento': 'fa-gamepad',
        'Assinaturas': 'fa-file-invoice',
        'Vestuário': 'fa-tshirt',
        'Roupas': 'fa-tshirt',
        'Investimentos': 'fa-chart-line',
        'Impostos': 'fa-landmark',
        'Seguros': 'fa-shield-alt',
        'Doações': 'fa-hand-holding-heart',
        'Carro': 'fa-car',
        'Presentes': 'fa-gift',
        'Limpeza': 'fa-broom',
        'Salário': 'fa-money-bill-wave',
        'Outros': 'fa-tag'
    }
    return icons.get(grupo, 'fa-folder')


@admin_bp.route('/api/grupos-cores', methods=['POST'])
def api_grupos_cores_post():
    """API para atualizar cores dos grupos"""
    try:
        from app.models import BaseMarcacao
        
        data = request.get_json()
        cores = data.get('cores', {})
        
        if not cores:
            return jsonify({'success': False, 'error': 'Nenhuma cor fornecida'}), 400
        
        db = get_db_session()
        
        for grupo_id, cor in cores.items():
            # Se é ID temporário (new_NomeGrupo), cria novo config
            if str(grupo_id).startswith('new_'):
                grupo_nome = str(grupo_id).replace('new_', '')
                
                # Verifica se já existe
                config = db.query(GrupoConfig).filter_by(nome=grupo_nome).first()
                if not config:
                    config = GrupoConfig(
                        nome=grupo_nome,
                        cor=cor,
                        icone=get_group_icon_default(grupo_nome),
                        ativo=True
                    )
                    db.add(config)
                else:
                    config.cor = cor
            else:
                # ID real, apenas atualiza
                grupo = db.query(GrupoConfig).filter_by(id=int(grupo_id)).first()
                if grupo:
                    grupo.cor = cor
        
        db.commit()
        db.close()
        
        flash('Cores atualizadas com sucesso!', 'success')
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/logos')
def logos():
    """Administração de logos de estabelecimentos"""
    db = get_db_session()
    logos = db.query(EstabelecimentoLogo).order_by(EstabelecimentoLogo.nome_exibicao).all()
    db.close()
    return render_template('admin_logos.html', logos=logos)


@admin_bp.route('/logos/upload', methods=['POST'])
def logos_upload():
    """Upload de NOVO logo de estabelecimento"""
    try:
        from flask import current_app
        
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
        if file_length > current_app.config['MAX_LOGO_SIZE']:
            return jsonify({'success': False, 'error': 'Arquivo muito grande (máx 2MB)'}), 400
        file.seek(0)
        
        # Validar extensão
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'success': False, 'error': 'Formato não suportado'}), 400
        
        # Gerar nome seguro do arquivo
        nome_arquivo = secure_filename(f"{nome_busca.lower().replace(' ', '_').replace(',', '')}{file_ext}")
        caminho_completo = os.path.join(current_app.config['LOGOS_FOLDER'], nome_arquivo)
        
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


@admin_bp.route('/logos/update/<int:logo_id>', methods=['POST'])
def logos_update(logo_id):
    """Atualizar logo existente"""
    try:
        from flask import current_app
        
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
            if file_length > current_app.config['MAX_LOGO_SIZE']:
                return jsonify({'success': False, 'error': 'Arquivo muito grande (máx 2MB)'}), 400
            file.seek(0)
            
            # Validar extensão
            allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'}
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                return jsonify({'success': False, 'error': 'Formato não suportado'}), 400
            
            # Gerar nome seguro do arquivo
            nome_arquivo = secure_filename(f"{nome_busca.lower().replace(' ', '_').replace(',', '')}{file_ext}")
            caminho_completo = os.path.join(current_app.config['LOGOS_FOLDER'], nome_arquivo)
            
            # Deletar arquivo antigo se diferente
            if logo.arquivo_logo != nome_arquivo:
                caminho_antigo = os.path.join(current_app.config['LOGOS_FOLDER'], logo.arquivo_logo)
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


@admin_bp.route('/logos/deletar/<int:logo_id>', methods=['POST'])
def logos_deletar(logo_id):
    """Deleta logo de estabelecimento"""
    try:
        from flask import current_app
        
        db = get_db_session()
        logo = db.query(EstabelecimentoLogo).filter_by(id=logo_id).first()
        
        if not logo:
            return jsonify({'success': False, 'error': 'Logo não encontrado'}), 404
        
        # Deletar arquivo
        caminho_arquivo = os.path.join(current_app.config['LOGOS_FOLDER'], logo.arquivo_logo)
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)
        
        db.delete(logo)
        db.commit()
        db.close()
        
        flash('Logo deletado com sucesso!', 'success')
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Tela de administração dos estabelecimentos a ignorar
@admin_bp.route('/ignorar_estabelecimentos', methods=['GET'])
def ignorar_estabelecimentos():
    estabelecimentos = get_ignorar_estabelecimentos()
    return render_template('admin_ignorar_estabelecimentos.html', estabelecimentos=estabelecimentos)


# Adicionar estabelecimento a ignorar
@admin_bp.route('/ignorar_estabelecimentos/add', methods=['POST'])
def ignorar_estabelecimentos_add():
    from app.models import get_db_session
    nome = request.form.get('nome','').strip()
    tipo = request.form.get('tipo','ambos')
    if nome:
        session = get_db_session()
        if not session.query(IgnorarEstabelecimento).filter_by(nome=nome).first():
            session.add(IgnorarEstabelecimento(nome=nome, tipo=tipo))
            session.commit()
        session.close()
    return redirect(url_for('admin.ignorar_estabelecimentos'))


# Remover estabelecimento da lista de ignorados
@admin_bp.route('/ignorar_estabelecimentos/del/<int:id>', methods=['POST'])
def ignorar_estabelecimentos_del(id):
    from app.models import get_db_session
    session = get_db_session()
    session.query(IgnorarEstabelecimento).filter_by(id=id).delete()
    session.commit()
    session.close()
    return redirect(url_for('admin.ignorar_estabelecimentos'))
