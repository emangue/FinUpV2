# 🐛 Bugs Conhecidos - Projeto Finanças V3

Este documento lista bugs identificados que precisam ser corrigidos.

---

## 🔴 Alta Prioridade

### 1. Switch não funciona na tela de Transações
**Localização:** `/dashboard/transacoes?mes=YYYY-MM`

**Descrição:** O switch "Status Dashboard" na tabela de transações não está respondendo aos cliques. Ele deveria alternar o status da transação (ativo/inativo no dashboard).

**Impacto:** Usuários não conseguem ocultar transações do dashboard.

**Arquivos Envolvidos:**
- `templates/transacoes.html`
- `app/blueprints/dashboard/routes.py` (possivelmente falta rota de toggle)
- `static/js/main.js` (JavaScript do switch)

**Possível Causa:** 
- Falta implementação da rota backend para processar o toggle
- JavaScript não está capturando o evento de clique
- URL da requisição AJAX pode estar incorreta após modularização

**Status:** 🔴 Não Corrigido

---

## 🟡 Média Prioridade

_(Nenhum bug nesta categoria no momento)_

---

## 🟢 Baixa Prioridade

_(Nenhum bug nesta categoria no momento)_

---

## ✅ Bugs Resolvidos

_(Lista será populada conforme bugs forem corrigidos)_

---

**Última Atualização:** 26 de dezembro de 2025
