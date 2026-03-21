# 📋 PRD - Upload com Seleção Manual + IdTransacao v5

**Status:** 🟢 Fase 1 Concluída · � Fase 2 Em Desenvolvimento  
**Versão:** 0.3  
**Data:** 21/03/2026  
**Autor:** Emanuel  
**Stakeholders:** Emanuel (PO + Dev)

---

## 📊 Sumário Executivo

Este PRD cobre **duas fases** relacionadas, ambas necessárias para que a deduplicação de transações funcione corretamente:

| Fase | O que | Status |
|------|-------|--------|
| **Fase 1** | Remover auto-detect — banco sempre selecionado manualmente | ✅ **Concluída** (commit `27ea995d`) |
| **Fase 2a** | Fix `service.py`: injetar `banco`/`tipo_documento` do form nos `raw` | ✅ **Concluída** (21/03/2026) |
| **Fase 2b** | Novo algoritmo `IdTransacao v5` em `hasher.py` + `marker.py` | 🔵 Em desenvolvimento |
| **Fase 2c** | Migração histórica: recalcular `IdTransacao` dos registros existentes no DB | 🟡 Pendente |

**Por quê duas fases são necessárias:**  
A Fase 1 garante que `banco` e `tipo_documento` estejam sempre presentes e corretos. Sem isso, a Fase 2 não pode ser implementada (o novo algoritmo depende de banco consistente).  
A Fase 2 resolve a causa raiz restante: descrições inconsistentes entre exports do mesmo banco fazem dois uploads do mesmo arquivo gerarem IDs diferentes.

**ROI:** Deduplicação funcionando = zero transações duplicadas = dados financeiros confiáveis.

---

## 🎯 1. Contexto e Problema

### 1.1 Situação Anterior (Fase 1 — ✅ Resolvida)

O upload tinha dois caminhos, sendo o problemático o atalho:

```
❌ Fluxo bypass (removido):
Usuário escolhe arquivo → auto-detect retorna "generico" → 
"Importar planilha" → banco_origem = filename, tipo_documento = NULL
```

**Impacto:** `journal_entries.banco_origem` ficava como o filename do arquivo  
(`Extrato_2025-11-20_a_2026-01-18_11259347605.xls`), não como `"BTG"`.

**Solução aplicada (commit `27ea995d`):**
- Removido `detectFile()` e `FileDetectionCard`
- Removido endpoint bypass `importPlanilhaFile`
- Banco agora sempre selecionado explicitamente pelo usuário → `banco_origem` = `"BTG"` consistente

---

### 1.2 Investigação Fase 2 (21/03/2026) — Dois sub-problemas identificados

#### Sub-problema A: `raw.banco` não vinha do form ✅ Corrigido

Os processadores individuais cada um definia `raw.banco` com strings diferentes — o service não sobrescrevia com o valor selecionado no form:

| Processador | `raw.banco` que gerava |
|-------------|------------------------|
| `btg_extrato.py` (XLS) | `nome_arquivo` (ex: `"Extrato_2025-12...xls"`) |
| `btg_extrato_pdf.py` | recebe `banco` do service ✅ |
| `mercadopago_extrato_pdf.py` | hardcoda `'MercadoPago'` (sem espaço) |
| `mercadopago_extrato.py` (XLSX) | hardcoda `'Mercado Pago'` (com espaço) |

**Fix aplicado em `service.py`:** após chamar o processador, injetar `raw.banco = banco` e `raw.tipo_documento = tipo_documento` para todos os `raw`. O form sempre envia o valor canônico da tabela `bank_format_compatibility` (`'Mercado Pago'`, `'BTG Pactual'`, etc.).

#### Sub-problema B: algoritmo v4.2.1 usa nome da transação na chave ❌ Ainda pendente

Mesmo com banco correto, a deduplicação **ainda falha** porque o `IdTransacao` atual inclui a **descrição/nome** da transação na chave de hash:

