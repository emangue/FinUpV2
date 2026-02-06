# 📱 Checklist de Teste Mobile - Upload Page

**Data:** 06/02/2026  
**Sprint:** 1.1.3 - Testar responsividade mobile  
**Página:** http://localhost:3000/mobile/upload

---

## 🔗 TESTE RÁPIDO - Abra no seu navegador:

### **Link Direto:**
```
http://localhost:3000/mobile/upload
```

### **Como Testar no Chrome:**

1. **Abrir DevTools:**
   - Pressione `F12` ou `Cmd + Option + I` (Mac)
   - Ou clique direito → Inspecionar

2. **Ativar Device Mode:**
   - Clique no ícone 📱 (Toggle Device Toolbar)
   - Ou pressione `Cmd + Shift + M` (Mac)

3. **Selecionar Dispositivos:**
   - Use o dropdown no topo para escolher:
     - iPhone SE
     - iPhone 14 Pro
     - iPad
   - Ou clique em "Edit..." para adicionar mais dispositivos

---

## ✅ Checklist de Validação

### 📱 **iPhone SE (375 x 667px)** - Tela Pequena

- [ ] **Header** visível e não cortado
- [ ] **Tabs** (Extrato/Fatura) ocupam largura total
- [ ] **Botões Tabs** não ficam espremidos
- [ ] **Labels** (Instituição Financeira, Cartão, etc.) legíveis
- [ ] **Selects** (dropdowns) não cortam texto
- [ ] **Radio buttons** (formatos) têm área clicável boa
- [ ] **Botão "Escolher Arquivo"** visível e clicável
- [ ] **Botão "Importar Arquivo"** ocupa largura total
- [ ] **Bottom Navigation** visível e não sobrepõe conteúdo
- [ ] **Scroll** funciona suavemente
- [ ] **Não há overflow horizontal** (scroll lateral)

### 📱 **iPhone 14 Pro (393 x 852px)** - Tela Média

- [ ] **Layout aproveita** espaço extra
- [ ] **Espaçamentos** proporcionais
- [ ] **Textos** não ficam muito pequenos
- [ ] **Botões** têm tamanho confortável (min 44px altura)
- [ ] **Campos** não ficam muito largos
- [ ] **Bottom Nav** fixa no rodapé

### 📱 **iPad (820 x 1180px)** - Tablet

- [ ] **Layout não fica esticado** demais
- [ ] **Componentes** mantêm proporções adequadas
- [ ] **Considera adicionar max-width** nos containers?
- [ ] **Aproveita espaço** sem parecer "perdido"

---

## 🎯 Critérios de Sucesso

### ✅ **APROVADO** se:
- Todos os elementos são **clicáveis/tocáveis** facilmente
- Não há **overflow horizontal** (scroll lateral indesejado)
- **Textos legíveis** sem zoom (mínimo 14px)
- **Botões** têm área de toque mínima de 44x44px
- **Scroll vertical** suave e sem "jumps"
- **Bottom Nav** sempre visível e não sobrepõe conteúdo

### ⚠️ **ATENÇÃO** se:
- Elementos muito próximos (difícil clicar)
- Textos muito pequenos
- Campos cortados
- Layout "quebrado" em algum tamanho

### ❌ **REPROVADO** se:
- Conteúdo não visível
- Impossível usar em algum dispositivo
- Scroll horizontal forçado
- Botões/campos inacessíveis

---

## 🛠️ Cenários de Teste

### **Cenário 1: Selecionar Extrato**
1. Clique em "Extrato bancário"
2. Selecione um banco
3. Escolha um formato
4. Clique em "Escolher Arquivo"
5. ✅ **Esperado:** Tudo funciona, nada cortado

### **Cenário 2: Selecionar Fatura**
1. Clique em "Fatura Cartão"
2. Selecione um banco
3. Selecione um cartão
4. Escolha mês e ano
5. Escolha formato
6. Clique em "Escolher Arquivo"
7. ✅ **Esperado:** Todos os campos visíveis, formulário completo cabe na tela

### **Cenário 3: Validação de Campos**
1. Deixe campos vazios
2. Clique em "Importar Arquivo"
3. ✅ **Esperado:** Alert aparece corretamente

### **Cenário 4: Navegação Bottom**
1. Scroll até o final
2. Clique nos botões do Bottom Nav
3. ✅ **Esperado:** Botões sempre acessíveis

---

## 📸 Screenshots (Opcional)

Se encontrar problemas, tire print de:
- Layout quebrado
- Elementos cortados
- Overflow horizontal
- Botões inacessíveis

---

## 🔧 Comandos Úteis

```bash
# Verificar se servidores estão rodando
curl http://localhost:3000/mobile/upload
curl http://localhost:8000/api/health

# Reiniciar frontend se necessário
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
./scripts/deploy/quick_stop.sh && ./scripts/deploy/quick_start.sh
```

---

## 📝 Resultado do Teste

**Testado por:** [Seu nome]  
**Data/Hora:** ____/____/____  
**Dispositivos testados:**
- [ ] iPhone SE
- [ ] iPhone 14 Pro  
- [ ] iPad

**Status Final:**
- [ ] ✅ Aprovado - Sem problemas
- [ ] ⚠️ Aprovado com ressalvas - Pequenos ajustes necessários
- [ ] ❌ Reprovado - Precisa correções

**Observações:**
```
[Escreva aqui qualquer problema encontrado]
```

---

## ⏭️ Próximo Sprint

Após aprovação:
- **Sprint 1.1.4** - Commit e push (15min)
- **Sprint 1.2** - Upload Backend (conectar APIs reais)
