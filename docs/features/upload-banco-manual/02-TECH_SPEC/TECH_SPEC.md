# 🛠️ TECH SPEC — IdTransacao v5

**Feature:** Upload com Seleção Manual + IdTransacao v5  
**PRD:** `../01-PRD/PRD.md`  
**Versão:** 1.0  
**Data:** 21/03/2026  
**Autor:** Emanuel  
**Status:** ✅ Pronto para implementação

---

## 📦 1. Contexto Técnico

### Estado atual do banco de dados

```
journal_entries — user_id=1
─────────────────────────────────────────────────
Total registros : 4.048
banco_origem distintos : 8

banco_origem              | count  | status
──────────────────────────┼────────┼──────────────────
Itaú                      | 1.872  | ✅ limpo
Mercado Pago              | 1.552  | ✅ limpo
XP                        |   486  | ✅ limpo
Santander                 |    98  | ✅ limpo
BTG                       |    10  | ✅ limpo (form antigo)
Nubank                    |     1  | ✅ limpo
BTG202601.xls             |    17  | ❌ sujo (filename)
Extrato_2025-11-..._11259347605.xls |  12  | ❌ sujo (filename)
─────────────────────────────────────────────────
Registros com banco sujo : 29  (0,7% do total)
Todos os IdTransacao     : v4.2.1 (baseado em nome) → precisam recálculo
```

### Arquivos impactados

| Arquivo | Tipo de mudança | Sprint |
|---------|----------------|--------|
| `app/shared/utils/hasher.py` | Modificar — nova assinatura + canonical map | S1 |
| `app/shared/utils/__init__.py` | Sem mudança de API pública — exportação já existe | S1 |
| `app/domains/upload/processors/marker.py` | Modificar — nova chamada ao hasher | S1 |
| `app/domains/upload/service.py` | ✅ **Já feito** — injeção banco/tipo do form | — |
| `app/domains/upload/router.py` | Modificar — validação banco ≠ vazio/generico | S1 |
| `scripts/database/recalculate_id_transacao_v5.py` | Criar — migração histórica | S2 |
| `scripts/testing/test_idtransacao_v5.py` | ✅ **Já existe** — 23/23 passando | — |

---

## 🏗️ 2. DAG de Dependências

```
A [hasher.py v5]
    ↓
B [marker.py atualizado]        C [router.py validação]
    ↓                               ↓
D [testes unitários passando]
    ↓
E [backup DB]
    ↓
F [script migração — limpeza banco_origem]
    ↓
G [script migração — recálculo IdTransacao]
    ↓
H [teste E2E: re-upload BTG XLS → dedup 100%]
    ↓
I [commit + deploy]
```

**Regra:** Nunca executar F/G sem E (backup). Nunca fazer I sem H.

---

## 🔧 3. hasher.py — Diff completo

### 3.1 Mudanças

- Adicionar `import unicodedata` e `import re` no topo
- Adicionar `_BANCO_CANONICAL` (dict)
- Adicionar `_normalize_str()` (função privada)
- Adicionar `get_canonical_banco()` (função pública — usada pela migração)
- **Substituir** `generate_id_transacao(data, estabelecimento, valor, user_id, sequencia)` pela v5
- Manter `fnv1a_64_hash` e `generate_id_simples` **inalterados**

### 3.2 Código novo completo

