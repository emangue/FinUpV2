"""
Script para atualizar url_for() nos templates para usar blueprints
"""
import os
import re

# Mapeamento de rotas antigas para novas (blueprint.rota)
ROUTE_MAPPING = {
    # Dashboard routes
    "url_for('dashboard')": "url_for('dashboard.index')",
    "url_for('transacoes')": "url_for('dashboard.transacoes')",
    "url_for('api_transacao_detalhes'": "url_for('dashboard.api_transacao_detalhes'",
    "url_for('toggle_dashboard_status'": "url_for('dashboard.toggle_dashboard_status'",
    
    # Upload routes
    "url_for('upload')": "url_for('upload.upload')",
    "url_for('revisao_upload')": "url_for('upload.revisao_upload')",
    "url_for('duplicados')": "url_for('upload.duplicados')",
    "url_for('validar')": "url_for('upload.validar')",
    "url_for('validar_lote')": "url_for('upload.validar_lote')",
    "url_for('salvar')": "url_for('upload.salvar')",
    "url_for('adicionar_marcacao')": "url_for('upload.adicionar_marcacao')",
    "url_for('listar_marcacoes')": "url_for('upload.listar_marcacoes')",
    
    # Admin routes
    "url_for('admin_marcacoes')": "url_for('admin.marcacoes')",
    "url_for('admin_padroes')": "url_for('admin.padroes')",
    "url_for('admin_grupos')": "url_for('admin.grupos')",
    "url_for('admin_grupos_salvar')": "url_for('admin.grupos_salvar')",
    "url_for('admin_grupos_deletar'": "url_for('admin.grupos_deletar'",
    "url_for('admin_logos')": "url_for('admin.logos')",
    "url_for('admin_logos_upload')": "url_for('admin.logos_upload')",
    "url_for('admin_logos_update'": "url_for('admin.logos_update'",
    "url_for('admin_logos_deletar'": "url_for('admin.logos_deletar'",
}

def atualizar_template(filepath):
    """Atualiza um template individual"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    modificado = False
    
    for old_route, new_route in ROUTE_MAPPING.items():
        if old_route in content:
            content = content.replace(old_route, new_route)
            modificado = True
            print(f"  ✓ {old_route} → {new_route}")
    
    if modificado:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def processar_diretorio(directory):
    """Processa todos os templates em um diretório"""
    count = 0
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.html'):
                filepath = os.path.join(root, filename)
                print(f"\n📝 Processando: {filepath}")
                if atualizar_template(filepath):
                    count += 1
                    print("  ✅ Atualizado!")
                else:
                    print("  ℹ️  Nenhuma alteração necessária")
    return count

if __name__ == '__main__':
    print("🔄 Atualizando url_for() nos templates...\n")
    
    # Processa templates na raiz (compartilhados)
    print("=" * 60)
    print("TEMPLATES COMPARTILHADOS (templates/)")
    print("=" * 60)
    count_root = processar_diretorio('templates')
    
    # Processa templates dos blueprints
    print("\n" + "=" * 60)
    print("TEMPLATES DOS BLUEPRINTS (app/blueprints/)")
    print("=" * 60)
    count_blueprints = processar_diretorio('app/blueprints')
    
    total = count_root + count_blueprints
    print("\n" + "=" * 60)
    print(f"✅ Concluído! {total} arquivos atualizados.")
    print("=" * 60)
