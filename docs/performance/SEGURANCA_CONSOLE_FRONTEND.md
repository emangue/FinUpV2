# Segurança — Console Logs e Exposição de Dados no Frontend

**Data:** 01/03/2026
**Contexto:** DevTools do app exibindo dados financeiros reais no console (valores, totais, parâmetros de API). Risco de exposição identificado.

---

## 1. O Problema

A screenshot do DevTools mostra:

```
useExpenseSources – Dados recebidos: {sources: Array(6), total_despesas: 32016.43}
useExpenseSources – Buscando despesas: {year: 2026, month: 3}
useExpenseSources – Total: 32016.43
```

Isso significa que **dados financeiros reais estão sendo impressos no console do browser**, acessíveis a qualquer pessoa que abra o DevTools na máquina do usuário.

Além disso, o DevTools mostra **393 network requests** e **36.5s de finish time** — ambos sintomas dos gargalos de backend já mapeados em `PERFORMANCE_OPORTUNIDADES.md`.

---

## 2. Por Que Isso É um Risco

### 2.1 Acesso físico / shoulder surfing
Se alguém estiver olhando a tela do usuário e abrir DevTools → Console, vê imediatamente os valores financeiros sem precisar fazer login.

### 2.2 Extensões de browser maliciosas
Extensões com permissão de `scripting` podem ler o console programaticamente. Um usuário que instale uma extensão comprometida expõe todos os logs.

### 2.3 XSS (Cross-Site Scripting)
Se houver uma vulnerabilidade XSS no app (injeção de script via dados do usuário), o atacante pode executar `console.log` hijacking e capturar tudo que foi logado na sessão.

### 2.4 Reconhecimento da API
Os logs expõem:
- Estrutura dos objetos retornados pela API (`sources: Array(6)`, `total_despesas`)
- Parâmetros exatos das chamadas (`year: 2026, month: 3`)
- Volume de dados (Array com 6 fontes)
- Padrão de nomes internos (`useExpenseSources`)

Um atacante consegue mapear toda a API sem sequer interceptar tráfego.

### 2.5 Chamadas duplicadas visíveis
O log mostra `useExpenseSources – Buscando despesas: {year: 2026, month: 3}` **duas vezes seguidas** — além do risco de segurança, isso confirma que o hook está sendo executado múltiplas vezes desnecessariamente (problema de performance frontend).

---

## 3. Regra Geral

```
Em produção: console deve estar VAZIO.
Em desenvolvimento: pode logar, mas NUNCA dados financeiros, nunca PII.
```

**O que nunca pode aparecer no console (em nenhum ambiente):**
- Valores monetários reais
- Dados pessoais (nome, CPF, email)
- Tokens de autenticação ou cookies
- Respostas completas de API com dados do usuário

---

## 4. Fix — Como Resolver

### 4.1 Remover todos os console.log com dados sensíveis

Localizar todas as ocorrências no frontend:

```bash
grep -r "console.log" app_dev/frontend/src --include="*.ts" --include="*.tsx" -l
```

Para cada ocorrência que imprime dados de API ou valores financeiros: **remover**.

### 4.2 Gating por ambiente (para logs de debug que têm valor)

Se algum log for útil durante desenvolvimento, gatear por `NODE_ENV`:

```typescript
// utils/logger.ts
const isDev = process.env.NODE_ENV === 'development';

export const logger = {
  debug: (...args: unknown[]) => { if (isDev) console.log(...args); },
  // Nunca logar dados financeiros mesmo em dev — usar IDs, contagens
};
```

Substituir todos os `console.log` nos hooks de dados por `logger.debug`.

### 4.3 Remover automaticamente em build de produção (Next.js)

No `next.config.js`, adicionar configuração que remove console automaticamente no build:

```javascript
// next.config.js
const nextConfig = {
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production'
      ? { exclude: ['error', 'warn'] }  // mantém só error e warn
      : false,
  },
};
```

Isso elimina todos os `console.log` e `console.debug` no bundle de produção. `console.error` e `console.warn` são mantidos para monitoramento legítimo.

### 4.4 Corrigir chamadas duplicadas do useExpenseSources

O hook está sendo chamado duas vezes para os mesmos parâmetros. Isso indica:
- Componente pai re-renderizando desnecessariamente
- Dependências do `useEffect` mal configuradas
- Falta de `useMemo` ou `useCallback` nas props passadas para o componente

```typescript
// Verificar se o hook tem dependências corretas
useEffect(() => {
  fetchExpenses(year, month);
}, [year, month]); // garantir que year e month são primitivos, não objetos
```

---

## 5. O Que Verificar nas Migrations/Auth

Além dos console logs, outros pontos de segurança para revisar:

| Item | Risco | Status |
|------|-------|--------|
| `user_id` ausente em queries de grupos/marcações | Dados cruzados entre usuários | ⚠️ Aberto (ver PERFORMANCE_OPORTUNIDADES.md) |
| Tokens JWT no localStorage | XSS rouba token facilmente | Verificar — preferir httpOnly cookie |
| Rotas de API sem autenticação | Acesso não autorizado | Verificar middleware de auth |
| Dados sensíveis em URL params | Aparecem em logs de servidor | Verificar endpoints |
| CORS configurado corretamente | Requisições de origens não autorizadas | Verificar config FastAPI |

---

## 6. Plano de Ação

| Prioridade | Ação | Esforço |
|------------|------|---------|
| 1 | Adicionar `removeConsole` no `next.config.js` de produção | 15min |
| 2 | Grep e remover/substituir console.logs com dados financeiros | 1h |
| 3 | Criar `utils/logger.ts` e padronizar logs de debug | 30min |
| 4 | Investigar e corrigir chamadas duplicadas do `useExpenseSources` | 1h |
| 5 | Revisar queries sem `user_id` (ver PERFORMANCE_OPORTUNIDADES.md seção 2) | 30min |

**Total estimado:** ~3h para eliminar os riscos de exposição.

---

## 7. Regra para o Futuro

```typescript
// ❌ NUNCA — dados reais no console
console.log('Dados recebidos:', { total_despesas: valor, sources: dados });
console.log('Token:', authToken);
console.log('Response:', apiResponse);

// ✅ SE PRECISAR logar algo — apenas metadata, nunca conteúdo
logger.debug('useExpenseSources: fetch concluído', { count: dados.length });
logger.debug('useExpenseSources: parâmetros', { year, month });
//                                              ^^ primitivos, sem valores financeiros
```