```python
"""
Utilitários para hash FNV-1a 64-bit

Versão: 3.0.0
Data: 21/03/2026
Status: stable

🔒 ARQUIVO CRÍTICO - Requer versionamento obrigatório

Histórico:
- 2.0.0: Migração de MD5 para FNV-1a 64-bit (correção bug colisão VPD)
- 2.1.0: Sistema de versionamento implementado
- 3.0.0: IdTransacao v5 — chave baseada em banco+tipo+data+valor (sem nome)
          Resolve deduplicação quebrada para BTG (descrição varia entre exports)
          Adiciona canonical mapping para migração de dados históricos
          BREAKING CHANGE: requer recálculo de todos os IdTransacao existentes
"""

import re
import unicodedata


# ──────────────────────────────────────────────────────────────────────────────
# FNV-1a 64-bit — INALTERADO
# ──────────────────────────────────────────────────────────────────────────────

def fnv1a_64_hash(text):
    """Gera hash FNV-1a 64-bit de uma string. Retorna str decimal."""
    FNV_OFFSET_64 = 0xcbf29ce484222325
    FNV_PRIME_64  = 0x100000001b3
    MASK64        = (1 << 64) - 1
    h = FNV_OFFSET_64
    for char in text:
        h ^= ord(char)
        h = (h * FNV_PRIME_64) & MASK64
    return str(h)


# ──────────────────────────────────────────────────────────────────────────────
# Canonical mapping — normalização de nomes de banco
# Necessário principalmente para migração histórica (banco_origem inconsistente)
# Em uploads novos, service.py injeta o valor canônico do form.
# ──────────────────────────────────────────────────────────────────────────────

_BANCO_CANONICAL: dict = {
    # BTG
    'BTG':         'BTG',
    'BTGPACTUAL':  'BTG',       # 'BTG Pactual' → _normalize_str → 'BTGPACTUAL' → 'BTG'
    # Mercado Pago
    'MERCADOPAGO': 'MERCADOPAGO',   # 'Mercado Pago' e 'MercadoPago' → mesmo resultado
    # Demais bancos suportados
    'ITAU':        'ITAU',
    'BRADESCO':    'BRADESCO',
    'NUBANK':      'NUBANK',
    'SANTANDER':   'SANTANDER',
    'BB':          'BB',
    'BANCODOB':    'BB',        # 'Banco do Brasil' → 'BANCODOB' → 'BB'
    'BANCODOBRASIL': 'BB',
    'CAIXA':       'CAIXA',
    'XP':          'XP',
    'INTER':       'INTER',
    'C6':          'C6',
    'C6BANK':      'C6',        # 'C6 Bank' → 'C6'
    'SICOOB':      'SICOOB',
    'SICREDI':     'SICREDI',
    'OUTROS':      'OUTROS',
}


def _normalize_str(text: str) -> str:
    """
    Remove acentos, converte para maiúsculas, elimina tudo que não for A-Z0-9.

    Exemplos:
        'Itaú'         → 'ITAU'
        'Mercado Pago' → 'MERCADOPAGO'
        'BTG Pactual'  → 'BTGPACTUAL'
        'C6 Bank'      → 'C6BANK'
    """
    sem_acento = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^A-Z0-9]', '', sem_acento.upper())


def get_canonical_banco(banco: str) -> str:
    """
    Retorna o nome canônico do banco para uso no hash v5.

    Fluxo: texto raw → _normalize_str → lookup em _BANCO_CANONICAL.
    Se não encontrado (banco novo), retorna o próprio _normalize_str como fallback.

    Exemplos:
        'BTG Pactual'  → 'BTG'
        'btg pactual'  → 'BTG'
        'Mercado Pago' → 'MERCADOPAGO'
        'MercadoPago'  → 'MERCADOPAGO'
        'Itaú'         → 'ITAU'
        'Banco do Brasil' → 'BB'
        'BancoDesconhecido' → 'BANCODESCONHECIDO'  ← fallback seguro
    """
    key = _normalize_str(banco)
    return _BANCO_CANONICAL.get(key, key)


# ──────────────────────────────────────────────────────────────────────────────
# generate_id_transacao — v5 (BREAKING CHANGE em relação à v4.2.1)
# ──────────────────────────────────────────────────────────────────────────────

def generate_id_transacao(data: str, banco: str, tipo_documento: str,
                          valor: float, user_id: int, sequencia: int = 1) -> str:
    """
    Gera IdTransacao v5 usando hash FNV-1a 64-bit.

    ESTRATÉGIA v5:
    - Chave: user_id | banco_canonical | tipo | data | valor
    - Remove dependência do nome/descrição da transação
    - Imune a variações de texto entre exports do mesmo banco
    - Sequência diferencia múltiplas transações com mesma chave no arquivo

    Args:
        data          : Data no formato DD/MM/AAAA
        banco         : Nome do banco do form (ex: 'BTG Pactual', 'Mercado Pago')
        tipo_documento: 'extrato' ou 'fatura'
        valor         : Valor EXATO (com sinal — negativo para despesas)
        user_id       : ID do usuário (isolamento entre usuários)
        sequencia     : Posição no arquivo (1=primeira ocorrência, 2=segunda, ...)

    Returns:
        str: IdTransacao — hash FNV-1a 64-bit em decimal

    Exemplos:
        # Mesma transação BTG, duas descrições diferentes → mesmo hash ✅
        >>> generate_id_transacao('29/12/2025', 'BTG Pactual', 'extrato', 10520.01, 1)
        >>> generate_id_transacao('29/12/2025', 'BTG',         'extrato', 10520.01, 1)
        # Ambos retornam o mesmo valor (canonical 'BTG')

        # Dois saques de R$100 no mesmo dia → hashes diferentes por sequência ✅
        >>> generate_id_transacao('15/01/2026', 'Itaú', 'extrato', -100.00, 1, sequencia=1)
        >>> generate_id_transacao('15/01/2026', 'Itaú', 'extrato', -100.00, 1, sequencia=2)
        # Valores diferentes

    BREAKING CHANGE vs v4.2.1:
        - Parâmetro 'estabelecimento' removido
        - Parâmetros 'banco' e 'tipo_documento' adicionados
        - Todos os IdTransacao existentes devem ser recalculados (migração)
    """
    banco_norm = get_canonical_banco(banco)           # 'BTG Pactual' → 'BTG'
    tipo_norm  = _normalize_str(tipo_documento)       # 'extrato' → 'EXTRATO'
    valor_str  = f"{float(valor):.2f}"                # -10520.01 → '-10520.01'

    chave = f"{user_id}|{banco_norm}|{tipo_norm}|{data}|{valor_str}"

    hash_atual = fnv1a_64_hash(chave)
    for _ in range(sequencia - 1):
        hash_atual = fnv1a_64_hash(hash_atual)

    return hash_atual


# ──────────────────────────────────────────────────────────────────────────────
# generate_id_simples — INALTERADO (compatibilidade n8n)
# ──────────────────────────────────────────────────────────────────────────────

def generate_id_simples(data, estabelecimento, valor):
    """Gera ID simples (compatível com n8n). INALTERADO."""
    from app.shared.utils.normalizer import normalizar_estabelecimento
    estab_norm = normalizar_estabelecimento(estabelecimento)
    str_concat = f"{data}{estab_norm}{valor:.2f}".replace(' ', '').replace('/', '').replace('-', '')
    hash_val = 0
    for char in str_concat:
        hash_val = ((hash_val << 5) - hash_val) + ord(char)
        hash_val = hash_val & 0xFFFFFFFF
    return str(abs(hash_val))
```