```python
# Algoritmo atual (v4.2.1) — PROBLEMA
chave = f"{user_id}|{data}|{estab_normalizado}|{valor:.2f}"
# estab_normalizado = re.sub(r'[^A-Z0-9]', '', lancamento.upper())
```

**O banco BTG exporta a mesma transação com descrições diferentes entre arquivos:**

| Campo | Upload anterior | Novo upload (sessão investigada) |
|-------|-----------------|-----------------------------------|
| `Estabelecimento` | `Salário - Pagamento recebido` | `Salário - Portabilidade de salário - Pagamento recebido` |
| `estab_normalizado` | `SALARIOPAGAMENTORECEBIDO` | `SALARIOPORTABILIDADEDESALARIOPAGAMENTORECEBIDO` |
| `Valor` | 10520.01 | 10520.01 |
| `Data` | 29/12/2025 | 29/12/2025 |
| `IdTransacao gerado` | `3033027455298180257` | `12688721295696874454` |
| **Dedup detecta?** | ❌ IDs diferentes | ❌ Nunca detecta como duplicata |

Mesmo valor, mesma data, mesmo banco — mas hashes **impossíveis de coincidir** por causa do nome.

**Impacto atual:**
- 🔴 **Crítico:** Deduplicação 0% para extratos BTG — usuário importa o mesmo extrato múltiplas vezes sem aviso
- 🟡 **Médio:** Preview mostra "Todas (65)" sem aba "Já Importadas" — UX confusa
- 🟡 **Médio:** Dashboard acumula transações duplicadas silenciosamente

---

## 🎯 2. Objetivos

### 2.1 Fase 1 — ✅ Concluída
Garantir que `banco` e `tipo_documento` estejam sempre presentes e corretos em todo upload.

### 2.2 Fase 2 — 🟡 A Implementar  
Reformular o algoritmo de geração de `IdTransacao` para **não depender do nome** da transação, usando banco + tipo_documento + data + valor + sequência como chave única.

### 2.3 Resultado Combinado
Com Fase 1 + Fase 2:
- Dois uploads do mesmo arquivo BTG → mesmos `IdTransacao` → deduplicação detecta 100%
- `banco_origem` sempre "BTG", "Mercado Pago", etc. → análises por banco corretas

---

## 👥 3. User Stories

#### **US-01: Upload com banco selecionado manualmente** ✅ DONE
**Como** usuário que importa extrato BTG  
**Quero** selecionar "BTG" no dropdown e prosseguir sem detecção automática  
**Para** que o sistema saiba o banco correto desde o início

**Acceptance Criteria:**
- [x] Auto-detect removido completamente — sem chamada de rede ao escolher arquivo
- [x] `FileDetectionCard` removido do fluxo
- [x] Botão "Importar planilha" (bypass) removido
- [x] Banco obrigatório antes de habilitar "Importar Arquivo"
- [x] `banco_origem` no banco de dados é sempre o nome do banco, nunca o filename

---

#### **US-02: Deduplicação funciona independente do nome da transação** 🟡 A IMPLEMENTAR
**Como** usuário que re-importa um extrato BTG por acidente (ou importa o período seguinte que tem overlap)  
**Quero** que o sistema reconheça as transações já importadas  
**Para** não ter duplicatas no meu dashboard

**Acceptance Criteria:**
- [ ] Ao importar um arquivo BTG XLS já importado anteriormente, a aba "Já Importadas" aparece com ≥90% das transações marcadas
- [ ] Transações com mesmo banco, tipo, data e valor são detectadas como duplicatas mesmo que a descrição seja diferente entre os dois arquivos
- [ ] A coluna `IdTransacao` no banco é recalculada com a v5 para todos os registros existentes
- [ ] Novos uploads usam automaticamente o algoritmo v5

---

#### **US-03: Tipo de documento sempre definido** ✅ DONE
**Como** sistema  
**Quero** que `tipo_documento` nunca seja NULL em `journal_entries`  

**Acceptance Criteria:**
- [x] Tab "Extrato Bancário" → `tipo_documento = "extrato"` (garantido pela remoção do bypass)
- [x] Tab "Fatura Cartão" → `tipo_documento = "fatura"`

