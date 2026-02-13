# 🚀 Plano de Implementação - Fase 5: Teste User Inicial

**Data de Criação:** 13/02/2026  
**Objetivo:** Implementar todas as melhorias mapeadas para onboarding de novos usuários  
**Duração Estimada:** 4 sprints (~2-3 semanas)  
**Prioridade:** 🔴 CRÍTICA

---

## 📊 Visão Geral dos Sprints

| Sprint | Objetivo | Duração | Status |
|--------|----------|---------|--------|
| **Sprint 1** | Consolidação Budget Tables | 2-3 dias | 📋 Planejado |
| **Sprint 2** | Auto-criação de Dados Default | 1-2 dias | 📋 Planejado |
| **Sprint 3** | Criar Grupos/Subgrupos na UI | 2-3 dias | 📋 Planejado |
| **Sprint 4** | Validação E2E e Refinamentos | 1-2 dias | 📋 Planejado |

**Total:** 6-10 dias úteis (~2 semanas com buffer)

---

## 🎯 Sprint 1: Consolidação Budget Tables (CRÍTICO)

**Duração:** 2-3 dias  
**Por quê primeiro:** Remove redundância, simplifica arquitetura em 75%  
**Bloqueante para:** Sprint 2 (auto-criação usa budget_planning)

### 📋 TODOs Detalhados

#### **1.1 Preparação - Análise de Impacto** (30 min)

- [ ] 1.1.1 Listar TODOS os endpoints que usam budget_geral
  ```bash
  cd app_dev/backend
  grep -r "budget_geral" app/domains --include="*.py"
  ```

- [ ] 1.1.2 Listar TODOS os componentes frontend que usam budget_geral
  ```bash
  cd app_dev/frontend
  grep -r "budget.*geral" src --include="*.tsx" --include="*.ts"
  ```

- [ ] 1.1.3 Criar branch feature
  ```bash
  git checkout -b feature/consolidate-budget-tables
  ```

---

#### **1.2 Backend - Database Migration** (2-3 horas)

- [ ] 1.2.1 Criar migration Alembic
  ```bash
  cd app_dev/backend
  source ../../.venv/bin/activate
  alembic revision -m "consolidate_budget_tables"
  ```

- [ ] 1.2.2 Escrever migration - upgrade()
  ```python
  # migrations/versions/XXXX_consolidate_budget_tables.py
  
  def upgrade():
      # 1. Migrar dados: budget_geral → budget_planning
      op.execute("""
          INSERT INTO budget_planning (
              user_id, ano, mes, grupo, 
              valor_planejado, ativo, created_at
          )
          SELECT 
              bg.user_id,
              bg.Ano,
              bg.Mes,
              bgc.nome_grupo,
              bg.total_mensal,  -- ou valor_planejado (são iguais)
              1 as ativo,
              COALESCE(bg.created_at, CURRENT_TIMESTAMP)
          FROM budget_geral bg
          INNER JOIN base_grupos_config bgc 
              ON bgc.user_id = bg.user_id
          WHERE NOT EXISTS (
              SELECT 1 FROM budget_planning bp
              WHERE bp.user_id = bg.user_id
                AND bp.ano = bg.Ano
                AND bp.mes = bg.Mes
                AND bp.grupo = bgc.nome_grupo
          );
      """)
      
      # 2. Deletar tabelas antigas
      op.drop_table('budget_geral_historico')
      op.drop_table('budget_categoria_config')
      op.drop_table('budget_geral')
  ```

- [ ] 1.2.3 Escrever migration - downgrade()
  ```python
  def downgrade():
      # Recriar tabelas (sem migrar dados de volta)
      op.create_table('budget_geral', ...)
      op.create_table('budget_categoria_config', ...)
      op.create_table('budget_geral_historico', ...)
      
      # Log warning
      print("⚠️  Downgrade criou tabelas vazias. Dados foram perdidos!")
  ```

- [ ] 1.2.4 Testar migration em banco de testes
  ```bash
  # Backup primeiro
  cp financas_dev.db financas_dev.db.backup_pre_migration
  
  # Aplicar
  alembic upgrade head
  
  # Validar
  sqlite3 financas_dev.db ".tables" | grep budget
  sqlite3 financas_dev.db "SELECT COUNT(*) FROM budget_planning;"
  ```

- [ ] 1.2.5 Validar integridade dos dados migrados
  ```bash
  sqlite3 financas_dev.db <<EOF
  SELECT 
      'budget_planning' as tabela,
      COUNT(*) as registros,
      COUNT(DISTINCT user_id) as usuarios,
      MIN(ano) as ano_min,
      MAX(ano) as ano_max
  FROM budget_planning;
  EOF
  ```

---

#### **1.3 Backend - Remover Código Antigo** (2 horas)

- [ ] 1.3.1 Deletar models antigos
  ```bash
  # Arquivos a deletar:
  rm app/domains/budget/models_geral.py  # Se existir separado
  
  # OU remover classes em app/domains/budget/models.py:
  # - BudgetGeral
  # - BudgetCategoriaConfig
  # - BudgetGeralHistorico
  ```

