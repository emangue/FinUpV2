# 📚 Códigos de Apoio - Sistema de Hash e Normalização

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

## 🔗 Arquivos Conectados

Estes arquivos trabalham juntos:

- **hasher.py** depende de **normalizer.py**:
  - `generate_id_transacao()` usa `normalizar()`
  - `generate_id_simples()` usa `normalizar_estabelecimento()`

- **Uso em produção:**
  - `app/blueprints/upload/processors/fatura_cartao.py`
  - `app/blueprints/upload/processors/extrato_conta.py`
  - `scripts/populate_id_parcela.py`
  - `scripts/fix_id_parcela_case.py`

---

## 📊 Sistema de Hashing Completo

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
Use como referência para entender a lógica de hash e normalização do sistema em produção.

### Opção 2: Importação Direta
```python
import sys
sys.path.append('/path/to/codigos_apoio')

from hasher import generate_id_transacao
from normalizer import normalizar_estabelecimento

# Usar normalmente
id_trans = generate_id_transacao('01/01/2025', 'IFOOD', -125.50)
```

### Opção 3: Copiar para Projeto
Copie os arquivos para o diretório do seu projeto e adapte conforme necessário.

---

## 📝 Histórico de Mudanças

### hasher.py
- **2.0.0 (26/12/2025):** Migração de MD5 para FNV-1a 64-bit (correção bug colisão VPD)
- **2.1.0 (27/12/2025):** Sistema de versionamento implementado

### normalizer.py
- **3.0.0 (27/12/2025):** Simplificação - preprocessamento movido para utils/

---

## ⚠️ Avisos Importantes

1. **Arquivo Crítico:** `hasher.py` é arquivo crítico que requer versionamento obrigatório. Mudanças afetam a integridade dos dados.

2. **Dependências:** `hasher.py` depende de `normalizer.py`. Sempre mantenha ambos sincronizados.

3. **Compatibilidade:** Estes arquivos são do código em **produção**. Use com cuidado ao adaptar para ambientes de desenvolvimento.

4. **Hash Consistency:** O hash FNV-1a garante que a mesma transação sempre gere o mesmo ID, essencial para evitar duplicatas.

---

## 📚 Documentação Relacionada

- **ESTRUTURA_PROJETO.md** - Seção "Conceitos Importantes > Sistema de Hashing"
- **BUGS.md** - Bug VPD IdParcela Collision (resolvido com hasher v2.0.0)
- **CHANGELOG.md** - Histórico completo de mudanças

---

**Data de Extração:** 04/01/2026  
**Repositório:** https://github.com/emangue/FinUp  
**Branch:** main (produção)