---

## 📋 4. Requisitos Funcionais

### 4.1 Fase 1 — ✅ Concluída (commit `27ea995d`)

| Requisito | Status | Detalhe |
|-----------|--------|---------|
| RF-01: Remover `detectFile()` e estado `detection` | ✅ Done | `handleFileChange` agora síncrono |
| RF-02: Remover `FileDetectionCard` do JSX | ✅ Done | Componente mantido no repo, não usado |
| RF-03: Remover `importPlanilhaFile` e estado `importingPlanilha` | ✅ Done | Função mantida no service, não chamada |
| RF-04: Banco obrigatório antes de "Importar Arquivo" | ✅ Done | Validação já existia, confirmada |
| RF-05: Tab define `tipo_documento` | ✅ Done | `activeTab` → `tipoDocumento` sem bypass |

---

### 4.2 Fase 2 — 🟡 IdTransacao v5 (a implementar)

**RF-10: Novo algoritmo `generate_id_transacao_v5`** em `hasher.py`

A chave de hash muda de:
```python
# v4.2.1 — ATUAL (QUEBRADO para BTG)
chave = f"{user_id}|{data}|{estab_normalizado}|{valor:.2f}"
# Falha porque 'estab_normalizado' varia entre exports:
# Upload 1: "SALARIOPAGAMENTORECEBIDO"
# Upload 2: "SALARIOPORTABILIDADEDESALARIOPAGAMENTORECEBIDO"
```

Para:
```python
# v5 — IMPLEMENTAÇÃO COMPLETA
import unicodedata

# Mapa canônico: garante que variações do mesmo banco gerem o mesmo hash.
# Necessário para a migração de dados históricos (registros salvos antes do fix
# do service.py ainda têm banco_origem inconsistente no DB).
_BANCO_CANONICAL: dict[str, str] = {
    'BTG':         'BTG',
    'BTGPACTUAL':  'BTG',      # 'BTG Pactual' após _normalize_str
    'MERCADOPAGO': 'MERCADOPAGO',
    'ITAU':        'ITAU',
    'BRADESCO':    'BRADESCO',
    'NUBANK':      'NUBANK',
    'SANTANDER':   'SANTANDER',
    'BB':          'BB',
    'CAIXA':       'CAIXA',
    'XP':          'XP',
    'INTER':       'INTER',
    'C6':          'C6',
    'C6BANK':      'C6',       # 'C6 Bank' após _normalize_str
    # adicionar conforme novos bancos suportados
}

def _normalize_str(text: str) -> str:
    """Remove acentos, maiuscula, elimina tudo que não for A-Z0-9."""
    sem_acento = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^A-Z0-9]', '', sem_acento.upper())

def get_canonical_banco(banco: str) -> str:
    """
    Retorna o nome canônico do banco para o hash v5.
    Processo: _normalize_str → lookup em _BANCO_CANONICAL.
    Se não encontrado, retorna o próprio _normalize_str (fallback seguro).
    
    Exemplos:
      'BTG Pactual' → _normalize_str → 'BTGPACTUAL' → canonical → 'BTG'
      'Mercado Pago' → 'MERCADOPAGO' → 'MERCADOPAGO'
      'MercadoPago'  → 'MERCADOPAGO' → 'MERCADOPAGO'
      'Itaú'         → 'ITAU'        → 'ITAU'
    """
    key = _normalize_str(banco)
    return _BANCO_CANONICAL.get(key, key)

def generate_id_transacao(data: str, banco: str, tipo_documento: str,
                          valor: float, user_id: int, sequencia: int = 1) -> str:
    """
    IdTransacao v5 — imune a variações de descrição entre exports do mesmo banco.
    
    Chave: user_id|banco_canonical|tipo|data|valor
    Sequência: diferencia múltiplas transações com mesma chave dentro do arquivo.
    """
    banco_norm = get_canonical_banco(banco)    # ex: 'BTG Pactual' → 'BTG'
    tipo_norm  = _normalize_str(tipo_documento)  # 'extrato' → 'EXTRATO'
    chave = f"{user_id}|{banco_norm}|{tipo_norm}|{data}|{valor:.2f}"
    h = fnv1a_64_hash(chave)
    for _ in range(sequencia - 1):
        h = fnv1a_64_hash(h)
    return h
```