- [ ] 1.3.2 Deletar schemas antigos
  ```bash
  # Verificar e remover em app/domains/budget/schemas.py:
  # - BudgetGeralCreate
  # - BudgetGeralUpdate
  # - BudgetGeralResponse
  # - BudgetCategoriaConfigCreate/Update/Response
  # E outros 7 schemas relacionados
  ```

- [ ] 1.3.3 Atualizar repository
  ```python
  # app/domains/budget/repository.py
  
  # ANTES:
  def get_budget_geral(self, user_id, ano, mes):
      return self.db.query(BudgetGeral).filter(...).first()
  
  # DEPOIS:
  def get_budget_planning(self, user_id, ano, mes, grupo):
      return self.db.query(BudgetPlanning).filter(...).first()
  ```

- [ ] 1.3.4 Remover endpoints antigos
  ```python
  # app/domains/budget/router.py
  
  # Comentar ou remover:
  # @router.get("/geral/{ano}/{mes}")
  # @router.post("/geral")
  # @router.put("/geral/{id}")
  # ... total de ~3 endpoints
  ```

- [ ] 1.3.5 Atualizar service layer
  ```python
  # app/domains/budget/service.py
  
  # Refatorar todos os métodos que usavam budget_geral
  # para usar budget_planning
  ```

---

#### **1.4 Frontend - Refactor Mobile** (2-3 horas)

- [ ] 1.4.1 Atualizar API calls em /mobile/budget
  ```typescript
  // ANTES:
  const response = await fetch('/api/v1/budget/geral')
  
  // DEPOIS:
  const response = await fetch('/api/v1/budget/planning')
  ```

- [ ] 1.4.2 Atualizar types/interfaces
  ```typescript
  // src/types/budget.ts
  
  // Remover:
  interface BudgetGeral { ... }
  
  // Usar apenas:
  interface BudgetPlanning { ... }
  ```

- [ ] 1.4.3 Refatorar componente principal de metas
  ```bash
  # Arquivo: src/app/mobile/budget/page.tsx
  # Mudanças:
  # - categoria_geral → grupo
  # - total_mensal → valor_planejado
  # - Remover lógica de budget_geral
  ```

- [ ] 1.4.4 Testar tela de metas mobile
  - [ ] Carregar metas existentes
  - [ ] Criar nova meta
  - [ ] Editar meta existente
  - [ ] Deletar meta

---

#### **1.5 Frontend - Refactor Desktop** (1-2 horas)

- [ ] 1.5.1 Atualizar /budget (se existir versão desktop)
  ```typescript
  // Mesmas mudanças que mobile:
  // - API calls
  // - Types
  // - Lógica de negócio
  ```

- [ ] 1.5.2 Atualizar dashboard (comparação meta vs real)
  ```typescript
  // src/app/dashboard/page.tsx
  
  // ANTES:
  const metas = await fetch('/api/v1/budget/geral/...')
  
  // DEPOIS:
  const metas = await fetch('/api/v1/budget/planning/...')
  ```

---

#### **1.6 Testes e Validação** (1-2 horas)

- [ ] 1.6.1 Testes unitários backend
  ```python
  # tests/domains/budget/test_service.py
  
  def test_create_budget_planning():
      # Criar meta
      # Validar que salvou em budget_planning
      # Validar que NÃO existe em budget_geral (deletado)
  
  def test_get_budget_planning():
      # Buscar meta
      # Validar estrutura do response
  ```

- [ ] 1.6.2 Testes E2E frontend
  ```bash
  # Cypress ou Playwright
  # - Criar meta
  # - Editar meta
  # - Deletar meta
  # - Visualizar dashboard com metas
  ```

- [ ] 1.6.3 Smoke tests em produção
  - [ ] Backup do banco produção
  - [ ] Aplicar migration em staging
  - [ ] Validar dados migrados
  - [ ] Testar endpoints críticos
  - [ ] Se OK → aplicar em prod

---

#### **1.7 Deploy e Documentação** (1 hora)

- [ ] 1.7.1 Atualizar CHANGELOG.md
  ```markdown
  ## [v2.1.0] - 2026-02-XX
  
  ### 🗑️ Breaking Changes
  - Removidas tabelas: budget_geral, budget_categoria_config, budget_geral_historico
  - Consolidado em: budget_planning
  - Campo removido: total_mensal (redundante com valor_planejado)
  
  ### ✨ Melhorias
  - Arquitetura 75% mais simples
  - Zero redundância de dados
  - Queries mais rápidas
  ```

- [ ] 1.7.2 Atualizar documentação técnica
  - [ ] Diagramas de banco (remover tabelas antigas)
  - [ ] Endpoints API (remover rotas antigas)
  - [ ] Schemas Pydantic (atualizar)

