# PRD — Upload Completo
> Sub-projeto 04 | Sprints 3, 3.5, 4, 5 | ~32h  
> Dependência: Sub-projeto 03 (grupos padrão existem antes do primeiro upload)

---

## 1. Problema

O upload atual exige que o usuário saiba exatamente qual banco, qual tipo de arquivo (extrato vs. fatura) e qual período está carregando. Isso gera erros silenciosos, duplicatas, e impossibilidade de desfazer importações equivocadas. Além disso, só aceita 1 arquivo por vez e não tem suporte a planilhas genéricas.

---

## 2. Objetivo

Tornar o upload de dados financeiros **inteligente, reversível e flexível**: detectar automaticamente o arquivo, aceitar múltiplos arquivos de uma vez, classificar transações em lote, alertar duplicatas, e permitir desfazer qualquer importação com rollback completo.

---

## 3. Escopo (IN)

| ID | Feature | Sprint |
|----|---------|--------|
| S20 | Detecção automática de banco/tipo/período | 3 |
| S30 | Alerta de arquivo duplicado | 3 |
| S31 | Rollback de upload | 3.5 |
| S21 | Drop zone multi-arquivo | 4 |
| S22 | Classificação em lote por estabelecimento | 4 |
| S23 | Importação de planilha genérica (CSV/XLS) | 5 |

---

## 4. Escopo (OUT)

- OCR de PDFs de fatura (future)
- Integração Open Banking direta
- Upload por e-mail / SFTP
- Sincronização automática de contas

---

## 5. Dependências de Outros Sub-projetos

| Dep | Motivo |
|-----|--------|
| **03-onboarding-grupos** (HARD) | Grupos padrão devem existir antes do primeiro upload para que a classificação automática funcione |
| **01-admin** (soft) | Se upload for testado com usuário demo, o init de grupos deve rodar antes |

---

## 6. User Stories

### S20 — Detecção automática de banco/tipo/período

**Como** usuário,  
**Quero** que o sistema identifique automaticamente qual banco, qual tipo (extrato/fatura), e qual período o arquivo representa,  
**Para que** eu não precise preencher esses campos manualmente.

**Acceptance Criteria:**
- [ ] Ao selecionar um arquivo, o sistema retorna `banco`, `tipo`, `período_início`, `período_fim`, `confiança` (0-1)
- [ ] Se `confiança < 0.6`, campos ficam editáveis com valor detectado como sugestão
- [ ] Se `confiança >= 0.6`, campos são preenchidos automaticamente mas ainda editáveis
- [ ] Suporta: Nubank CSV, Itaú XLS, BTG CSV, BB OFX, MercadoPago CSV, Fatura genérica CSV
- [ ] Tempo de detecção < 2 segundos

### S30 — Alerta de arquivo duplicado

**Como** usuário,  
**Quero** ser avisado quando o arquivo que estou tentando carregar já foi importado antes,  
**Para que** eu não duplique transações acidentalmente.

**Acceptance Criteria:**
- [ ] Na etapa de detecção, o backend verifica se já existe `UploadHistory` com mesmo `banco + tipo + período`
- [ ] Se duplicata detectada: modal de aviso com data da importação anterior + contagem de transações
- [ ] Opções: "Cancelar" ou "Carregar de qualquer forma"
- [ ] Se usuário confirmar carga duplicada, registro é criado com flag `is_duplicate_warning = true`

### S31 — Rollback de upload

**Como** usuário,  
**Quero** poder desfazer uma importação específica,  
**Para que** eu possa corrigir erros de importação sem precisar apagar registros manualmente.

**Acceptance Criteria:**
- [ ] Tela "Meus Uploads" lista todos os uploads com data, banco, tipo, período, nº de transações
- [ ] Ao clicar em "Desfazer": preview mostra exatamente o que será removido (tx, marcações, parcelas, vínculos de investimento)
- [ ] Confirmação explícita antes de executar
- [ ] Rollback em transação atômica: ou tudo é removido, ou nada
- [ ] Se upload tiver transação vinculada a investimento: aviso especial no preview ("⚠️ N transações possuem vínculos de investimento")
- [ ] Após rollback: saldo e dashboard atualizam automaticamente

### S21 — Drop zone multi-arquivo

**Como** usuário,  
**Quero** arrastar múltiplos arquivos de uma vez para o upload,  
**Para que** eu possa carregar vários bancos/períodos sem repetir o fluxo.

**Acceptance Criteria:**
- [ ] Drop zone aceita N arquivos simultaneamente (limite: 10 arquivos/batch)
- [ ] Cada arquivo passa pela detecção em paralelo
- [ ] Card individual por arquivo com: nome, banco detectado, tipo, período, status (detectando → ok / erro)
- [ ] Campos banco/tipo/período editáveis por arquivo
- [ ] Botão "Importar todos" quando todos os arquivos estão prontos
- [ ] Progresso por arquivo durante importação
- [ ] Se algum arquivo falhar: os outros continuam; erro exibido no card

