"""
Script para limpar service.py removendo métodos obsoletos
Cria stubs que retornam HTTP 410 Gone
"""
import re

# Path do arquivo
SERVICE_PATH = "/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/app/domains/budget/service.py"

# Ler arquivo backup
with open(f"{SERVICE_PATH}.backup_consolidation", 'r') as f:
    lines = f.readlines()

# Encontrar linhas onde terminam métodos válidos
# Último método válido: bulk_upsert_budgets (linha ~590)

# Procurar linha que contém "return [BudgetResponse.from_orm(b) for b in result]" após bulk_upsert_budgets
valid_end_line = None
for i, line in enumerate(lines):
    if i > 580 and "return [BudgetResponse.from_orm(b) for b in result]" in line:
        valid_end_line = i + 1  # Próxima linha
        break

if not valid_end_line:
    print("❌ Não encontrou linha de corte")
    exit(1)

print(f"✅ Linha de corte: {valid_end_line} (linha {valid_end_line + 1} no arquivo)")

# Criar novo conteúdo: tudo até valid_end_line + stubs
new_content = ''.join(lines[:valid_end_line])

# Adicionar stubs para métodos obsoletos
stubs = '''
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # MÉTODOS OBSOLETOS - REMOVIDOS EM 13/02/2026
    # ═══════════════════════════════════════════════════════════════════════════════
    # Retornam HTTP 410 Gone se chamados
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def get_budget_geral_by_month(self, user_id: int, mes_referencia: str):
        """OBSOLETO - Use get_budget_planning()"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Use /api/v1/budget/planning")
    
    def get_all_budget_geral(self, user_id: int):
        """OBSOLETO - Use get_budget_planning()"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Use /api/v1/budget/planning")
    
    def bulk_upsert_budget_geral(self, user_id: int, mes_referencia: str, budgets: List[dict]):
        """OBSOLETO - Use bulk_upsert_budget_planning()"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Use /api/v1/budget/planning/bulk-upsert")
    
    def get_categorias_config(self, user_id: int, apenas_ativas: bool = True):
        """OBSOLETO - Categorias fixas"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Endpoint removido")
    
    def create_categoria_config(self, user_id: int, data: dict):
        """OBSOLETO"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Endpoint removido")
    
    def update_categoria_config(self, config_id: int, user_id: int, data: dict):
        """OBSOLETO"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Endpoint removido")
    
    def reordenar_categorias(self, user_id: int, reorders: List[Dict[str, int]]):
        """OBSOLETO"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Endpoint removido")
    
    def update_tipos_gasto_categoria(self, config_id: int, user_id: int, tipos_gasto: list):
        """OBSOLETO"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Endpoint removido")
    
    def delete_categoria_config(self, config_id: int, user_id: int):
        """OBSOLETO"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Endpoint removido")
    
    def bulk_upsert_budget_geral_com_validacao(self, user_id: int, mes_referencia: str, budgets: List[dict], total_mensal: float = None):
        """OBSOLETO"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Endpoint removido")
    
    def get_tipos_gasto_disponiveis(self, user_id: int, fonte_dados: str, filtro_valor: str):
        """OBSOLETO"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Tipos fixos (base_grupos_config)")
'''

new_content += stubs

# Escrever arquivo
with open(SERVICE_PATH, 'w') as f:
    f.write(new_content)

print(f"✅ service.py reescrito ({len(new_content)} chars)")
print(f"✅ Backup salvo em {SERVICE_PATH}.backup_consolidation")