- [ ] 1.7.3 Merge e deploy
  ```bash
  git add .
  git commit -m "feat: consolida budget tables (budget_geral → budget_planning)"
  git push origin feature/consolidate-budget-tables
  
  # Criar PR → Review → Merge → Deploy
  ```

---

### ✅ Critérios de Aceitação Sprint 1

- [ ] ✅ Migration executada sem erros
- [ ] ✅ 100% dos dados migrados (validação SQL)
- [ ] ✅ 3 tabelas deletadas (geral, categoria_config, historico)
- [ ] ✅ Backend compila sem erros
- [ ] ✅ Frontend compila sem erros
- [ ] ✅ Testes unitários passando
- [ ] ✅ Telas de metas funcionando (mobile + desktop)
- [ ] ✅ Dashboard exibindo metas corretamente
- [ ] ✅ Documentação atualizada

---

## 🎯 Sprint 2: Auto-criação de Dados Default

**Duração:** 1-2 dias  
**Dependência:** Sprint 1 completo (usa budget_planning)  
**Objetivo:** Novos usuários iniciam com estrutura completa

### 📋 TODOs Detalhados

#### **2.1 Backend - Função de Populamento** (2-3 horas)

- [ ] 2.1.1 Criar service de populamento
  ```python
  # app/domains/users/services/user_defaults.py
  
  from datetime import datetime
  from sqlalchemy.orm import Session
  from app.domains.budget.models import BudgetPlanning
  from app.domains.cards.models import Cartao
  
  class UserDefaultsService:
      def __init__(self, db: Session):
          self.db = db
      
      def populate_new_user(self, user_id: int) -> dict:
          """
          Popula dados default para novo usuário
          
          Returns:
              dict com contadores de registros criados
          """
          try:
              stats = {
                  'budget_planning': 0,
                  'cartoes': 0
              }
              
              # 1. Budget Planning (estrutura vazia)
              stats['budget_planning'] = self._create_budget_structure(user_id)
              
              # 2. Cartão genérico
              stats['cartoes'] = self._create_default_card(user_id)
              
              self.db.commit()
              return stats
              
          except Exception as e:
              self.db.rollback()
              raise Exception(f"Erro ao popular usuário {user_id}: {str(e)}")
  ```

- [ ] 2.1.2 Implementar _create_budget_structure()
  ```python
  def _create_budget_structure(self, user_id: int) -> int:
      """
      Cria estrutura de budget para 3 meses (atual + 2 próximos)
      10 grupos × 3 meses = 30 registros
      """
      current_date = datetime.now()
      current_year = current_date.year
      current_month = current_date.month
      
      # Buscar grupos ativos do sistema
      grupos = self.db.query(BaseGruposConfig).filter(
          BaseGruposConfig.ativo == True
      ).all()
      
      count = 0
      for i in range(3):  # 3 meses
          month = current_month + i
          year = current_year
          
          if month > 12:
              month = month - 12
              year += 1
          
          for grupo in grupos:
              # Verificar se já existe
              exists = self.db.query(BudgetPlanning).filter(
                  BudgetPlanning.user_id == user_id,
                  BudgetPlanning.ano == year,
                  BudgetPlanning.mes == month,
                  BudgetPlanning.grupo == grupo.nome_grupo
              ).first()
              
              if not exists:
                  budget = BudgetPlanning(
                      user_id=user_id,
                      ano=year,
                      mes=month,
                      grupo=grupo.nome_grupo,
                      valor_planejado=0.00,  # Usuário preenche depois
                      ativo=True,
                      created_at=datetime.now()
                  )
                  self.db.add(budget)
                  count += 1
      
      return count
  ```

- [ ] 2.1.3 Implementar _create_default_card()
  ```python
  def _create_default_card(self, user_id: int) -> int:
      """
      Cria cartão genérico para não bloquear uploads de fatura
      """
      # Verificar se já existe cartão
      has_card = self.db.query(Cartao).filter(
          Cartao.user_id == user_id
      ).first()
      
      if has_card:
          return 0
      
      # Criar cartão padrão
      card = Cartao(
          user_id=user_id,
          nome="Cartão Padrão",
          final="0000",
          bandeira="Genérico",
          limite=0.00,
          ativo=True,
          created_at=datetime.now()
      )
      self.db.add(card)
      return 1
  ```

---

#### **2.2 Backend - Integração com Registro** (1 hora)

- [ ] 2.2.1 Atualizar UserService.create_user()
  ```python
  # app/domains/users/service.py
  
  def create_user(self, data: UserCreate) -> User:
      # ... código existente de criar usuário ...
      
      new_user = User(**data.dict())
      self.db.add(new_user)
      self.db.flush()  # Gera user.id
      
      # NOVO: Popular dados default
      try:
          defaults_service = UserDefaultsService(self.db)
          stats = defaults_service.populate_new_user(new_user.id)
          logger.info(f"Dados default criados: {stats}")
      except Exception as e:
          logger.error(f"Falha ao popular defaults: {e}")
          # NÃO fazer rollback - usuário é criado mesmo se defaults falharem
      
      self.db.commit()
      self.db.refresh(new_user)
      return new_user
  ```

