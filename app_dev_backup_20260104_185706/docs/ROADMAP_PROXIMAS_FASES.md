# 🗺️ ROADMAP - Próximas Fases do Projeto

**Sistema de Finanças - Arquitetura Mista (FastAPI + Next.js)**

---

## ✅ FASE 1 - CONCLUÍDA (Jan 2026)

### Frontend Base
- ✅ Login e autenticação JWT
- ✅ Dashboard com métricas, gráficos e transações
- ✅ Página de configurações (categorias, bancos, API docs)
- ✅ Página de upload de arquivos
- ✅ **Tela de confirmação de upload** (validação pré-salvamento)
- ✅ Componentes shadcn/ui integrados
- ✅ Tailwind CSS estilizado

### Backend Base
- ✅ API FastAPI com documentação Swagger/ReDoc
- ✅ JWT authentication (compatível com Werkzeug e bcrypt)
- ✅ Endpoints de dashboard (métricas, categorias, gráficos)
- ✅ CRUD de marcações (base_marcacoes)
- ✅ Compatibilidade de bancos (bank_format_compatibility)
- ✅ SQLAlchemy ORM com SQLite

---

## 🚀 FASE 2 - UPLOAD E PROCESSAMENTO (Próxima)

### 2.1 Backend - Endpoints de Upload
**Prioridade:** ALTA

#### Criar Routers
```python
# app/routers/upload.py
@router.post("/upload")
async def upload_file(
    file: UploadFile,
    bank: str,
    type: str,  # 'fatura' ou 'extrato'
    credit_card: Optional[str] = None
) -> UploadSessionResponse

@router.get("/upload/session/{session_id}")
async def get_upload_session(session_id: str) -> UploadSessionDetail

@router.post("/upload/confirm/{session_id}")
async def confirm_upload(
    session_id: str,
    selected_transactions: List[int]
) -> ConfirmResponse
```

#### Funcionalidades
- [ ] Receber arquivo (CSV, XLS, XLSX, PDF, OFX)
- [ ] Salvar temporariamente em `uploads_temp/`
- [ ] Criar sessão com UUID único
- [ ] Armazenar metadados da sessão (Redis ou tabela temp)
- [ ] Retornar sessionId para frontend

**Tempo estimado:** 2-3 horas

---

### 2.2 Migração de Preprocessadores
**Prioridade:** ALTA

#### Arquivos a Migrar
```
De: /app/utils/processors/preprocessors/
Para: /app_dev/backend/app/processors/

Arquivos:
- itau_preprocessor.py
- btg_preprocessor.py  
- bb_preprocessor.py
- mercado_pago_preprocessor.py
- detect_and_preprocess.py (main)
```

#### Adaptações Necessárias
- [ ] Converter imports Flask → FastAPI
- [ ] Adaptar leitura de arquivos para UploadFile
- [ ] Testar com arquivos históricos em `_csvs_historico/`
- [ ] Validar detecção automática de banco
- [ ] Garantir compatibilidade de encoding (UTF-8, ISO-8859-1)

**Tempo estimado:** 3-4 horas

---

### 2.3 Migração de Processadores
**Prioridade:** ALTA

#### Arquivos a Migrar
```
De: /app/blueprints/upload/processors/
Para: /app_dev/backend/app/processors/

Arquivos:
- fatura_cartao.py (processar_fatura_cartao)
- extrato_conta.py (processar_extrato_conta)
- base_parcelas.py (atualizar_base_parcelas)
```

#### Funcionalidades
- [ ] Processar DataFrame preprocessado
- [ ] Gerar hash IdTransacao (FNV-1a 64-bit)
- [ ] Aplicar regras de negócio (tipos, categorias)
- [ ] Normalizar estabelecimentos
- [ ] Calcular parcelas (IdParcela)
- [ ] Retornar lista de transações processadas

**Tempo estimado:** 4-5 horas

---

### 2.4 Deduplicação e Validação
**Prioridade:** MÉDIA

#### Detectar Duplicatas
```python
async def check_duplicates(
    transactions: List[Transaction],
    db: Session
) -> List[DuplicateInfo]
```

**Critérios:**
- Comparar IdTransacao com journal_entries existentes
- Verificar duplicatas no mesmo arquivo (hash)
- Flagear transações idênticas (Data + Estabelecimento + Valor)

#### Validar Integridade
- [ ] Estabelecimentos não reconhecidos
- [ ] Valores extremos (outliers)
- [ ] Datas inválidas
- [ ] Parcelas incompletas
- [ ] Categorias ausentes