### S22 — Classificação em lote por estabelecimento

**Como** usuário,  
**Quero** ver todas as transações agrupadas por estabelecimento para classificar de uma vez,  
**Para que** eu não precise classificar transação por transação.

**Acceptance Criteria:**
- [ ] Após detecção, tela de revisão agrupa transações por `estabelecimento_base`
- [ ] Para cada grupo: nome do estabelecimento, contagem de ocorrências, valor total
- [ ] Se estabelecimento já foi classificado antes: preenche `grupo` automaticamente
- [ ] Estabelecimentos novos: dropdown de grupo + campo de busca
- [ ] "Aplicar para todas as ocorrências" por padrão (checkbox desmarcável)
- [ ] Botão "Salvar classificação e importar"

### S23 — Importação de planilha genérica

**Como** usuário que exporta dados de um banco não suportado,  
**Quero** importar um CSV/XLS com formato mínimo padronizado,  
**Para que** eu consiga registrar transações de qualquer banco.

**Acceptance Criteria:**
- [ ] Colunas obrigatórias: `Data` (DD/MM/YYYY), `Descrição`, `Valor` (negativo = débito, positivo = crédito)
- [ ] Colunas opcionais: `Banco`, `Tipo`, `Grupo`
- [ ] Se coluna faltante: mensagem clara indicando quais colunas estão ausentes
- [ ] Preview de 5 primeiras linhas com mapeamento de colunas
- [ ] Estabelecimentos não classificados vão para fluxo S22 (classificação em lote)
- [ ] Endpoint `POST /upload/import-planilha` + `POST /upload/confirmar`

---

## 7. UX / Wireframes

### Fluxo de Upload (após S20+S21)

```
[Botão Upload / FAB] → [Drop Zone] → [Detecção automática por arquivo]
        ↓
[FileDetectionCard × N]
  ├── banco: [Nubank ▼]  tipo: [Extrato ▼]  período: [Nov 2025 - Dez 2025]
  ├── ⚠️ "Já importado em 15/01" → [Cancelar | Carregar mesmo assim]
  └── status: ✅ Pronto / ❌ Erro de detecção
        ↓
[Classificação em lote — Estabelecimentos novos]
        ↓
[Resumo: X transações × Y arquivos] → [Importar tudo]
        ↓
[Tela "Meus Uploads" com histórico + botão Desfazer]
```

### Tela "Meus Uploads"

```
┌────────────────────────────────────────────────────────┐
│ 📁 Meus Uploads                                         │
├────────────────────────────────────────────────────────┤
│ Nubank Extrato — Nov 2025   47 tx   15/01/2026  [↩️ Desfazer] │
│ Itaú Fatura   — Out 2025   32 tx   10/01/2026  [↩️ Desfazer] │
│ BTG Extrato   — Nov 2025   18 tx   08/01/2026  [↩️ Desfazer] │
└────────────────────────────────────────────────────────┘
```

### RollbackPreviewModal

```
┌──────────────────────────────────────────┐
│ ↩️ Desfazer importação                    │
│ Nubank Extrato — Nov 2025                │
├──────────────────────────────────────────┤
│ Serão removidos:                         │
│  • 47 transações                         │
│  • 12 marcações associadas               │
│  • 3 parcelas associadas                 │
│                                          │
│ ⚠️ 2 transações têm vínculo de           │
│    investimento — vínculos serão         │
│    desfeitos junto.                      │
├──────────────────────────────────────────┤
│ [Cancelar]          [Confirmar remoção]  │
└──────────────────────────────────────────┘
```

---

## 8. Riscos

| Risco | Probabilidade | Mitigação |
|-------|--------------|-----------|
| Processador existente não retorna fingerprint suficiente | Médio | Fallback: usuário preenche manualmente |
| Rollback parcial se FK quebrar | Baixo | Ordem garantida na transação atômica |
| Multi-arquivo com arquivos conflitantes (mesmo período) | Médio | Detectar por S30 e exibir aviso por arquivo |
| Planilha com formato inesperado | Alto | Validação de colunas antes de processar |

---

## 9. Métricas de Sucesso

| Métrica | Meta |
|---------|------|
| Taxa de detecção automática correta (sem edição) | > 85% dos uploads |
| Uploads com rollback usados | < 5% (indica uploads errados) |
| Adoção do multi-arquivo | > 40% dos uploads em 3 meses |
| Tempo médio do fluxo de upload | < 90 segundos (multi-arquivo incluído) |