---

#### **2.3 Script Standalone** (1 hora)

- [ ] 2.3.1 Criar script para popular usuários existentes
  ```python
  # scripts/database/popular_user_defaults.py
  
  """
  Popula dados default para usuários existentes que não têm
  """
  
  import sys
  from pathlib import Path
  sys.path.append(str(Path(__file__).parent.parent.parent / "app_dev/backend"))
  
  from app.core.database import get_db
  from app.domains.users.models import User
  from app.domains.users.services.user_defaults import UserDefaultsService
  
  def main():
      db = next(get_db())
      
      # Buscar usuários sem dados default
      users = db.query(User).all()
      
      for user in users:
          # Verificar se já tem budget
          has_budget = db.query(BudgetPlanning).filter(
              BudgetPlanning.user_id == user.id
          ).first()
          
          if not has_budget:
              print(f"Populando usuário {user.id} ({user.email})...")
              service = UserDefaultsService(db)
              stats = service.populate_new_user(user.id)
              print(f"  ✅ Criados: {stats}")
          else:
              print(f"Usuário {user.id} já tem dados, pulando")
  
  if __name__ == "__main__":
      main()
  ```

- [ ] 2.3.2 Testar script
  ```bash
  python scripts/database/popular_user_defaults.py
  ```

---

#### **2.4 Testes e Validação** (1 hora)

- [ ] 2.4.1 Teste unitário do service
  ```python
  # tests/domains/users/test_user_defaults.py
  
  def test_populate_new_user():
      # Criar usuário teste
      user = create_test_user(db)
      
      # Popular defaults
      service = UserDefaultsService(db)
      stats = service.populate_new_user(user.id)
      
      # Validar contadores
      assert stats['budget_planning'] == 30  # 10 grupos × 3 meses
      assert stats['cartoes'] == 1
      
      # Validar dados criados
      budgets = db.query(BudgetPlanning).filter(
          BudgetPlanning.user_id == user.id
      ).count()
      assert budgets == 30
      
      cards = db.query(Cartao).filter(
          Cartao.user_id == user.id
      ).count()
      assert cards == 1
  ```

- [ ] 2.4.2 Teste E2E - Criar usuário novo
  ```bash
  # Via API ou frontend
  # 1. Criar usuário
  # 2. Login
  # 3. Verificar que dashboard tem estrutura (mesmo vazio)
  # 4. Verificar que pode criar meta imediatamente
  # 5. Verificar que pode fazer upload com cartão padrão
  ```

---

### ✅ Critérios de Aceitação Sprint 2

- [ ] ✅ Service UserDefaultsService criado e testado
- [ ] ✅ Integrado em create_user()
- [ ] ✅ Script standalone funcionando
- [ ] ✅ Novos usuários iniciam com ~30 registros
- [ ] ✅ Dashboard não exibe EmptyState (tem estrutura)
- [ ] ✅ Pode criar meta sem criar estrutura antes
- [ ] ✅ Pode fazer upload com cartão padrão

---

## 🎯 Sprint 3: Criar Grupos/Subgrupos na UI

**Duração:** 2-3 dias  
**Dependência:** Sprint 1 (consolidação completa)  
**Objetivo:** UX fluida para criar classificações durante upload

### 📋 TODOs Detalhados

#### **3.1 Backend - Endpoints de Criação** (2 horas)

- [ ] 3.1.1 Criar schemas Pydantic
  ```python
  # app/domains/upload/schemas.py
  
  class CriarGrupoSchema(BaseModel):
      grupo: str = Field(..., min_length=1, max_length=100)
      primeiro_subgrupo: str = Field(..., min_length=1, max_length=100)
      tipo_gasto: str = Field(..., pattern="^(Fixo|Variável|Investimento)$")
      categoria_geral: str = Field(..., pattern="^(Receita|Despesa)$")
      
      @validator('grupo', 'primeiro_subgrupo')
      def trim_and_title(cls, v):
          return v.strip().title()
  
  class CriarSubgrupoSchema(BaseModel):
      grupo: str = Field(..., min_length=1, max_length=100)
      subgrupo: str = Field(..., min_length=1, max_length=100)
      
      @validator('grupo', 'subgrupo')
      def trim_and_title(cls, v):
          return v.strip().title()
  ```

