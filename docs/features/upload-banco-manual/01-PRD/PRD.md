# 📋 PRD - Upload com Seleção Manual de Banco

**Status:** 🟡 Em Construção  
**Versão:** 0.1 (rascunho)  
**Data:** 21/03/2026  
**Autor:** Emanuel  
**Stakeholders:** Emanuel (PO + Dev)

---

## 📊 Sumário Executivo

**O que:** Remover completamente a detecção automática de banco do fluxo de upload e substituir por seleção manual obrigatória.  
**Por quê:** A detecção automática falha para vários arquivos (ex: BTG XLS → retorna "Planilha genérica"), criando um bypass que perde banco e tipo_documento, quebrando a deduplicação. A complexidade de manter e melhorar o auto-detect não compensa o benefício atual.  
**Para quem:** Qualquer usuário que importe arquivos bancários.  
**ROI:** Deduplicação funcionando = zero transações duplicadas = dados financeiros confiáveis.  
**Decisão:** Auto-detect removido completamente agora. Poderá ser reintroduzido no futuro como feature separada, quando tiver cobertura robusta para todos os formatos.

---

## 🎯 1. Contexto e Problema

### 1.1 Situação Atual

O upload funciona assim:

```
1. Usuário escolhe arquivo
2. Frontend chama /upload/detect (auto-detect)
3a. Se banco detectado ≠ generico → pré-preenche banco/período
3b. Se banco = generico → mostra FileDetectionCard com botão "Importar planilha"
4b. Usuário clica "Importar planilha" → chama /upload/importar-planilha
5b. Backend salva banco="Planilha genérica", tipo_documento=NULL
→ journal_entries.banco_origem = "Extrato_2025-12-10_...xls" (filename!)
```

### 1.2 Problema a Resolver

**Problema raiz:** O `fingerprints.py` não consegue identificar arquivos BTG XLS por conteúdo porque o arquivo não contém palavras como "btg" ou "pactual" no corpo — apenas no nome. O fallback resulta em `banco="generico"`.

Quando o usuário clica em "Importar planilha" para contornar, o fluxo especial:
- **Não passa banco** → `banco_origem` no `journal_entries` fica como o *filename*
- **Não passa tipo_documento** → coluna fica NULL
- **Inviabiliza a deduplicação** → dois uploads do mesmo arquivo geram `IdTransacao` completamente diferentes

**Evidência coletada (21/03/2026):**

| Campo | Upload Jan/2025 | Upload Dez/2025 (sessão ativa) |
|-------|-----------------|-------------------------------|
| `banco_origem` | `Extrato_2025-11-20_a_2026-01-18_...xls` | `Extrato_2025-12-10_a_2026-03-09_...xls` |
| `tipodocumento` | NULL | NULL |
| `Estabelecimento` | `Salário - Pagamento recebido` | `Salário - Portabilidade de salário - Pagamento recebido` |
| `IdTransacao` | `3033027455298180257` | `12688721295696874454` |
| **Dedup funciona?** | ❌ IDs diferentes | ❌ Não detecta como duplicata |

Mesmo valor (`R$ 10.520,01`), mesma data (`29/12/2025`), **mas banco e descrição inconsistentes entre exports do mesmo banco** → hashes impossíveis de coincidir.

**Impacto do Problema:**
- 🔴 **Crítico:** Deduplicação não funciona — usuário importa as mesmas transações múltiplas vezes sem aviso
- 🔴 **Crítico:** `banco_origem` fica como filename → impossível agrupar por banco nas análises
- 🟡 **Médio:** UX confusa — usuário não entende por que vê "Todas (65)" sem aba "Já Importadas"
- 🟡 **Médio:** `tipo_documento` NULL quebra lógica de extrato vs fatura em vários pontos

### 1.3 Por que a seleção manual resolve

Se o banco é passado explicitamente pelo usuário:
- `banco_origem` = `"BTG"` sempre (consistente entre uploads)
- O processador correto (`btg_extrato`) é invocado
- A descrição da transação continua variando entre exports, mas isso é problema separado (ver seção 9.3)