---

## 🔧 4. marker.py — Diff

### 4.1 Localização da mudança

Arquivo: `app_dev/backend/app/domains/upload/processors/marker.py`  
Linhas ~295–315 (bloco de cálculo do `estab_normalizado` e `id_transacao`)

### 4.2 Antes

```python
# v4.2.3 — usa nome da transação na chave
if info_parcela and is_fatura:
    base_norm = re.sub(r'[^A-Z0-9]', '', estabelecimento_base.upper())
    estab_normalizado = f"{base_norm} ({parcela_atual}/{total_parcelas})"
else:
    estab_normalizado = re.sub(r'[^A-Z0-9]', '', raw.lancamento.upper())

estab_hash = estab_normalizado
valor_hash = arredondar_2_decimais(raw.valor)

chave_unica = f"{raw.data}|{estab_hash}|{valor_hash:.2f}"
sequencia = self._get_sequence_for_duplicate(chave_unica)

id_transacao = generate_id_transacao(
    data=raw.data,
    estabelecimento=estab_normalizado,
    valor=raw.valor,
    user_id=self.user_id,
    sequencia=sequencia
)
```

### 4.3 Depois

```python
# v5 — usa banco+tipo na chave (nome ignorado para IdTransacao)
# Nota: banco e tipo_documento são garantidos pelo fix do service.py (Fase 2a)

# Chave de dedup dentro do arquivo: banco|tipo|data|valor (sem nome)
valor_hash   = arredondar_2_decimais(raw.valor)
chave_unica  = f"{raw.banco}|{raw.tipo_documento}|{raw.data}|{valor_hash:.2f}"
sequencia    = self._get_sequence_for_duplicate(chave_unica)

id_transacao = generate_id_transacao(
    data=raw.data,
    banco=raw.banco,
    tipo_documento=raw.tipo_documento,
    valor=raw.valor,
    user_id=self.user_id,
    sequencia=sequencia
)
```

> **Atenção:** o bloco `estab_normalizado` não precisa ser removido — ainda é usado para `IdParcela` e `EstabelecimentoBase`. Apenas o trecho de `chave_unica` e a chamada a `generate_id_transacao` mudam.