- [ ] 3.1.2 Implementar POST /classification/grupo
  ```python
  # app/domains/upload/router.py
  
  @router.post("/classification/grupo")
  def criar_grupo(
      data: CriarGrupoSchema,
      user_id: int = Depends(get_current_user_id),
      db: Session = Depends(get_db)
  ):
      # Validar se grupo já existe
      grupo_exists = db.query(BaseGruposConfig).filter(
          BaseGruposConfig.user_id == user_id,
          BaseGruposConfig.nome_grupo == data.grupo
      ).first()
      
      if grupo_exists:
          raise HTTPException(400, f"Grupo '{data.grupo}' já existe")
      
      # Criar grupo
      novo_grupo = BaseGruposConfig(
          user_id=user_id,
          nome_grupo=data.grupo,
          tipo_gasto_padrao=data.tipo_gasto,
          categoria_geral=data.categoria_geral,
          ativo=True,
          created_at=datetime.now()
      )
      db.add(novo_grupo)
      
      # Criar primeiro subgrupo
      primeira_marcacao = BaseMarcacoes(
          user_id=user_id,
          GRUPO=data.grupo,
          SUBGRUPO=data.primeiro_subgrupo,
          origem="manual_criacao",
          created_at=datetime.now()
      )
      db.add(primeira_marcacao)
      
      db.commit()
      db.refresh(novo_grupo)
      db.refresh(primeira_marcacao)
      
      return {
          "success": True,
          "grupo": {
              "id": novo_grupo.id,
              "nome": novo_grupo.nome_grupo,
              "tipo_gasto": novo_grupo.tipo_gasto_padrao,
              "categoria_geral": novo_grupo.categoria_geral
          },
          "subgrupo": {
              "id": primeira_marcacao.id,
              "subgrupo": primeira_marcacao.SUBGRUPO
          }
      }
  ```

- [ ] 3.1.3 Implementar POST /classification/subgrupo
  ```python
  @router.post("/classification/subgrupo")
  def criar_subgrupo(
      data: CriarSubgrupoSchema,
      user_id: int = Depends(get_current_user_id),
      db: Session = Depends(get_db)
  ):
      # Validar se grupo existe
      grupo_exists = db.query(BaseGruposConfig).filter(
          BaseGruposConfig.user_id == user_id,
          BaseGruposConfig.nome_grupo == data.grupo
      ).first()
      
      if not grupo_exists:
          raise HTTPException(400, f"Grupo '{data.grupo}' não existe")
      
      # Validar se subgrupo já existe
      subgrupo_exists = db.query(BaseMarcacoes).filter(
          BaseMarcacoes.user_id == user_id,
          BaseMarcacoes.SUBGRUPO == data.subgrupo,
          BaseMarcacoes.GRUPO == data.grupo
      ).first()
      
      if subgrupo_exists:
          raise HTTPException(400, f"Subgrupo '{data.subgrupo}' já existe")
      
      # Criar mapeamento
      nova_marcacao = BaseMarcacoes(
          user_id=user_id,
          GRUPO=data.grupo,
          SUBGRUPO=data.subgrupo,
          origem="manual_criacao",
          created_at=datetime.now()
      )
      db.add(nova_marcacao)
      db.commit()
      db.refresh(nova_marcacao)
      
      return {
          "success": True,
          "subgrupo": {
              "id": nova_marcacao.id,
              "grupo": nova_marcacao.GRUPO,
              "subgrupo": nova_marcacao.SUBGRUPO
          }
      }
  ```

---

#### **3.2 Frontend - Componentes Modais** (3-4 horas)

- [ ] 3.2.1 Criar modal-novo-grupo.tsx
  ```typescript
  // src/features/upload/components/modals/modal-novo-grupo.tsx
  
  export function ModalNovoGrupo({ 
    open, 
    onOpenChange, 
    onSuccess 
  }: Props) {
    const [form, setForm] = useState({
      grupo: '',
      primeiroSubgrupo: '',
      tipoGasto: 'Variável',
      categoriaGeral: 'Despesa'
    })
    
    const handleSubmit = async (e: React.FormEvent) => {
      e.preventDefault()
      
      try {
        const response = await fetch('/api/v1/upload/classification/grupo', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            grupo: form.grupo,
            primeiro_subgrupo: form.primeiroSubgrupo,
            tipo_gasto: form.tipoGasto,
            categoria_geral: form.categoriaGeral
          })
        })
        
        const data = await response.json()
        
        if (data.success) {
          toast.success(`Grupo "${data.grupo.nome}" criado!`)
          onSuccess(data.grupo.nome, data.subgrupo.subgrupo)
          onOpenChange(false)
        }
      } catch (error) {
        toast.error("Erro ao criar grupo")
      }
    }
    
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Criar Novo Grupo</DialogTitle>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label>Nome do Grupo *</Label>
              <Input 
                value={form.grupo}
                onChange={(e) => setForm({...form, grupo: e.target.value})}
                placeholder="Ex: Lazer, Educação"
                required
              />
            </div>
            
            <div>
              <Label>Primeiro Subgrupo *</Label>
              <Input 
                value={form.primeiroSubgrupo}
                onChange={(e) => setForm({...form, primeiroSubgrupo: e.target.value})}
                placeholder="Ex: Cinema, Cursos"
                required
              />
              <p className="text-xs text-muted-foreground mt-1">
                Você pode adicionar mais subgrupos depois
              </p>
            </div>
            
            <div>
              <Label>Tipo de Gasto *</Label>
              <Select 
                value={form.tipoGasto}
                onValueChange={(v) => setForm({...form, tipoGasto: v})}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Fixo">Fixo</SelectItem>
                  <SelectItem value="Variável">Variável</SelectItem>
                  <SelectItem value="Investimento">Investimento</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>Categoria Geral *</Label>
              <Select 
                value={form.categoriaGeral}
                onValueChange={(v) => setForm({...form, categoriaGeral: v})}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Receita">Receita</SelectItem>
                  <SelectItem value="Despesa">Despesa</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <DialogFooter>
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => onOpenChange(false)}
              >
                Cancelar
              </Button>
              <Button type="submit">
                Criar Grupo
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    )
  }
  ```