> **Nota:** A inconsistência de descrição (`"Salário - Pagamento recebido"` vs `"Salário - Portabilidade..."`) é um problema de *extração do arquivo pelo banco BTG*, não do nosso sistema. A seleção manual do banco não resolve esse problema específico. Ele exigiria que o `IdTransacao` seja baseado em banco + tipo + data + valor (sem nome), o que é decisão separada documentada na investigação de 21/03/2026.

---

## 🎯 2. Objetivos

### 2.1 Objetivo Principal
Garantir que **banco** e **tipo_documento** sejam sempre explicitamente definidos em todo upload, eliminando qualquer caminho automático que os perca.

### 2.2 Objetivos Secundários
1. Simplificar o código de upload (remover detection state, FileDetectionCard, importPlanilhaFile)
2. Unificar em um único fluxo linear e previsível
3. Preparar base para futura mudança do algoritmo de `IdTransacao` (banco+tipo+data+valor)

---

## 👥 3. User Stories

#### **US-01: Upload com banco selecionado manualmente**
**Como** usuário que importa extrato BTG  
**Quero** selecionar "BTG" no dropdown mesmo que o auto-detect retorne "Planilha genérica"  
**Para** que o sistema saiba o banco correto e a deduplicação funcione

**Acceptance Criteria:**
- [ ] O dropdown de banco está sempre visível e selecionável, independente do resultado do auto-detect
- [ ] O auto-detect pré-preenche o banco como *sugestão* — usuário pode alterar
- [ ] Quando a detecção retorna "generico", o sistema NÃO mostra botão "Importar planilha" que bypassa o fluxo
- [ ] O botão "Importar Arquivo" só fica ativo após banco selecionado
- [ ] `banco_origem` no banco de dados é sempre o nome do banco (ex: "BTG"), nunca o filename

**Prioridade:** 🔴 Alta

---

#### **US-02: Feedback claro quando banco não for detectado**
**Como** usuário que enviou um arquivo não reconhecido  
**Quero** ver uma mensagem explicando que o banco não foi detectado automaticamente e que devo selecionar manualmente  
**Para** entender o que fazer sem ficar preso na tela

**Acceptance Criteria:**
- [ ] Quando auto-detect retorna "generico", mostrar aviso inline: "Não conseguimos identificar o banco automaticamente. Selecione abaixo."
- [ ] O aviso NÃO bloqueia o fluxo — usuário seleciona banco e prossegue normalmente
- [ ] Não existe mais um path alternativo de "importar como planilha genérica" para arquivos bancários

**Prioridade:** 🔴 Alta

---

#### **US-03: Tipo de documento sempre definido**
**Como** sistema  
**Quero** que `tipo_documento` nunca seja NULL em `journal_entries`  
**Para** que a lógica de extrato vs fatura funcione corretamente

**Acceptance Criteria:**
- [ ] Se usuário selecionou aba "Extrato Bancário" → `tipo_documento = "extrato"`
- [ ] Se usuário selecionou aba "Fatura Cartão" → `tipo_documento = "fatura"`
- [ ] Sem exceções — não existe upload sem tipo definido

**Prioridade:** 🔴 Alta

---

## 📋 4. Requisitos Funcionais

### 4.1 Frontend — Tela de Upload (`/mobile/upload/page.tsx`)

**RF-01: Remover auto-detect completamente**
- **Removido:** Chamada ao `detectFile()` (`POST /upload/detect`) ao selecionar arquivo
- **Removido:** Estado `detection`, `detecting`, `importingPlanilha` da página
- **Removido:** Componente `FileDetectionCard` da página de upload
- **Removido:** Função `importPlanilhaFile` e botão "Importar planilha"
- **Resultado:** Ao selecionar arquivo, apenas `fileName` e `selectedFormat` são atualizados. Sem chamada de rede.
- **Prioridade:** Must Have

**RF-02: Fluxo linear simples**
- Usuário: escolhe arquivo → seleciona banco → seleciona tipo (extrato/fatura) → preenche campos → clica Importar
- Sem ramificações, sem detecção, sem estados intermediários de "detectando"
- **Prioridade:** Must Have