**Notas de implementação:**
- `fnv1a_64_hash` permanece inalterado
- O parâmetro `estabelecimento` é **removido** da assinatura pública
- `sequencia` passa a ser obrigatório para uploads (padrão=1 mantido para retrocompatibilidade de chamadas avulsas)
- `_BANCO_CANONICAL` é necessário principalmente para a **migração histórica** — em novos uploads o service.py já garante o valor canônico do form

---

**RF-11: Atualizar `marker.py`** — passar `raw.banco` e `raw.tipo_documento` em vez de `estab_normalizado`

```python
# ANTES (marker.py)
estab_normalizado = re.sub(r'[^A-Z0-9]', '', raw.lancamento.upper())
id_transacao = generate_id_transacao(
    data=raw.data, estabelecimento=estab_normalizado,
    valor=raw.valor, user_id=self.user_id, sequencia=sequencia
)

# DEPOIS (marker.py)
id_transacao = generate_id_transacao(
    data=raw.data, banco=raw.banco,
    tipo_documento=raw.tipo_documento,
    valor=raw.valor, user_id=self.user_id, sequencia=sequencia
)
# raw.banco e raw.tipo_documento são garantidos pelo fix do service.py (Fase 2a)
```

**RF-12: Migração histórica** — recalcular `IdTransacao` de todos os registros existentes  
(detalhes em seção 4.3 abaixo)

**RF-13: Validação backend `/upload/preview`** — rejeitar banco vazio, null ou "generico"

---

### 4.3 Migração Histórica — Registros Existentes no DB

**Por que é necessária:**  
Os registros em `journal_entries` foram salvos com `IdTransacao` v4.2.1 (baseado no nome). Mesmo após implementar o v5 no código, os uploads novos gerarão IDs v5 mas o banco terá IDs v4.2.1 — a dedup comparará v5 (preview) com v4.2.1 (journal_entries) e **nunca encontrará match**.

**Problema adicional nos dados históricos:**  
Além do algoritmo diferente, o campo `banco_origem` em muitos registros históricos está incorreto:
- Registros do bypass antigo: `banco_origem = filename` (ex: `"Extrato_2025-12...xls"`)
- Registros do MP PDF: `banco_origem = 'MercadoPago'` (sem espaço)
- Registros do MP XLSX: `banco_origem = 'Mercado Pago'` (com espaço)

**Estratégia de migração:**

```python
# Script: scripts/database/recalculate_id_transacao_v5.py
# Execução: docker exec finup_backend_dev python3 /app/scripts/database/recalculate_id_transacao_v5.py

for entry in journal_entries:
    # 1. Usar canonical mapping para normalizar banco_origem inconsistente
    banco = get_canonical_banco(entry.banco_origem or '')  # trata filenames, variações
    tipo  = entry.tipodocumento or 'extrato'
    
    # 2. Recalcular IdTransacao com algoritmo v5
    novo_id = generate_id_transacao(
        data=entry.Data,
        banco=banco,
        tipo_documento=tipo,
        valor=entry.Valor,
        user_id=entry.user_id,
        sequencia=entry.sequencia  # campo existente ou recalculado por ordem no arquivo
    )
    entry.IdTransacao = novo_id
```

**Risco da migração:**  
- `banco_origem = filename` não mapeia para nenhum banco canônico conhecido → fallback será o próprio filename normalizado (ex: `'EXTRATO2025'`) → hash diferente do que novos uploads gerariam  
- **Ação:** antes de migrar, fazer limpeza de `banco_origem` usando heurística por filename (BTG detectado por `"btg"` ou `"11259347605"` no nome, etc.)
- Volume esperado: todos os registros do `user_id=1` (~2631 registros)
- Backup obrigatório antes de executar

