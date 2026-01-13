# 📚 Códigos de Apoio - Sistema Completo de Hash, Normalização e Deduplicação

## Arquivos do Repositório GitHub: emangue/FinUp

### 🔐 hasher.py
**Versão:** 2.1.0  
**Status:** stable (produção)  
**Fonte:** [app/utils/hasher.py](https://github.com/emangue/FinUp/tree/main/app/utils/hasher.py)

**Funções principais:**
- `fnv1a_64_hash(text)` - Gera hash FNV-1a 64-bit 
- `generate_id_transacao(data, estabelecimento, valor)` - Gera IdTransacao único para transações
- `generate_id_simples(data, estabelecimento, valor)` - Hash simples compatível com n8n

**Uso:**
```python
from hasher import generate_id_transacao

id_trans = generate_id_transacao('01/01/2025', 'IFOOD', -125.50)
# Retorna: "12345678901234567" (hash FNV-1a 64-bit)
```

**Características:**
- Hash determinístico (mesma entrada = mesmo hash)
- Colisão extremamente rara (2^64 possibilidades)
- Performance: ~100 nanossegundos por hash
- Tratamento de colisões com sufixo `_1`, `_2`, etc

---

### 🔤 normalizer.py
**Versão:** 3.0.0  
**Status:** stable (produção)  
**Fonte:** [app/utils/normalizer.py](https://github.com/emangue/FinUp/tree/main/app/utils/normalizer.py)

**Funções principais:**
- `normalizar(texto)` - Normalização completa (remove acentos, upper, remove especiais)
- `normalizar_estabelecimento(estabelecimento)` - Remove parcelas XX/YY e normaliza
- `tokens_validos(texto)` - Extrai tokens significativos (remove stop words)
- `detectar_parcela(estabelecimento, origem)` - Detecta formato de parcela (10/12)
- `get_faixa_valor(valor)` - Segmenta valores em faixas
- `arredondar_2_decimais(valor)` - Arredonda para 2 casas decimais

**Uso:**
```python
from normalizer import normalizar_estabelecimento, detectar_parcela

# Normalização
estab = normalizar_estabelecimento("LOJA XYZ (10/12)")
# Retorna: "loja xyz"

# Detecção de parcela
info = detectar_parcela("LOJA XYZ (10/12)")
# Retorna: {'parcela': 10, 'total': 12}
```

**Processo de normalização:**
1. Remove informações de parcela: `"LOJA 10/10"` → `"LOJA"`
2. Converte para minúsculas: `"LOJA"` → `"loja"`
3. Remove caracteres especiais: `"LOJA*XYZ"` → `"loja xyz"`
4. Normaliza espaços: `"LOJA    XYZ"` → `"loja xyz"`

---

### 🔍 deduplicator.py
**Versão:** 2.1.0  
**Status:** stable (produção)  
**Fonte:** [app/utils/deduplicator.py](https://github.com/emangue/FinUp/tree/main/app/utils/deduplicator.py)

**Funções principais:**
- `deduplicate_transactions(transactions)` - Deduplica lista de transações contra banco
- `get_duplicados_temp()` - Recupera duplicados temporários armazenados
- `clear_duplicados_temp()` - Limpa tabela de duplicados temporários
- `get_duplicados_count()` - Conta quantidade de duplicados temporários

**Estratégias de Deduplicação:**
1. **IdTransacao exato:** Hash FNV-1a 64-bit já existe em `journal_entries`
2. **Base de Parcelas:** Para parceladas, verifica se `parcela_atual <= qtd_pagas`
3. **Data + Valor + Estabelecimento:** Para extratos, compara similaridade de nomes

**Uso:**
```python
from deduplicator import deduplicate_transactions, clear_duplicados_temp

# Deduplica transações
transacoes = [
    {'IdTransacao': '12345...', 'Data': '01/12/2025', 'Estabelecimento': 'UBER', 'Valor': -35.50},
    # ... mais transações
]

transacoes_unicas, duplicados_count = deduplicate_transactions(transacoes)
# transacoes_unicas: Lista sem duplicatas
# duplicados_count: 5 (quantidade removida)

# Após processar, limpar duplicados temporários
clear_duplicados_temp()
```

**⚠️ IMPORTANTE:** 
- Requer conexão com banco de dados SQLite (`financas.db`)
- Depende de `models.py` (JournalEntry, DuplicadoTemp, BaseParcelas)
- Usado extensivamente em `app/blueprints/upload/routes.py`
- **Bug conhecido:** Detecção de duplicatas no extrato Mercado Pago pode falhar em alguns casos

**Tabela Temporária:**
- `duplicados_temp`: Armazena duplicados detectados durante upload
- Campos: IdTransacao, Data, Estabelecimento, Valor, origem, motivo_duplicacao, created_at

---

## 🔗 Arquivos Conectados

Estes arquivos trabalham juntos em uma cadeia de dependências:

```
deduplicator.py
  ↓ depende de
hasher.py + models.py (JournalEntry, DuplicadoTemp, BaseParcelas)
  ↓ depende de
normalizer.py
  ↓ usa
re, unicodedata (Python stdlib)
```

**Ordem de Importação Recomendada:**
1. `normalizer.py` (sem dependências externas exceto stdlib)
2. `hasher.py` (depende de normalizer)
3. `deduplicator.py` (depende de hasher + models + banco)

**Uso em produção:**
- `app/blueprints/upload/routes.py` - Rota `/processar_confirmados` (linha 395-431)
- `app/blueprints/upload/processors/fatura_cartao.py` - Processamento de faturas
- `app/blueprints/upload/processors/extrato_conta.py` - Processamento de extratos
- `scripts/populate_id_parcela.py` - Migração de parcelas
- `scripts/fix_id_parcela_case.py` - Correção de case sensitivity

---

## 📊 Sistema Completo de Processamento

### Fluxo de Upload (Visão Geral)

```
1. Arquivo Enviado (CSV/XLS)
   ↓
2. Preprocessador (detecção automática de banco)
   ↓
3. Processador (fatura_cartao.py ou extrato_conta.py)
   ↓ gera hashes usando hasher.py
4. Deduplicação (deduplicator.py)
   ↓ remove duplicatas
5. Classificação Automática (pattern_generator.py)
   ↓
6. Revisão Manual (revisao_upload.html)
   ↓
7. Salvamento (journal_entries)
   ↓ limpa duplicados_temp
8. Regeneração de Padrões (pattern_generator.py)
```

### IdTransacao (FNV-1a 64-bit)
- **Entrada:** `data + estabelecimento_normalizado + valor`
- **Exemplo:** `"01/01/2025|IFOOD|-125.50"` → `"12345678901234567"`
- **Uso:** Identificador único de cada transação

### IdParcela (MD5 16-char)
- **Entrada:** `estabelecimento_normalizado + valor + total_parcelas`
- **Exemplo:** `"loja xyz|100.00|10"` → `"abc123def456"`
- **Uso:** Agrupar todas as parcelas da mesma compra

---

## 🛠️ Como Usar Estes Códigos

### Opção 1: Referência
Use como referência para entender a lógica de hash, normalização e deduplicação do sistema em produção.

### Opção 2: Importação Direta (hasher + normalizer apenas)
```python
import sys
sys.path.append('/path/to/codigos_apoio')

from hasher import generate_id_transacao
from normalizer import normalizar_estabelecimento

# Usar normalmente
id_trans = generate_id_transacao('01/01/2025', 'IFOOD', -125.50)
```

**⚠️ ATENÇÃO:** `deduplicator.py` **NÃO** pode ser usado standalone. Requer:
- Banco de dados SQLite (`financas.db`) configurado
- `models.py` com SQLAlchemy models
- Tabelas: `journal_entries`, `duplicados_temp`, `base_parcelas`

### Opção 3: Copiar para Projeto
Copie os arquivos para o diretório do seu projeto e adapte conforme necessário.

**Para usar deduplicator.py:**
1. Configure banco de dados SQLite
2. Copie `models.py` ou crie models equivalentes
3. Ajuste imports: `from app.models import ...` → `from models import ...`
4. Teste extensivamente antes de usar em produção

---

## 📝 Histórico de Mudanças

### deduplicator.py
- **2.1.0 (27/12/2025):** Versão estável em produção
  - 3 estratégias de deduplicação (IdTransacao, Parcelas, Data+Valor)
  - Tabela temporária `duplicados_temp`
  - 4 funções públicas
  - ⚠️ Bug conhecido: Mercado Pago pode não detectar duplicatas em alguns casos

### hasher.py
- **2.0.0 (26/12/2025):** Migração de MD5 para FNV-1a 64-bit (correção bug colisão VPD)
- **2.1.0 (27/12/2025):** Sistema de versionamento implementado

### normalizer.py
- **3.0.0 (27/12/2025):** Simplificação - preprocessamento movido para utils/

---

## ⚠️ Avisos Importantes

1. **Arquivos Críticos:** 
   - `hasher.py` é arquivo crítico que requer versionamento obrigatório
   - `deduplicator.py` é arquivo crítico que requer versionamento obrigatório
   - Mudanças afetam a integridade dos dados

2. **Dependências:** 
   - `hasher.py` depende de `normalizer.py`
   - `deduplicator.py` depende de `hasher.py` + `models.py` + banco de dados
   - Sempre mantenha sincronizados

3. **Compatibilidade:** 
   - Estes arquivos são do código em **produção**
   - Use com cuidado ao adaptar para ambientes de desenvolvimento
   - Teste extensivamente antes de modificar

4. **Hash Consistency:** 
   - O hash FNV-1a garante que a mesma transação sempre gere o mesmo ID
   - Essencial para evitar duplicatas
   - **NUNCA** mude a lógica de hash sem migração completa do banco

5. **Deduplicação:** 
   - Sistema de 3 camadas (IdTransacao, Parcelas, Data+Valor)
   - Duplicados armazenados em tabela temporária
   - Limpar `duplicados_temp` após processar cada upload

---

## 📚 Documentação Relacionada

**No repositório principal (FinUp):**
- [ESTRUTURA_PROJETO.md](https://github.com/emangue/FinUp/tree/main/docs/ESTRUTURA_PROJETO.md) - Arquitetura completa
  - Seção "4. Deduplicação" (linhas 286-328)
  - Seção "Sistema de Hashing" (linhas 902-925)
- [BUGS.md](https://github.com/emangue/FinUp/tree/main/docs/BUGS.md#L85-L119) - Bug conhecido de deduplicação Mercado Pago
- [app/blueprints/upload/routes.py](https://github.com/emangue/FinUp/tree/main/app/blueprints/upload/routes.py#L395-L431) - Uso de deduplicate_transactions() no upload
- [app/blueprints/upload/processors/fatura_cartao.py](https://github.com/emangue/FinUp/tree/main/app/blueprints/upload/processors/fatura_cartao.py) - Uso em processadores
- [scripts/populate_id_parcela.py](https://github.com/emangue/FinUp/tree/main/scripts/populate_id_parcela.py) - Migração de parcelas

**Templates Relacionados:**
- [duplicados.html](https://github.com/emangue/FinUp/tree/main/app/blueprints/upload/templates/duplicados.html) - Visualização de duplicados
- [revisao_upload.html](https://github.com/emangue/FinUp/tree/main/app/blueprints/upload/templates/revisao_upload.html) - Contador de duplicados

---

## 🔍 Troubleshooting

### Problema: deduplicator.py não funciona
**Causa:** Falta de dependências (models.py ou banco de dados)  
**Solução:** 
```bash
# Verificar se banco existe
ls -la financas.db

# Testar conexão
python -c "from app.models import get_db_session; print(get_db_session())"
```

### Problema: Duplicatas não detectadas
**Causa:** Hash inconsistente ou formato de arquivo não suportado  
**Solução:** 
- Verificar se preprocessador está detectando banco corretamente
- Checar logs de hash generation
- Ver [BUGS.md](https://github.com/emangue/FinUp/tree/main/docs/BUGS.md#L85-L119) para bugs conhecidos

### Problema: ImportError no hasher.py
**Causa:** normalizer.py não encontrado  
**Solução:** 
```python
# Ajustar import
from normalizer import normalizar  # Se no mesmo diretório
# ou
from app.utils.normalizer import normalizar  # Se em app/utils/
```

---

**Data de Extração:** 04/01/2026  
**Repositório:** https://github.com/emangue/FinUp  
**Branch:** main (produção)  
**Arquivos Extraídos:** hasher.py, normalizer.py, deduplicator.py