**RF-03: Banco obrigatório antes de habilitar "Importar Arquivo"**
- O botão "Importar Arquivo" só é habilitado quando banco estiver selecionado (já é assim, confirmar que continua)
- **Prioridade:** Must Have

**RF-04: Tab extrato/fatura determina tipo_documento**
- A seleção da tab (`activeTab`) deve sempre ser transmitida ao backend como `tipoDocumento`
- Atualmente `tipoDocumento` vem de `activeTab` na chamada `upload()` — confirmar que não existe path que ignora isso
- **Prioridade:** Must Have

### 4.2 Backend

**RF-10: Remover ou restringir `/upload/importar-planilha`**
- O endpoint especial que bypassa banco/tipo deve ser removido ou modificado para exigir banco e tipo_documento obrigatoriamente
- **Prioridade:** Must Have

**RF-11: Validação de banco e tipo_documento no `/upload/preview`**
- Rejeitar (400) se `banco` for vazio, null ou "generico" ao chamar preview
- Rejeitar (400) se `tipoDocumento` for vazio ou null
- **Prioridade:** Must Have

---

## 📐 5. Wireframes

### 5.1 Fluxo Atual (COM problema)

```
[Usuário escolhe arquivo BTG XLS]
         ↓
[Auto-detect retorna: banco="generico", tipo="planilha"]
         ↓
[FileDetectionCard aparece com CTA "Importar planilha"]
         ↓
[Usuário clica "Importar planilha"]
         ↓
[/upload/importar-planilha → banco="Planilha genérica", tipo=NULL]
         ↓
[journal_entries.banco_origem = filename 💥]
[Dedup quebrado 💥]
```

### 5.2 Fluxo Proposto (SEM auto-detect)

```
[Usuário escolhe arquivo BTG XLS]
         ↓
[Apenas: fileName atualizado, formato inferido da extensão (.xls → excel)]
[Sem chamada de rede, sem loading, sem card]
         ↓
[Usuário seleciona "BTG" no dropdown]
[Usuário confirma "Extrato Bancário" na tab]
         ↓
[Botão "Importar Arquivo" habilitado]
         ↓
[/upload/preview → banco="BTG", tipo="extrato"]
         ↓
[journal_entries.banco_origem = "BTG" ✅]
[Dedup funciona ✅]
```

### 5.3 Layout da tela (sem mudança estrutural)

```
┌─────────────────────────┐
│ ← Importar Arquivo  ⚙️   │
├─────────────────────────┤
│ [Extrato] [Fatura]      │  ← tab define tipo_documento
├─────────────────────────┤
│ [📁 Arquivo escolhido]  │
│ ⚠️ Banco não detectado  │  ← novo: aviso inline (não card separado)
│    Selecione abaixo.    │
├─────────────────────────┤
│ Instituição *           │
│ [Selecione o banco ▼]   │  ← sempre visível e obrigatório
├─────────────────────────┤
│ ...resto do formulário  │
└─────────────────────────┘
```

---

## 📏 6. Escopo

### 6.1 Incluído (In Scope)
✅ Remover `detectFile()` e chamada ao `POST /upload/detect` do frontend  
✅ Remover componente `FileDetectionCard` da página de upload  
✅ Remover função `importPlanilhaFile` e botão "Importar planilha"  
✅ Remover estados `detection`, `detecting`, `importingPlanilha`  
✅ Validação backend: banco e tipo_documento obrigatórios no `/upload/preview`  
✅ `tipo_documento` nunca NULL em `journal_entries`

### 6.2 Excluído (Out of Scope)
❌ Mudança no algoritmo de `IdTransacao` (banco+tipo+data+valor — decisão separada)  
❌ Remoção do endpoint `/upload/detect` no backend (manter para uso futuro)  
❌ Migração retroativa de registros existentes com `banco_origem` como filename  
❌ Upload em batch — escopo separado  
❌ Remover `file-detection-card.tsx` do repositório (manter inativo para reuso futuro)