**Tempo estimado:** 2-3 horas

---

### 2.5 Frontend - Integração Upload Completo
**Prioridade:** MÉDIA

#### Atualizar Upload Dialog
```typescript
// src/components/upload-dialog.tsx
const response = await uploadAPI.uploadFile(formData);
router.push(`/upload/confirm?session=${response.sessionId}`);
```

#### Página de Confirmação
- [ ] Buscar transações da sessão via API
- [ ] Exibir tabela com flags (duplicata, problema, ok)
- [ ] Permitir edição manual inline ou via modal
- [ ] Filtros: Todas, Duplicatas, Problemas
- [ ] Seleção individual e em massa
- [ ] Botão "Salvar X Transações"

**Tempo estimado:** 2 horas

---

## 🤖 FASE 3 - CLASSIFICAÇÃO AUTOMÁTICA (IA)

### 3.1 Migração de Classifiers
**Prioridade:** MÉDIA

#### Arquivos a Migrar
```
De: /app/blueprints/upload/classifiers/
Para: /app_dev/backend/app/classifiers/

Arquivos:
- classificador_regex.py
- classificador_ml.py (se existir)
- classificar_transacoes.py (main)
```

#### Funcionalidades
- [ ] Carregar base de padrões (base_marcacoes)
- [ ] Regex matching (estabelecimentos conhecidos)
- [ ] Score de confiança (0-100%)
- [ ] Classificação por categoria/grupo/subgrupo
- [ ] Marcação de origem: "IA", "Manual", "Manual (Lote)"

**Tempo estimado:** 3-4 horas

---

### 3.2 Base de Aprendizado
**Prioridade:** BAIXA

#### Machine Learning (Opcional - Futuro)
- [ ] Coletar histórico de correções manuais
- [ ] Treinar modelo simples (Naive Bayes ou Random Forest)
- [ ] Melhorar score de predição com uso
- [ ] Sugestões inteligentes baseadas em padrões

**Tempo estimado:** 8-12 horas (FUTURO)

---

## 📊 FASE 4 - TRANSAÇÕES E PARCELAS

### 4.1 CRUD de Transações
**Prioridade:** ALTA

#### Backend Endpoints
```python
# app/routers/transactions.py
@router.get("/transactions")  # Listar com filtros
@router.get("/transactions/{id}")  # Detalhes
@router.put("/transactions/{id}")  # Editar
@router.delete("/transactions/{id}")  # Deletar
@router.patch("/transactions/{id}/category")  # Reclassificar
```

#### Frontend
- [ ] Tabela de transações com paginação
- [ ] Filtros avançados (data, categoria, banco, valor)
- [ ] Edição inline ou modal
- [ ] Confirmação de exclusão
- [ ] Busca por texto (estabelecimento)

**Tempo estimado:** 4-5 horas

---

### 4.2 Sistema de Parcelas
**Prioridade:** MÉDIA

#### Auto-sync de Parcelas
```python
# app/services/parcelas_service.py
async def sync_parcelas(transactions: List[Transaction]):
    # 1. Detectar transações parceladas (IdParcela)
    # 2. Atualizar base_parcelas
    # 3. Vincular parcelas relacionadas
    # 4. Calcular status (pagas, pendentes)
```

#### Frontend - Visualização
- [ ] Card de parcelas na dashboard
- [ ] Listagem agrupada por compra original
- [ ] Indicador de progresso (3/12 pagas)
- [ ] Filtro de parcelas pendentes

**Tempo estimado:** 3-4 horas

---

## 🔍 FASE 5 - ANÁLISES E RELATÓRIOS

### 5.1 Relatórios Avançados
**Prioridade:** BAIXA

#### Backend Endpoints
```python
@router.get("/reports/monthly")  # Resumo mensal
@router.get("/reports/category-trends")  # Tendências
@router.get("/reports/comparison")  # Comparativo períodos
@router.get("/reports/export")  # PDF ou Excel
```

#### Frontend
- [ ] Página de relatórios
- [ ] Gráficos interativos (Recharts)
- [ ] Comparação mês a mês
- [ ] Top gastos por categoria
- [ ] Exportação PDF

**Tempo estimado:** 6-8 horas

---

### 5.2 Metas e Orçamentos
**Prioridade:** BAIXA

#### Funcionalidades
- [ ] Definir metas mensais por categoria
- [ ] Alertas de orçamento excedido
- [ ] Progresso visual (progress bars)
- [ ] Notificações no dashboard

**Tempo estimado:** 4-5 horas

---

## 🔐 FASE 6 - SEGURANÇA E MULTI-USUÁRIO