- [ ] 3.2.2 Criar modal-novo-subgrupo.tsx
  ```typescript
  // src/features/upload/components/modals/modal-novo-subgrupo.tsx
  
  export function ModalNovoSubgrupo({ 
    open, 
    onOpenChange, 
    grupos,
    onSuccess 
  }: Props) {
    const [form, setForm] = useState({
      grupo: '',
      subgrupo: ''
    })
    const [showModalGrupo, setShowModalGrupo] = useState(false)
    
    const handleSubmit = async (e: React.FormEvent) => {
      e.preventDefault()
      
      try {
        const response = await fetch('/api/v1/upload/classification/subgrupo', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(form)
        })
        
        const data = await response.json()
        
        if (data.success) {
          toast.success(`Subgrupo "${data.subgrupo.subgrupo}" criado!`)
          onSuccess(data.subgrupo.grupo, data.subgrupo.subgrupo)
          onOpenChange(false)
        }
      } catch (error) {
        toast.error("Erro ao criar subgrupo")
      }
    }
    
    return (
      <>
        <Dialog open={open} onOpenChange={onOpenChange}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Criar Novo Subgrupo</DialogTitle>
            </DialogHeader>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label>Grupo *</Label>
                <div className="flex gap-2">
                  <Select 
                    value={form.grupo}
                    onValueChange={(v) => setForm({...form, grupo: v})}
                    required
                  >
                    <SelectTrigger className="flex-1">
                      <SelectValue placeholder="Selecione o grupo" />
                    </SelectTrigger>
                    <SelectContent>
                      {grupos.map(g => (
                        <SelectItem key={g} value={g}>{g}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    onClick={() => setShowModalGrupo(true)}
                    title="Criar novo grupo"
                  >
                    <PlusIcon className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              
              <div>
                <Label>Nome do Subgrupo *</Label>
                <Input 
                  value={form.subgrupo}
                  onChange={(e) => setForm({...form, subgrupo: e.target.value})}
                  placeholder="Ex: Cinema, Restaurante"
                  required
                />
              </div>
              
              <div className="text-sm text-muted-foreground">
                Este subgrupo será adicionado ao grupo "{form.grupo || '...'}"
              </div>
              
              <DialogFooter>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => onOpenChange(false)}
                >
                  Cancelar
                </Button>
                <Button type="submit" disabled={!form.grupo}>
                  Criar Subgrupo
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
        
        {/* Modal aninhado de criar grupo */}
        <ModalNovoGrupo 
          open={showModalGrupo}
          onOpenChange={setShowModalGrupo}
          onSuccess={(grupo, subgrupo) => {
            setForm({...form, grupo})
            // Atualizar lista de grupos
          }}
        />
      </>
    )
  }
  ```

- [ ] 3.2.3 Integrar modais em edit-transaction-modal.tsx
  ```typescript
  // src/features/upload/components/edit-transaction-modal.tsx
  
  export function EditTransactionModal({ transaction }: Props) {
    const [showModalGrupo, setShowModalGrupo] = useState(false)
    const [showModalSubgrupo, setShowModalSubgrupo] = useState(false)
    const [grupo, setGrupo] = useState(transaction.GRUPO)
    const [subgrupo, setSubgrupo] = useState(transaction.SUBGRUPO)
    
    return (
      <>
        <Dialog>
          <DialogContent>
            {/* ... outros campos ... */}
            
            <div>
              <Label>Grupo</Label>
              <div className="flex gap-2">
                <Select value={grupo} onValueChange={setGrupo}>
                  <SelectTrigger className="flex-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {grupos.map(g => (
                      <SelectItem key={g} value={g}>{g}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setShowModalGrupo(true)}
                >
                  <PlusIcon />
                </Button>
              </div>
            </div>
            
            <div>
              <Label>Subgrupo</Label>
              <div className="flex gap-2">
                <Select value={subgrupo} onValueChange={setSubgrupo}>
                  <SelectTrigger className="flex-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {subgrupos.map(s => (
                      <SelectItem key={s} value={s}>{s}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setShowModalSubgrupo(true)}
                >
                  <PlusIcon />
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
        
        <ModalNovoGrupo 
          open={showModalGrupo}
          onOpenChange={setShowModalGrupo}
          onSuccess={(novoGrupo, novoSubgrupo) => {
            setGrupo(novoGrupo)
            setSubgrupo(novoSubgrupo)
            // Refresh listas
          }}
        />
        
        <ModalNovoSubgrupo 
          open={showModalSubgrupo}
          onOpenChange={setShowModalSubgrupo}
          grupos={grupos}
          onSuccess={(grupoSelecionado, novoSubgrupo) => {
            setGrupo(grupoSelecionado)
            setSubgrupo(novoSubgrupo)
            // Refresh listas
          }}
        />
      </>
    )
  }
  ```