**Ordem de execução:**
1. Implementar e testar `hasher.py` v5 + `marker.py`
2. Fazer backup: `./scripts/deploy/backup_daily.sh`
3. Executar migração em dev, validar contagens
4. Fazer novo upload de teste → confirmar dedup funciona
5. Deploy em prod → executar migração em prod

---

### 4.4 Análise de Riscos do Novo Algoritmo

**Risco: mesma data, mesmo valor, mesmo banco, transações diferentes**  
Exemplo: dois saques de R$100 no mesmo dia.

Solução: a **sequência** já existe e resolve:
```python
# Transação 1: banco=BTG, tipo=extrato, data=29/12, valor=-100.00, seq=1 → hash_A
# Transação 2: banco=BTG, tipo=extrato, data=29/12, valor=-100.00, seq=2 → hash_B
# hash_A ≠ hash_B ✅
```

A sequência é determinada pela **ordem no arquivo**. Se o mesmo arquivo é re-importado, a ordem é idêntica → as mesmas transações recebem o mesmo seq → mesmos hashes → dedup detecta. ✅

**Risco residual:** Se o banco reordenar as linhas entre dois exports diferentes do mesmo período, seq=1 e seq=2 trocariam → falso negativo na dedup. Probabilidade: muito baixa (bancos exportam em ordem cronológica consistente). Impacto: aceitável (é o mesmo risco que já existe hoje para faturas). Não bloqueia.

---

## 📐 5. Fluxo de Deduplicação (Antes vs Depois)

### 5.1 Antes (com todos os problemas)

```
Upload 1 (arquivo A, BTG XLS):
  bypass → banco=filename, tipo=NULL
  IdTransacao = hash(user|data|"SALARIOPAGAMENTORECEBIDO"|10520.01)
              = 3033027455298180257

Upload 2 (arquivo B, mesmo período, BTG XLS):
  bypass → banco=filename, tipo=NULL
  IdTransacao = hash(user|data|"SALARIOPORTABILIDADEDESALARIOPAGAMENTORECEBIDO"|10520.01)
              = 12688721295696874454

Dedup: 3033027455298180257 ≠ 12688721295696874454 → NÃO detecta 💥
```

### 5.2 Depois da Fase 1 apenas

```
Upload 1: banco="BTG", tipo="extrato" ✅
  IdTransacao = hash(user|data|"SALARIOPAGAMENTORECEBIDO"|10520.01)  ← nome ainda varia
              = X

Upload 2: banco="BTG", tipo="extrato" ✅
  IdTransacao = hash(user|data|"SALARIOPORTABILIDADEDESALARIOPAGAMENTORECEBIDO"|10520.01)
              = Y  (X ≠ Y) → ainda não detecta 😕
```

### 5.3 Depois da Fase 1 + Fase 2

```
Upload 1: banco="BTG", tipo="extrato"
  IdTransacao_v5 = hash(user|"BTG"|"EXTRATO"|29/12/2025|10520.01|seq=1)
                 = Z

Upload 2: banco="BTG", tipo="extrato"
  IdTransacao_v5 = hash(user|"BTG"|"EXTRATO"|29/12/2025|10520.01|seq=1)
                 = Z  (mesmo hash!) → DETECTA como duplicata ✅
```

---

## 📏 6. Escopo

### 6.1 Fase 1 — ✅ Concluída
- [x] Remover `detectFile()` e chamada ao `POST /upload/detect`
- [x] Remover `FileDetectionCard` do fluxo de upload
- [x] Remover `importPlanilhaFile` e estados de detecção
- [x] `handleFileChange` síncrono — só infere formato pela extensão