### 6.3 Futuro (V2 — quando tiver cobertura robusta)
🔮 Reintroduzir auto-detect como *sugestão* (não bloqueante, cobertura ≥95% dos formatos)  
🔮 Melhorar `fingerprints.py` para BTG XLS (extensão `.xls` + conteúdo sem keyword)  
🔮 Mudar `IdTransacao` para usar banco+tipo+data+valor (eliminar dependência do nome)  
🔮 Migração dos registros existentes com `banco_origem` incorreto

---

## 📊 7. Métricas de Sucesso

| Métrica | Baseline | Meta |
|---------|----------|------|
| `journal_entries` com `banco_origem` = filename | ~16 registros históricos | 0 novos |
| `journal_entries` com `tipodocumento` = NULL | ~16 registros históricos | 0 novos |
| Uploads que chegam na preview com `banco="generico"` | desconhecido | 0 |
| Taxa de deduplicação em segundo upload do mesmo extrato | 0% | ≥90% |

---

## 🚧 8. Riscos

**Risco 1: Usuário não sabe qual banco selecionar**
- **Probabilidade:** Baixa (usuário tem o arquivo na mão)
- **Mitigação:** Label claro "Instituição Financeira *" + placeholder "Selecione o banco"

**Risco 2: Processador errado invocado (banco selecionado ≠ formato do arquivo)**
- **Probabilidade:** Baixa
- **Mitigação:** Backend já retorna erro 422 com mensagem clara quando processador não encontrado para banco/formato

**Risco 3: Registros históricos com banco_origem=filename causam falsos negativos na dedup**
- **Probabilidade:** Alta (já existe no banco)
- **Mitigação:** Out of scope — aceitar que registros antigos não serão deduplicados; apenas novos uploads serão corretos
- **Plano B longo prazo:** Script de migração que corrige `banco_origem` baseado em `session_id` + `upload_history`

---

## ⏱️ 9. Estimativa

| Atividade | Estimativa |
|-----------|------------|
| Frontend: remover auto-detect, FileDetectionCard, importPlanilha | ~1h |
| Backend: validação banco+tipo obrigatório no `/upload/preview` | ~30min |
| Testes manuais (upload BTG XLS + verificar dedup) | ~1h |
| **Total** | **~2,5h** |

---

## 🔗 10. Contexto Técnico Relevante

### Arquivos a modificar
- `app_dev/frontend/src/app/mobile/upload/page.tsx` — remover lógica `importPlanilhaFile` / `FileDetectionCard` com bypass
- `app_dev/frontend/src/features/upload/components/file-detection-card.tsx` (ou equivalente) — tornar informativo
- `app_dev/backend/app/domains/upload/router.py` — endpoint `/importar-planilha` e validações em `/preview`
- `app_dev/backend/app/domains/upload/service.py` — validar banco e tipo no `process_and_preview`

### Causa raiz da detecção falha (para referência)
`fingerprints.py` fingerprint `btg_extrato`:
```python
"btg_extrato": {
    "extensao": [".csv", ".xlsx"],
    "cabecalho_obrigatorio": ["Data", "Histórico", "Valor"],
    "conteudo_regex": r"btg|pactual",  # Não presente no corpo do XLS
    "banco": "btg",
    "tipo": "extrato",
},
```
O arquivo `Extrato_..._11259347605.xls` não contém "btg" ou "pactual" no corpo — apenas no nome. E `.xls` não está na lista de extensões (apenas `.csv`, `.xlsx`). Logo: fallback "generico".

### Endpoint de bypass que será removido/restringido
```
POST /api/v1/upload/importar-planilha
```
Atualmente: ignora banco e tipo_documento → salva como "Planilha genérica"

---

## ✅ 11. Aprovação

| Nome | Papel | Status |
|------|-------|--------|
| Emanuel | PO + Dev | ⏳ Em revisão |

---

**Próximo Passo:** Aprovar PRD → criar TECH SPEC (`/docs/features/upload-banco-manual/02-TECH_SPEC/TECH_SPEC.md`)