---

## 🔧 5. router.py — Validação de banco obrigatório

### 5.1 Localização

Endpoint `POST /upload/preview` — antes da chamada ao service.

### 5.2 Código a adicionar

```python
# Bancos inválidos para geração de IdTransacao v5
_BANCOS_INVALIDOS = {'', 'generico', 'outros', 'outro', 'desconhecido'}

@router.post("/preview", response_model=UploadPreviewResponse)
async def upload_preview(
    ...
    banco: str = Form(...),
    ...
):
    # Validação: banco deve ser identificável para gerar IdTransacao correto
    if banco.strip().lower() in _BANCOS_INVALIDOS:
        raise HTTPException(
            status_code=422,
            detail={
                "errorCode": "UPL_010",
                "error": "Instituição financeira obrigatória",
                "detail": (
                    "Selecione a instituição financeira correta. "
                    "Uploads sem banco identificado não permitem deduplicação."
                )
            }
        )
    ...
```

> **Nota:** `'Outros'` está na lista de bancos do dropdown mas não mapeia para um processador real. Se o usuário selecionar, deve ser bloqueado pelo processador antes desse ponto — a validação aqui é uma segunda linha de defesa.

---

## 🔧 6. Script de Migração Histórica

### 6.1 Arquivo

`scripts/database/recalculate_id_transacao_v5.py`

### 6.2 Lógica completa

```python
#!/usr/bin/env python3
"""
Migração: IdTransacao v4.2.1 → v5

Recalcula IdTransacao de todos os registros em journal_entries usando o
novo algoritmo v5 (banco + tipo + data + valor, sem nome).

PRÉ-REQUISITOS:
  1. Backup do banco: ./scripts/deploy/backup_daily.sh
  2. Containers Docker rodando: ./scripts/deploy/quick_start_docker.sh
  3. Testes unitários passando: python3 scripts/testing/test_idtransacao_v5.py

EXECUÇÃO:
  docker exec finup_backend_dev python3 /app/scripts/database/recalculate_id_transacao_v5.py
  
  Flags:
    --dry-run    Calcula sem salvar (mostra preview)
    --user-id N  Migrar apenas um usuário específico

REVERSÃO:
  Não é possível reverter automaticamente. Usar backup criado antes da execução.
"""

import sys
import argparse
import logging
from pathlib import Path

# Mapa de limpeza de banco_origem sujo (filenames → banco canônico)
# Atualizar conforme novos filenames sujos forem encontrados
BANCO_ORIGEM_CLEANUP: dict = {
    # Filenames BTG identificados no DB em 21/03/2026
    'BTG202601.xls':                                         'BTG Pactual',
    'Extrato_2025-11-20_a_2026-01-18_11259347605.xls':       'BTG Pactual',
    # Adicionar aqui novos casos de banco_origem sujo
}

def _inferir_banco_de_filename(banco_origem: str) -> str:
    """
    Tenta inferir o banco a partir de um filename quando o mapa explícito não cobre.
    
    Heurísticas:
    - Contém 'btg' ou número de conta BTG → 'BTG Pactual'
    - Contém 'mp' ou 'mercado' → 'Mercado Pago'
    - Contém 'itau' → 'Itaú'
    """
    nome = banco_origem.lower()
    if 'btg' in nome or '11259347605' in nome or '11259' in nome:
        return 'BTG Pactual'
    if 'mercado' in nome or 'mp' in nome:
        return 'Mercado Pago'
    if 'itau' in nome or 'itaú' in nome:
        return 'Itaú'
    if 'xp' in nome:
        return 'XP'
    # Não reconhecido — retorna o original (canonical fallback no hasher)
    return banco_origem


def limpar_banco_origem(banco_origem: str) -> str:
    """Retorna o banco canônico para o banco_origem fornecido."""
    if not banco_origem:
        return 'Desconhecido'
    # 1. Mapa explícito (casos conhecidos)
    if banco_origem in BANCO_ORIGEM_CLEANUP:
        return BANCO_ORIGEM_CLEANUP[banco_origem]
    # 2. Heurística por filename
    if '.' in banco_origem and '/' not in banco_origem:
        # Parece um filename (tem extensão, sem barras de data)
        return _inferir_banco_de_filename(banco_origem)
    # 3. Banco já está limpo
    return banco_origem


def main():
    parser = argparse.ArgumentParser(description='Migração IdTransacao v4.2.1 → v5')
    parser.add_argument('--dry-run', action='store_true', help='Simula sem salvar')
    parser.add_argument('--user-id', type=int, help='Migrar apenas este user_id')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)

    # Import app após setup de path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'app_dev' / 'backend'))
    from app.core.database import SessionLocal
    from app.domains.transactions.models import JournalEntry
    from app.shared.utils.hasher import generate_id_transacao, get_canonical_banco

    db = SessionLocal()
    try:
        # Carregar registros
        query = db.query(JournalEntry)
        if args.user_id:
            query = query.filter(JournalEntry.user_id == args.user_id)
        entries = query.all()

        logger.info(f"📊 Total de registros a migrar: {len(entries)}")

        # Estatísticas
        bancos_sujos  = 0
        bancos_limpos = 0
        erros         = 0
        atualizados   = 0

        for entry in entries:
            try:
                # 1. Limpar banco_origem
                banco_original = entry.banco_origem or ''
                banco_limpo    = limpar_banco_origem(banco_original)

                if banco_limpo != banco_original:
                    bancos_sujos += 1
                    logger.debug(f"  Banco corrigido: '{banco_original}' → '{banco_limpo}'")
                else:
                    bancos_limpos += 1

                # 2. Tipo documento
                tipo = entry.tipodocumento or 'extrato'

                # 3. Recalcular IdTransacao v5
                # sequencia: usar campo existente se disponível, senão 1
                seq = getattr(entry, 'sequencia', 1) or 1

                novo_id = generate_id_transacao(
                    data=entry.Data,
                    banco=banco_limpo,
                    tipo_documento=tipo,
                    valor=entry.Valor,
                    user_id=entry.user_id,
                    sequencia=seq
                )

                if not args.dry_run:
                    entry.IdTransacao   = novo_id
                    entry.banco_origem  = banco_limpo   # persiste banco limpo também
                    atualizados += 1

            except Exception as e:
                erros += 1
                logger.error(f"  ERRO entry id={getattr(entry, 'id', '?')}: {e}")

        # Resumo
        logger.info("=" * 60)
        logger.info(f"  Registros processados  : {len(entries)}")
        logger.info(f"  Bancos já limpos       : {bancos_limpos}")
        logger.info(f"  Bancos corrigidos      : {bancos_sujos}")
        logger.info(f"  Erros                  : {erros}")
        if args.dry_run:
            logger.info("  ⚠  DRY RUN — nenhuma alteração salva")
        else:
            logger.info(f"  ✅ Atualizados         : {atualizados}")

        if not args.dry_run and erros == 0:
            db.commit()
            logger.info("✅ Commit realizado com sucesso")
        elif erros > 0:
            db.rollback()
            logger.error("❌ Rollback por erros — verificar logs acima")
            sys.exit(1)

    finally:
        db.close()


if __name__ == '__main__':
    main()
```

