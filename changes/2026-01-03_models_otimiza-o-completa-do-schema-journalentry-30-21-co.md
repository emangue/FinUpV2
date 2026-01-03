# Mudança: Otimização completa do schema JournalEntry (30→21 colunas): Remove campos obsoletos, adiciona arquivo_origem/origem_classificacao/banco_origem/MesFatura, atualiza processors e models

**Arquivo:** `app/models.py`  
**Versão:** `3.0.1` → `3.0.2`  
**Data:** 03/01/2026 12:31  
**Autor:** Sistema Automático

---

## 📝 Descrição

Otimização completa do schema JournalEntry (30→21 colunas): Remove campos obsoletos, adiciona arquivo_origem/origem_classificacao/banco_origem/MesFatura, atualiza processors e models

## 📂 Arquivos Modificados

- `app/models.py`

## 🔄 Mudanças Realizadas

<!-- Descrever mudanças detalhadamente -->

- [ ] Adicionar detalhes das mudanças aqui

## 🧪 Testes Realizados

<!-- Descrever testes executados -->

- [ ] Adicionar testes aqui

## 💥 Impacto

<!-- Descrever possíveis impactos -->

- [ ] Breaking changes? Sim/Não
- [ ] Requer migração de banco? Sim/Não
- [ ] Afeta outras funcionalidades? Sim/Não

## 🔙 Rollback

Para reverter esta mudança:

```bash
# Checkout para versão anterior
git checkout v3.0.1 -- app/models.py

# Ou rollback completo
python scripts/version_manager.py rollback v3.0.1
```

## 🔗 Relacionado

- Issue: #
- PR: #
- Documentação: 

---

**Nota:** Este arquivo foi gerado automaticamente. Complete as seções pendentes.