### 6.2 Fase 2 — � Em Desenvolvimento
- [x] **Fase 2a:** `service.py` injetar `raw.banco = banco` + `raw.tipo_documento = tipo_documento` após processamento
- [x] **Testes:** `scripts/testing/test_idtransacao_v5.py` — 23/23 passando
- [ ] **Fase 2b:** Novo `generate_id_transacao(data, banco, tipo_documento, valor, user_id, sequencia)` em `hasher.py` (com canonical mapping)
- [ ] **Fase 2b:** Atualizar `marker.py` para usar nova assinatura
- [ ] **Fase 2c:** Migração histórica: limpeza de `banco_origem` + recalcular `IdTransacao` de todos os registros em `journal_entries`
- [ ] Validação backend: rejeitar banco vazio/"generico" no `/upload/preview`

### 6.3 Out of Scope
- ❌ Remoção do endpoint `/upload/detect` no backend (manter para reuso futuro)
- ❌ Remover `file-detection-card.tsx` do repositório
- ❌ Melhorar `fingerprints.py` para reconhecer BTG XLS por conteúdo
- ❌ Upload em batch

### 6.4 Futuro (V2)
- 🔮 Reintroduzir auto-detect como *sugestão* (não bloqueante, cobertura ≥95%)
- 🔮 Migração dos registros históricos com `banco_origem` = filename

---

## 📊 7. Métricas de Sucesso

| Métrica | Baseline | Meta | Status |
|---------|----------|------|--------|
| `banco_origem` = filename em novos uploads | acontecia 100% BTG XLS | 0 | ✅ Fase 1 resolve |
| `tipodocumento` = NULL em novos uploads | acontecia 100% BTG XLS | 0 | ✅ Fase 1 resolve |
| Taxa dedup em re-upload do mesmo arquivo BTG | 0% | ≥90% | 🟡 Fase 2 resolve |
| Preview mostra aba "Já Importadas" para segundo upload do mesmo extrato | nunca | sempre | 🟡 Fase 2 resolve |

---

## 🧪 8. Testes de Validação

### 8.1 Script automatizado — `scripts/testing/test_idtransacao_v5.py`

O script em `scripts/testing/test_idtransacao_v5.py` ✅ **já existe e passa 23/23**.

| Grupo | Testes | O que valida |
|-------|--------|--------------|
| [1] Prova do bug | 3 | v4.2.1 gera IDs diferentes para mesma transação BTG; IDs conferem com os valores reais do DB |
| [2] Fix v5 | 2 | Mesmo banco+tipo+data+valor → mesmo ID; v5 não colide com v4 |
| [3] Sequência | 3 | seq=1/2/3 geram IDs diferentes |
| [4] Isolamento | 1 | user_id diferente → ID diferente |
| [5] Tipo | 1 | extrato ≠ fatura |
| [6] Normalização | 4 | case, acentos (`Itaú`==`Itau`), canonical (`BTG`==`BTG Pactual`), espaços (`Mercado Pago`==`MercadoPago`) |
| [7] Anti-colisão | 3 | BTG ≠ MP ≠ Itaú após canonical |
| [8] Cross-format | 6 | PDF==XLSX quando banco vem do form; documenta bug de filename; prova do fix |

Executar:
```bash
# Standalone (sem Docker)
python3 scripts/testing/test_idtransacao_v5.py

# Dentro do container (após implementar em hasher.py)
docker exec finup_backend_dev python3 /app/scripts/testing/test_idtransacao_v5.py
```

Resultado atual:
```
✅ 23/23 testes passaram

CONCLUSÃO: v5 resolve o problema de deduplicação BTG.
Implementar em hasher.py + marker.py + migração de dados.
```

### 8.2 Teste de ponta a ponta (manual)

1. Importar `Extrato_2025-12-10_a_2026-03-09_11259347605.xls` → banco=BTG, tipo=extrato
2. Confirmar upload → 65 transações importadas
3. Importar **mesmo arquivo** novamente
4. **Esperado:** Preview mostra aba "Já Importadas (65)" · aba "Novas (0)"

---

## ⏱️ 9. Estimativa