---

#### **3.3 Testes** (1-2 horas)

- [ ] 3.3.1 Testes unitários backend
  ```python
  def test_criar_grupo():
      # Criar grupo novo
      # Validar em base_grupos_config
      # Validar primeiro subgrupo em base_marcacoes
  
  def test_criar_grupo_duplicado():
      # Tentar criar grupo que já existe
      # Deve retornar 400
  
  def test_criar_subgrupo():
      # Criar subgrupo em grupo existente
      # Validar em base_marcacoes
  
  def test_criar_subgrupo_grupo_invalido():
      # Tentar criar subgrupo em grupo inexistente
      # Deve retornar 400
  ```

- [ ] 3.3.2 Testes E2E frontend
  ```bash
  # Cypress/Playwright
  # 1. Abrir modal de edição de transação
  # 2. Clicar no "+" de Grupo
  # 3. Preencher formulário de novo grupo
  # 4. Salvar
  # 5. Validar que formulário principal já vem com grupo pré-preenchido
  # 6. Repetir para Subgrupo
  ```

---

### ✅ Critérios de Aceitação Sprint 3

- [ ] ✅ 2 endpoints criados e funcionando
- [ ] ✅ 2 modais criados com UX fluida
- [ ] ✅ Modais aninhados funcionam (criar grupo dentro de criar subgrupo)
- [ ] ✅ Pré-preenchimento automático após criação
- [ ] ✅ Validações de duplicatas funcionando
- [ ] ✅ Testes unitários passando
- [ ] ✅ Testes E2E passando

---

## 🎯 Sprint 4: Validação E2E e Refinamentos

**Duração:** 1-2 dias  
**Dependência:** Sprints 1, 2 e 3 completos  
**Objetivo:** Garantir que fluxo completo funciona perfeitamente

### 📋 TODOs Detalhados

#### **4.1 Testes E2E - Onboarding Completo** (2-3 horas)

- [ ] 4.1.1 Cenário 1: Usuário novo do zero
  ```bash
  # Setup:
  # - Deletar usuário teste (se existir)
  # - Preparar arquivo de extrato
  
  # Execução:
  1. Criar novo usuário via API/frontend
  2. Login
  3. Dashboard exibe estrutura (não EmptyState)
  4. Acessar /budget
  5. Criar meta para "Alimentação" - Janeiro
  6. Criar meta para "Transporte" - Ano todo
  7. Validar 12 meses salvos
  8. Acessar /upload
  9. Fazer upload de extrato
  10. Preview exibe transações
  11. Classificar 1 transação manualmente
  12. Criar novo grupo via botão "+"
  13. Confirmar upload
  14. Dashboard exibe transações
  15. Comparação meta vs real funcionando
  ```

- [ ] 4.1.2 Cenário 2: Segundo upload (duplicatas)
  ```bash
  1. Fazer segundo upload do mesmo arquivo
  2. Preview exibe duplicatas marcadas
  3. Confirmar → apenas não-duplicatas importadas
  4. Dashboard não tem duplicatas
  ```

- [ ] 4.1.3 Cenário 3: Upload fatura sem cartão
  ```bash
  1. Deletar cartão padrão
  2. Tentar upload de fatura
  3. DEVE funcionar com cartão padrão (criado no Sprint 2)
  ```

---

#### **4.2 Performance e Otimizações** (1-2 horas)

- [ ] 4.2.1 Medir tempo de criação de usuário
  ```python
  # Deve ser < 500ms
  import time
  start = time.time()
  user = create_user(...)
  elapsed = time.time() - start
  assert elapsed < 0.5, f"Criação demorou {elapsed}s"
  ```

- [ ] 4.2.2 Otimizar queries se necessário
  ```python
  # Bulk inserts em vez de loops
  # Usar session.bulk_save_objects() para budget_planning
  ```

- [ ] 4.2.3 Adicionar índices se necessário
  ```sql
  CREATE INDEX idx_budget_planning_user_ano_mes 
  ON budget_planning(user_id, ano, mes);
  
  CREATE INDEX idx_base_marcacoes_grupo_subgrupo
  ON base_marcacoes(user_id, GRUPO, SUBGRUPO);
  ```

---

#### **4.3 Documentação e UX** (1 hora)