### 6.1 Gestão de Usuários
**Prioridade:** MÉDIA (se compartilhar sistema)

#### Backend
```python
@router.post("/users")  # Criar usuário
@router.get("/users/me")  # Perfil atual
@router.put("/users/me")  # Atualizar perfil
@router.post("/users/change-password")  # Trocar senha
```

#### Frontend
- [ ] Página de perfil
- [ ] Alteração de senha
- [ ] Preferências (tema, idioma)

**Tempo estimado:** 3-4 horas

---

### 6.2 Permissões e Roles
**Prioridade:** BAIXA

#### Roles
- Admin: Acesso total
- User: Acesso às próprias transações
- Viewer: Apenas leitura

#### Implementação
- [ ] Middleware de autorização
- [ ] Filtros por user_id em queries
- [ ] Proteção de rotas sensíveis

**Tempo estimado:** 2-3 horas

---

## 🚀 FASE 7 - DEPLOY E OTIMIZAÇÃO

### 7.1 Deploy Backend
**Prioridade:** ALTA (quando pronto para produção)

#### Opções de Hospedagem
- **Railway.app** (fácil, grátis)
- **Render.com** (grátis com limites)
- **DigitalOcean** ($5/mês)
- **AWS EC2** ($10-20/mês)

#### Checklist
- [ ] Configurar variáveis de ambiente
- [ ] Migrar para PostgreSQL (opcional)
- [ ] Configurar HTTPS
- [ ] Backup automático do banco
- [ ] Monitoramento (Sentry, Datadog)

**Tempo estimado:** 4-6 horas

---

### 7.2 Deploy Frontend
**Prioridade:** ALTA

#### Opção: Vercel (Recomendado)
- [ ] Deploy automático via GitHub
- [ ] Configurar variáveis de ambiente
- [ ] Apontar para backend em produção
- [ ] Domínio customizado (opcional)

**Tempo estimado:** 1-2 horas

---

### 7.3 Otimizações
**Prioridade:** BAIXA

#### Performance
- [ ] Cache de queries frequentes (Redis)
- [ ] Paginação server-side
- [ ] Lazy loading de componentes
- [ ] Compressão de assets
- [ ] CDN para imagens

#### Qualidade
- [ ] Testes unitários (pytest)
- [ ] Testes de integração (frontend)
- [ ] CI/CD com GitHub Actions
- [ ] Code coverage >80%

**Tempo estimado:** 10-15 horas

---

## 📝 PRIORIZAÇÃO SUGERIDA

### Próximos Passos Imediatos (Esta Semana)
1. **FASE 2.1** - Endpoints de upload (2-3h)
2. **FASE 2.2** - Migrar preprocessadores (3-4h)
3. **FASE 2.3** - Migrar processadores (4-5h)
4. **FASE 2.4** - Deduplicação (2-3h)
5. **FASE 2.5** - Integrar frontend (2h)

**Total estimado:** 13-17 horas de desenvolvimento

---

### Curto Prazo (Próximas 2 Semanas)
- FASE 3 - Classificação IA
- FASE 4.1 - CRUD de transações

---

### Médio Prazo (Próximo Mês)
- FASE 4.2 - Sistema de parcelas
- FASE 5 - Relatórios

---

### Longo Prazo (Próximos 3 Meses)
- FASE 6 - Multi-usuário
- FASE 7 - Deploy e otimizações

---

## 🎯 META PRINCIPAL

**Ter sistema 100% funcional de upload até final de Janeiro 2026:**
- ✅ Upload de arquivos
- ✅ Preprocessamento automático
- ✅ Classificação IA
- ✅ Deduplicação
- ✅ Validação e confirmação
- ✅ Salvamento no banco

---

## 📌 OBSERVAÇÕES IMPORTANTES

### Manter Compatibilidade
- ✅ Sistema Flask original (`/app`) continua funcionando
- ✅ Banco de dados compartilhado entre versões
- ✅ Migração gradual de funcionalidades

### Validação Pré-Deploy
- ✅ **SEMPRE** executar `./scripts/pre_deploy_validation.sh`
- ✅ Validar com arquivos históricos (`_csvs_historico/`)
- ✅ Critério: ≥95% de match com dados existentes

### Versionamento
- ✅ Seguir `CONTRIBUTING.md` para mudanças em arquivos críticos
- ✅ Usar `version_manager.py` para rastreabilidade
- ✅ Documentar em `changes/` antes de commit

---

**Última atualização:** 03/01/2026  
**Versão:** 1.0.0