| Atividade | Status | Estimativa |
|-----------|--------|------------|
| Fase 1: remover auto-detect | ✅ Done | ~1h |
| Fase 2a: fix `service.py` (`raw.banco` do form) | ✅ Done | ~30min |
| Fase 2b: `hasher.py` v5 + `marker.py` | 🔵 Próximo | ~2h |
| Fase 2c: limpeza `banco_origem` histórico | 🟡 Pendente | ~1h |
| Fase 2c: script migração `IdTransacao` | 🟡 Pendente | ~1h |
| Testes manuais end-to-end | 🟡 Pendente | ~1h |
| Script de testes automatizados | ✅ Done (23/23) | ~1h |
| **Total restante** | | **~5h** |

---

## 🔗 10. Contexto Técnico

### Arquivos modificados
- ✅ `app_dev/backend/app/domains/upload/service.py` — `raw.banco = banco` + `raw.tipo_documento = tipo_documento` (Fase 2a)
- ✅ `scripts/testing/test_idtransacao_v5.py` — 23 testes do algoritmo v5

### Arquivos a modificar (Fase 2b/2c)
- `app_dev/backend/app/shared/utils/hasher.py` — nova `generate_id_transacao` v5 com canonical mapping
- `app_dev/backend/app/domains/upload/processors/marker.py` — passar `raw.banco` e `raw.tipo_documento`
- `app_dev/backend/app/domains/upload/router.py` — validação banco obrigatório
- `scripts/database/recalculate_id_transacao_v5.py` — **novo** script de migração histórica
- `app_dev/backend/scripts/regenerate_standalone.py` — atualizar para algoritmo v5

### Algoritmo v4.2.1 atual (referência)
```python
# hasher.py — generate_id_transacao atual
chave = f"{user_id}|{data}|{estab_upper}|{valor_str}"
# estab_upper = estabelecimento.upper().strip()
# estabelecimento = re.sub(r'[^A-Z0-9]', '', lancamento.upper())  # em marker.py
```

### Algoritmo v5 — implementação completa
Ver seção 4.2 RF-10 para o código completo com canonical mapping + unicodedata.

**Resumo das diferenças:**

| Aspecto | v4.2.1 | v5 |
|---------|--------|----|
| Dependência do nome | ✅ Sim (`lancamento`) | ❌ Não |
| Campo chave | `user\|data\|nome_normalizado\|valor` | `user\|banco_canonical\|tipo\|data\|valor` |
| Normalização banco | — | `unicodedata` + regex + canonical map |
| Cross-format PDF/XLSX | ❌ Quebra (nome varia) | ✅ Funciona (banco do form) |
| Retrocompatível | — | ❌ Não (requer migração de todos os registros) |

### Fonte de verdade do nome do banco
A tabela `bank_format_compatibility` é a fonte canônica. O form sempre envia `bank_name` dessa tabela:
```
'BTG Pactual', 'Banco do Brasil', 'Bradesco', 'Itaú', 'Mercado Pago', 'Outros', 'Santander'
```
O canonical mapping no `hasher.py` é necessário apenas para a **migração de dados históricos** — em uploads novos o service.py já garante o valor correto.

### Causa raiz da detecção falha (histórico)
`fingerprints.py` não reconhecia BTG XLS porque `.xls` não estava na lista e o corpo do arquivo não continha "btg"/"pactual". Resolvido pela Fase 1 (usuário seleciona manualmente).

---

## ✅ 11. Aprovação

| Nome | Papel | Status |
|------|-------|--------|
| Emanuel | PO + Dev | � Fase 2b aprovada — implementando |

---

**Próximo Passo (ordem):**
1. 🔵 Implementar `hasher.py` v5 (com canonical mapping)
2. 🔵 Atualizar `marker.py` para nova assinatura
3. 🟡 Criar `scripts/database/recalculate_id_transacao_v5.py` (migração histórica com limpeza de `banco_origem`)
4. 🟡 Executar migração em dev → testar dedup com BTG XLS
5. 🟡 Validação backend: rejeitar banco vazio em `/upload/preview`
6. 🟡 Deploy + migração em produção
