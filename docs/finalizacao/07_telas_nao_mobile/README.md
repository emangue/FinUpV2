# 7️⃣ Telas Não-Mobile

**Frente:** Telas Não-Mobile  
**Status:** 🔴 Não Iniciado  
**Prioridade:** 🟡 MÉDIA  
**Responsável:** A definir  
**Data Início:** A definir  
**Deadline:** A definir

---

## 🎯 Objetivo

Decidir o que fazer com as telas desktop que não estão sendo utilizadas: remover, adaptar para mobile ou manter.

---

## 📋 Escopo

### Incluído
- ✅ Mapeamento de todas as telas não-mobile
- ✅ Análise de uso/necessidade
- ✅ Decisão por tela (remover/adaptar/manter)
- ✅ Execução das ações decididas
- ✅ Atualização de navegação

### Excluído
- ❌ Criação de novas telas
- ❌ Refatoração de telas mobile existentes

---

## 🔍 Fase 1: Mapeamento de Telas

### 1.1 Identificar Telas Não-Mobile

**Onde procurar:**
```bash
# Frontend - todas as páginas
find app_dev/frontend/src/app -name "page.tsx" -type f

# Verificar quais NÃO têm versão mobile
grep -r "isMobile" app_dev/frontend/src/app --include="*.tsx"
```

### 1.2 Lista de Telas Conhecidas

```markdown
| Tela | Path | Tem Mobile? | Uso Atual |
|------|------|-------------|-----------|
| Dashboard | /dashboard | ✅ Sim | Alto |
| Transações | /transactions | ✅ Sim | Alto |
| Upload | /upload | ✅ Sim | Alto |
| Metas | /budget | ✅ Sim | Médio |
| Configurações | /settings | ✅ Sim | Médio |
| Admin | /admin | ❌ Não | Baixo |
| Relatórios | /reports | ❓ ? | ? |
| Investimentos | /investments | ❓ ? | ? |
| Cartões | /cards | ❓ ? | ? |
```

### 1.3 Categorizar por Status

**✅ Com Mobile (OK):**
- Dashboard
- Transações
- Upload
- Metas
- Configurações

**❌ Sem Mobile (INVESTIGAR):**
- Admin
- Outros?

**🗑️ Não Usadas (CANDIDATAS A REMOÇÃO):**
- Telas antigas da refatoração?
- Telas de teste?

---

## 📊 Fase 2: Análise de Necessidade

### 2.1 Critérios de Decisão

**REMOVER se:**
- Tela não é usada há ≥6 meses
- Funcionalidade já existe em outra tela
- Tela era de teste/desenvolvimento
- Custo de manutenção > benefício

**ADAPTAR se:**
- Funcionalidade é importante
- Usuários precisam acessar via mobile
- Tela é usada ocasionalmente
- Adaptação é viável (não muito complexa)

**MANTER (desktop only) se:**
- Funcionalidade é crítica MAS
- Uso é exclusivo de admin/desktop
- Adaptação para mobile não faz sentido
- Ex: relatórios complexos, configurações avançadas

### 2.2 Template de Análise

**Por cada tela não-mobile:**
```markdown
### Tela: [Nome]
**Path:** [caminho]
**Última Modificação:** [data]
**Uso Atual:** [frequência]

**Funcionalidades:**
- Feature 1
- Feature 2

**Análise:**
- [ ] Funcionalidade ainda é necessária?
- [ ] Há tela equivalente mobile?
- [ ] Pode ser adaptada facilmente?
- [ ] Custo vs benefício de manter?

**Decisão:** [ ] Remover / [ ] Adaptar / [ ] Manter

**Justificativa:**
[explicar decisão]

**Ação:** [se aplicável]
```

---

## 🛠️ Fase 3: Execução

### 3.1 Remoção de Telas

**Processo de remoção:**
```bash
# 1. Identificar todos os arquivos relacionados
find app_dev/frontend/src -name "*nome-tela*"

# 2. Verificar dependências
grep -r "import.*nome-tela" app_dev/frontend/src

# 3. Remover arquivos
rm -rf app_dev/frontend/src/app/nome-tela

# 4. Remover rotas
# Editar app/layout.tsx ou nav-main.tsx

# 5. Remover APIs backend (se específicas desta tela)
# Editar app/domains/*/router.py

# 6. Testar que nada quebrou
npm run build
```

**Checklist por tela removida:**
- [ ] Arquivos deletados
- [ ] Rotas removidas da navegação
- [ ] Imports atualizados
- [ ] APIs backend removidas (se não usadas)
- [ ] Build passa sem erros
- [ ] Testes passam (se existirem)

### 3.2 Adaptação para Mobile