### 6.3 Comandos de execução

```bash
# 1. Backup obrigatório
./scripts/deploy/backup_daily.sh

# 2. Dry-run — ver o que será feito sem alterar
docker exec finup_backend_dev python3 \
  /app/scripts/database/recalculate_id_transacao_v5.py --dry-run

# 3. Migrar apenas user_id=1 (dev — confirmar antes de todos)
docker exec finup_backend_dev python3 \
  /app/scripts/database/recalculate_id_transacao_v5.py --user-id 1

# 4. Migrar todos
docker exec finup_backend_dev python3 \
  /app/scripts/database/recalculate_id_transacao_v5.py

# 5. Validar contagem pós-migração
docker exec finup_postgres_dev psql -U finup_user -d finup_db \
  -c "SELECT banco_origem, COUNT(*) FROM journal_entries GROUP BY banco_origem ORDER BY count DESC;"
```

---

## 🧪 7. Testes

### 7.1 Testes unitários (já existem — 23/23 ✅)

```bash
python3 scripts/testing/test_idtransacao_v5.py
```

### 7.2 Smoke test pós-implementação (antes da migração)

```bash
# Verificar que backend levanta sem erro
docker-compose restart backend
sleep 5
curl -s http://localhost:8000/api/health | python3 -m json.tool

# Verificar que endpoint /upload/preview ainda responde
curl -s http://localhost:8000/docs | grep -c "upload/preview"
```

### 7.3 Teste E2E (obrigatório antes do deploy)