- [ ] 4.3.1 Adicionar tooltips
  ```tsx
  <Button 
    onClick={...}
    title="Criar novo grupo"  // ← Tooltip
  >
    <PlusIcon />
  </Button>
  ```

- [ ] 4.3.2 Adicionar loading states
  ```tsx
  const [loading, setLoading] = useState(false)
  
  <Button disabled={loading}>
    {loading ? <Spinner /> : 'Criar Grupo'}
  </Button>
  ```

- [ ] 4.3.3 Melhorar mensagens de erro
  ```typescript
  if (error.status === 400) {
    toast.error(error.detail)  // Mensagem do backend
  } else {
    toast.error("Erro inesperado. Tente novamente.")
  }
  ```

- [ ] 4.3.4 Atualizar documentação de usuário
  ```markdown
  # Guia: Criar Seu Primeiro Grupo
  
  1. Durante a edição de uma transação...
  2. Clique no botão "+" ao lado do campo Grupo
  3. Preencha o formulário...
  4. O novo grupo já ficará selecionado!
  ```

---

#### **4.4 Refinamentos Finais** (1 hora)

- [ ] 4.4.1 Code review completo
  - [ ] Backend: models, services, routers
  - [ ] Frontend: componentes, hooks, types
  - [ ] Testes: cobertura adequada

- [ ] 4.4.2 Ajustes de UX baseados em testes
  - [ ] Animações suaves nos modais
  - [ ] Feedback visual de sucesso
  - [ ] Validações em tempo real

- [ ] 4.4.3 Logs e monitoramento
  ```python
  # Adicionar logs estruturados
  logger.info(
      "Usuário criado com dados default",
      extra={
          "user_id": user.id,
          "budget_records": stats['budget_planning'],
          "cards_created": stats['cartoes']
      }
  )
  ```

---

### ✅ Critérios de Aceitação Sprint 4

- [ ] ✅ Fluxo E2E completo testado e funcionando
- [ ] ✅ Performance adequada (< 500ms para criar usuário)
- [ ] ✅ Zero bugs críticos
- [ ] ✅ UX refinada (tooltips, loading, erros claros)
- [ ] ✅ Documentação atualizada
- [ ] ✅ Code review aprovado
- [ ] ✅ Pronto para deploy em produção

---

## 📊 Resumo de Entregas

| Sprint | Entregável | Impacto |
|--------|-----------|---------|
| **Sprint 1** | Budget consolidado (3→1 tabelas) | 🔴 Arquitetura 75% mais simples |
| **Sprint 2** | Auto-criação de dados (~30 registros) | 🟡 Onboarding funcional |
| **Sprint 3** | Criação de grupos na UI | 🟡 UX fluida no upload |
| **Sprint 4** | Validação E2E completa | 🟢 Qualidade garantida |

**Total de entregas:** 4 funcionalidades críticas implementadas

---

## 🚨 Riscos e Mitigações

### Risco 1: Migration falha em produção
**Probabilidade:** Média  
**Impacto:** Alto  
**Mitigação:**
- Backup completo antes da migration
- Testar em staging idêntico a produção
- Preparar rollback script
- Executar em horário de baixo tráfego

### Risco 2: Performance degrada com auto-criação
**Probabilidade:** Baixa  
**Impacto:** Médio  
**Mitigação:**
- Usar bulk inserts
- Adicionar índices
- Executar async em background
- Monitorar tempo de resposta

### Risco 3: Modais aninhados causam bugs de state
**Probabilidade:** Média  
**Impacto:** Baixo  
**Mitigação:**
- Usar context API para gerenciar state
- Testes E2E extensivos
- Code review focado em state management

---

## 📝 Checklist Final

### Antes de Iniciar
- [ ] ✅ Todas as documentações lidas
- [ ] ✅ Ambiente de desenvolvimento configurado
- [ ] ✅ Branch main atualizada
- [ ] ✅ Backups do banco criados

### Após Cada Sprint
- [ ] ✅ Testes unitários passando
- [ ] ✅ Testes E2E passando
- [ ] ✅ Code review aprovado
- [ ] ✅ Documentação atualizada
- [ ] ✅ CHANGELOG.md atualizado
- [ ] ✅ PR mergeado

### Antes do Deploy Final
- [ ] ✅ Todos os 4 sprints completos
- [ ] ✅ Validação E2E em staging
- [ ] ✅ Performance validada
- [ ] ✅ Backup de produção criado
- [ ] ✅ Plano de rollback pronto
- [ ] ✅ Stakeholders notificados

---

## 🎯 Próximos Passos Imediatos

1. **Revisar este plano** com time/stakeholders
2. **Criar branch** `feature/fase5-implementacao`
3. **Iniciar Sprint 1** - Consolidação Budget
4. **Daily standup** para acompanhar progresso
5. **Deploy incremental** após cada sprint (se possível)

---

**Criado em:** 13/02/2026  
**Responsável:** A definir  
**Status:** 📋 Aguardando aprovação para início
