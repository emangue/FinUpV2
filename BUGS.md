# 🐛 Bugs Conhecidos - FinUpV2

**Data:** 04/01/2026

## 🔴 Bugs Críticos

### 1. Switch de Transações Não Funciona
**Descrição:** O switch na coluna "Dashboard" da tabela de transações não está alternando o valor de `IgnorarDashboard` quando clicado.

**Localização:**
- Frontend: [app_dev/frontend/src/app/transactions/page.tsx](app_dev/frontend/src/app/transactions/page.tsx#L427)
- Backend: [app_dev/backend/app/routers/transactions.py](app_dev/backend/app/routers/transactions.py) (PATCH endpoint)

**Comportamento Esperado:**
- Clicar no switch deve alternar entre 0 (incluir no dashboard) e 1 (ignorar no dashboard)
- A atualização deve ser refletida imediatamente na UI
- O total deve ser recalculado após a mudança

**Comportamento Atual:**
- O switch não responde ao clique
- Nenhuma atualização é enviada ao backend

**Próximos Passos:**
- [ ] Verificar se o endpoint PATCH está funcionando (testar com curl)
- [ ] Verificar console do navegador para erros JavaScript
- [ ] Validar se `handleToggleIgnorar` está sendo chamado corretamente
- [ ] Verificar se há problema com propagação de eventos (`onClick` no TableCell)

---

## 🟡 Bugs Médios

### 2. Transações de Transferência Não Aparecem na Aba Superior
**Descrição:** A aba "Transferências" no topo da página não exibe nenhuma transação quando clicada, mas se o usuário usar os filtros detalhados e selecionar tipo "Transferência", as transações aparecem corretamente.

**Localização:**
- Frontend: [app_dev/frontend/src/app/transactions/page.tsx](app_dev/frontend/src/app/transactions/page.tsx#L340-L365)
- Backend: Query de filtros em `transactions.py`

**Comportamento Esperado:**
- Clicar na aba "Transferências" deve exibir todas as transações com `TipoTransacao = "Transferência"`
- O total deve refletir apenas as transferências
- A contagem de transações deve aparecer

**Comportamento Atual:**
- **Clicar na aba "Transferências"**: Nenhuma transação aparece (página vazia)
- **Usar filtro detalhado com tipo "Transferência"**: Funciona corretamente e mostra as transações
- Inconsistência entre aba superior e filtros detalhados

**Próximos Passos:**
- [ ] Verificar lógica da aba "Transferências" vs filtros detalhados
- [ ] Comparar parâmetros enviados ao backend em ambos os casos
- [ ] Validar se o valor de `tipo_transacao` está sendo enviado corretamente
- [ ] Verificar se campo `TipoTransacao` no banco usa "Transferência" ou "Transferencias"
- [ ] Ajustar mapeamento entre aba clicada e valor do filtro enviado ao backend

---

## 🟡 Bugs Médios

### 3. Upload Não Atualiza Base de Preview
**Descrição:** Quando um novo arquivo é enviado para upload, os dados antigos de preview não são limpos/substituídos corretamente.

**Localização:**
- Backend: [app_dev/backend/app/routers/upload.py](app_dev/backend/app/routers/upload.py#L78-L83)
- Tabela: `preview_transacoes` no banco SQLite

**Comportamento Esperado:**
- Ao fazer novo upload, todos os registros de preview do usuário devem ser deletados
- Novos dados devem ser inseridos com novo `session_id`
- Frontend deve exibir apenas os dados do upload mais recente

**Comportamento Atual:**
- Dados antigos permanecem no banco
- Possível acúmulo de registros duplicados

**Código Relevante:**
```python
# Linha 78-83 em upload.py
deleted = db.query(PreviewTransacao).filter(
    PreviewTransacao.user_id == user_id
).delete(synchronize_session=False)

if deleted > 0:
    db.commit()
```

**Próximos Passos:**
- [ ] Verificar se o delete está realmente executando
- [ ] Adicionar logs para confirmar quantos registros foram deletados
- [ ] Testar com múltiplos uploads consecutivos
- [ ] Verificar se commit está sendo chamado corretamente
- [ ] Considerar limpar por `session_id` além de `user_id`

---

## 📝 Notas de Desenvolvimento

**Status Atual do Sistema:**
- ✅ Backend rodando na porta 8000
- ✅ Frontend rodando na porta 3000
- ✅ Banco de dados SQLite funcionando
- ✅ Autenticação bypassed para desenvolvimento (user_id=1)

**Últimas Alterações:**
- Removido filtro `IgnorarDashboard=0` das queries (agora mostra todas as transações)
- Simplificado processo de upload (apenas campos básicos)
- Adicionados endpoints de preview: GET, POST confirm, DELETE

**Próxima Sessão de Debug:**
1. Testar switch manualmente com DevTools aberto
2. Validar endpoints de transação com Postman/curl
3. Revisar lógica de eventos no componente Switch
4. Adicionar tratamento para transferências
5. Validar limpeza de preview com logs detalhados

---

## 🔧 Como Reproduzir

### Bug 1 - Switch Não Funciona
1. Acessar http://localhost:3000/transactions
2. Clicar em qualquer switch na coluna "Dashboard"
3. Observar que nada acontece

### Bug 2 - Transferências Não Aparecem na Aba
1. Acessar http://localhost:3000/transactions
2. Verificar que existem transferências na aba "Todas"
3. Clicar na aba "Transferências" no topo
4. Observar que nenhuma transação aparece (página vazia)
5. **Workaround**: Usar o filtro detalhado e selecionar tipo "Transferência" - funciona corretamente

### Bug 3 - Preview Não Limpa
1. Fazer upload de um arquivo CSV de fatura
2. Verificar dados inseridos em `preview_transacoes`
3. Fazer upload de outro arquivo diferente
4. Verificar que dados antigos ainda estão no banco (não foram limpos)

---

**Última atualização:** 04/01/2026 às 23:45