1. **Limpar preview:** DELETE na sessão existente se houver
2. **Upload 1:** `Extrato_2025-12-10_a_2026-03-09_11259347605.xls` → banco=BTG Pactual → confirmar → 65 transações
3. **Verificar DB:** todos os 65 registros novos têm `banco_origem='BTG Pactual'`
4. **Upload 2:** mesmo arquivo novamente
5. **Verificado:** preview mostra aba "Já Importadas" com 65 transações

```bash
# Consulta de validação após Upload 1 + Upload 2:
docker exec finup_postgres_dev psql -U finup_user -d finup_db -c "
  SELECT 
    p.banco,
    p.tipo_documento,
    COUNT(*) as total,
    SUM(CASE WHEN p.is_duplicate THEN 1 ELSE 0 END) as duplicados
  FROM preview_transacoes p
  WHERE p.session_id = '<session_id_upload_2>'
  GROUP BY p.banco, p.tipo_documento;
"
# Esperado: duplicados = 65
```

### 7.4 Teste de não-regressão pós-migração

```bash
# Total de registros não deve mudar
docker exec finup_postgres_dev psql -U finup_user -d finup_db \
  -c "SELECT COUNT(*) FROM journal_entries;"
# Esperado: 4048 (mesmo número antes e depois)

# Nenhum IdTransacao nulo
docker exec finup_postgres_dev psql -U finup_user -d finup_db \
  -c "SELECT COUNT(*) FROM journal_entries WHERE \"IdTransacao\" IS NULL;"
# Esperado: 0

# Nenhum banco_origem com filename (após limpeza)
docker exec finup_postgres_dev psql -U finup_user -d finup_db \
  -c "SELECT COUNT(*) FROM journal_entries WHERE banco_origem LIKE '%.xls%' OR banco_origem LIKE '%.pdf%';"
# Esperado: 0
```

---

## ⚠️ 8. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Registros com `sequencia` incorreta ou NULL | Média | Alto — IDs errados | Campo `sequencia` verificado na migração; fallback seq=1 para NULL |
| Banco não identificado por heurística | Baixa (29 registros sujos, todos BTG) | Médio — IDs com canonical fallback em vez do canônico correto | Mapa explícito cobre os 29 casos conhecidos |
| Rollback necessário em prod após migração | Baixa | Alto | Backup obrigatório antes; script faz `db.rollback()` em caso de qualquer erro |
| `generate_id_simples` chamado por código legado ainda usa `estabelecimento` | N/A | Zero — função INALTERADA | Verificar que nenhum código chama `generate_id_transacao` com assinatura antiga |

### 8.1 Checklist de chamadas à função antiga

Antes de implementar, verificar se há outras chamadas com assinatura v4.2.1:

```bash
# Buscar todas as chamadas a generate_id_transacao no projeto
grep -rn "generate_id_transacao" app_dev/backend/ --include="*.py" | grep -v "__pycache__"
```

Resultado esperado — arquivos a atualizar além de `marker.py`:

```
app/shared/utils/hasher.py            ← definição (atualizar)
app/domains/upload/processors/marker.py ← principal consumidor (atualizar)
scripts/regenerate_id_transacao_v4_2_3.py  ← script legado (atualizar assinatura)
scripts/recalculate_id_transacao_sql.py    ← script legado (atualizar assinatura)
scripts/recalcular_idtransacao.py          ← script legado (atualizar assinatura)
scripts/fix_temp_ids.py                    ← script legado (atualizar assinatura)
```

> Scripts legados em `backend/scripts/` devem ter a assinatura atualizada para não quebrar se executados acidentalmente, mas **não serão usados** — o novo script é `recalculate_id_transacao_v5.py`.

---

## 📁 9. Estrutura de Arquivos Final

```
app_dev/backend/
├── app/
│   ├── shared/utils/
│   │   └── hasher.py              ← ✏️  v3.0.0 (nova assinatura)
│   └── domains/upload/
│       ├── processors/
│       │   └── marker.py          ← ✏️  chave_unica e generate_id_transacao
│       ├── router.py              ← ✏️  validação banco obrigatório
│       └── service.py             ← ✅ já feito (injeção banco/tipo)
└── scripts/
    └── database/ (novo)
        └── recalculate_id_transacao_v5.py  ← 🆕 migração histórica

scripts/testing/
└── test_idtransacao_v5.py         ← ✅ já existe (23/23)
```