**Processo de adaptação:**
```typescript
// Exemplo: Adaptar tela desktop para mobile

// 1. Criar versão mobile do componente
// src/features/admin/components/admin-mobile.tsx
export function AdminMobile() {
  return (
    <div className="mobile-layout">
      {/* Layout adaptado para mobile */}
    </div>
  )
}

// 2. Detectar dispositivo e renderizar apropriadamente
// src/app/admin/page.tsx
export default function AdminPage() {
  const isMobile = useMediaQuery('(max-width: 768px)')
  
  return isMobile ? <AdminMobile /> : <AdminDesktop />
}
```

**Checklist por tela adaptada:**
- [ ] Componente mobile criado
- [ ] Detecção de dispositivo funcionando
- [ ] Layout mobile responsivo
- [ ] Funcionalidades principais mantidas
- [ ] Navegação mobile integrada
- [ ] Testado em dispositivo real

### 3.3 Manter Desktop Only

**Se decisão for manter:**
```typescript
// Adicionar aviso em mobile
export default function DesktopOnlyPage() {
  const isMobile = useMediaQuery('(max-width: 768px)')
  
  if (isMobile) {
    return (
      <div className="p-6 text-center">
        <h2>Esta funcionalidade está disponível apenas em desktop</h2>
        <p>Acesse em um computador para usar esta tela.</p>
        <Button onClick={goBack}>Voltar</Button>
      </div>
    )
  }
  
  return <DesktopFeature />
}
```

**Checklist:**
- [ ] Aviso mobile implementado
- [ ] Botão de voltar funciona
- [ ] Desktop continua funcionando normalmente
- [ ] Documentação atualizada

---

## 📋 Decisões por Tela

### Admin
**Status:** ❌ Sem Mobile  
**Uso:** Baixo (apenas administradores)  
**Decisão:** 🎯 **A DEFINIR**

**Opções:**
1. **Adaptar:** Criar telas mobile admin (ver frente 8)
2. **Manter desktop only:** Aviso em mobile
3. **Remover:** Se funcionalidades não são essenciais

**Recomendação:** Adaptar (criar mobile) - ver [08_TELAS_ADMIN_MOBILE.md](./08_TELAS_ADMIN_MOBILE.md)

---

### Relatórios (se existir)
**Status:** ❓ A verificar  
**Uso:** ❓ A medir  
**Decisão:** 🎯 **A DEFINIR**

**Análise:**
- [ ] Tela existe?
- [ ] É usada?
- [ ] Funcionalidades são críticas?

---

### Investimentos (se existir)
**Status:** ❓ A verificar  
**Uso:** ❓ A medir  
**Decisão:** 🎯 **A DEFINIR**

**Análise:**
- [ ] Tela existe?
- [ ] É usada?
- [ ] Funcionalidades são críticas?

---

## 🧪 Validação

### Teste de Navegação

**Após remoções/adaptações:**
```markdown
1. [ ] Testar todas as rotas principais
2. [ ] Verificar que links quebrados foram removidos
3. [ ] Testar navegação mobile
4. [ ] Testar navegação desktop
5. [ ] Verificar que botões "voltar" funcionam
6. [ ] Confirmar que nenhuma tela retorna 404
```

### Teste de Build

```bash
# Frontend
cd app_dev/frontend
npm run build

# Deve passar sem erros de imports não encontrados
```

---

## 📊 Métricas

### Progresso
```
Mapeamento:    ░░░░░░░░░░ 0%
Análise:       ░░░░░░░░░░ 0%
Execução:      ░░░░░░░░░░ 0%
Validação:     ░░░░░░░░░░ 0%
TOTAL:         ░░░░░░░░░░ 0%
```

### Decisões
```markdown
| Decisão | Quantidade | % |
|---------|------------|---|
| Remover | 0          | 0%|
| Adaptar | 0          | 0%|
| Manter  | 0          | 0%|
| Pendente| ?          | ? |
```

---

## 🚧 Riscos

1. **Médio:** Remover tela ainda usada acidentalmente
2. **Médio:** Adaptação mobile pode quebrar desktop
3. **Baixo:** Usuários esperarem feature que foi removida

### Mitigações
1. Verificar logs de acesso antes de remover
2. Testar ambos os layouts após adaptação
3. Comunicar mudanças aos usuários

---

## 📝 Próximos Passos

1. [ ] Executar mapeamento completo
2. [ ] Analisar cada tela individualmente
3. [ ] Decidir: remover/adaptar/manter
4. [ ] Executar ações por prioridade
5. [ ] Validar navegação completa
6. [ ] Atualizar documentação

---

## 🔗 Referências

- [PLANO_FINALIZACAO.md](./PLANO_FINALIZACAO.md)
- [08_TELAS_ADMIN_MOBILE.md](./08_TELAS_ADMIN_MOBILE.md) (relacionado)
- [09_VALIDACAO_NAVEGACAO.md](./09_VALIDACAO_NAVEGACAO.md) (relacionado)

---

**Última Atualização:** 10/02/2026
