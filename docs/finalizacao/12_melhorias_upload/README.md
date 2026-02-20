# 🚀 Frente 12: Melhorias Futuras - Upload

**Status:** 📋 Backlog (Futuro)  
**Prioridade:** 🟢 BAIXA  
**Ordem Recomendada:** ❌ Não prioritário - fazer após todas as frentes críticas  

---

## 🎯 Objetivo

Centralizar todas as melhorias, testes aprofundados e features avançadas do sistema de upload para serem implementadas em versões futuras do sistema.

**Por quê adiar?** Upload já está 96% funcional - focar em finalizar sistema básico primeiro.

---

## 📋 Melhorias Planejadas

### 1. Testes Múltiplos de Upload (Learning)

**Objetivo:** Validar aprendizado progressivo da base_padroes

**Plano:**
- 3 uploads MercadoPago (MP202501, MP202502, MP202503)
- 3 uploads Itaú (fatura_itau-202510, 202511, 202512)
- Medir evolução: 0% → 17% → 27% Base Padrões

**Documentação criada:**
- `PASSO_A_PASSO_TESTES_UPLOAD.md` (800+ linhas)
- `test_uploads_automated.sh` (300+ linhas bash)

**Validações SQL por upload:**
- Total transações, padrões, parcelas
- Top 5 padrões mais frequentes
- Origem classificação (Genérica/Padrões/Não Classificado)
- Parcelas ativas vs finalizadas
- Dashboard queries
- Final evolution report

---

### 2. Base de Bancos (Formatos)

**Objetivo:** Conexão dinâmica tela upload ↔ base de bancos

**Features:**
- Auto-detectar banco baseado em formato do arquivo
- Exibir formatos disponíveis por banco (OK, WIP, TBD)
- Mensagem clara se formato não suportado
- Guia visual de como exportar arquivo correto

**Benefício:** Melhor UX para usuário iniciante

---

### 3. Preview - Botão "+"

**Objetivo:** Adicionar grupos/subgrupos diretamente da preview

**Features:**
- Botão "+" na preview de transações
- Modal rápido para criar novo grupo/subgrupo
- Aplicar automaticamente na transação atual
- Atualizar base_generica ou base_padroes

**Benefício:** Usuário não precisa sair da preview para criar grupos

---

### 4. Filtro Classificados/Não Classificados

**Objetivo:** Melhorar filtro na preview

**Features:**
- Toggle "Apenas não classificados"
- Contador atualizado em tempo real
- Scroll automático para próximo não classificado
- Highlight visual de transações pendentes

**Benefício:** Facilitar revisão de transações

---

### 5. Mapeamento de Atualização de Bases

**Objetivo:** Entender quando/como bases são atualizadas

**Investigações:**
- base_generica: atualizada manualmente ou via admin?
- base_padroes: regenerada a cada upload (Fase 0 ✅)
- base_grupos_config: atualizada quando?
- base_bancos: quem mantém?

**Documentação:**
- Fluxo de atualização de cada base
- Responsabilidades (admin/usuário/sistema)
- Frequência de atualização

---

### 6. Subgrupo Inteligente por Banco

**Objetivo:** Auto-preencher subgrupo baseado em banco + estabelecimento

**Lógica proposta:**
```python
if grupo == "Investimentos":
    if banco == "MercadoPago":
        subgrupo = "Conta Digital"  # ou analisa description
    elif banco == "Itaú":
        subgrupo = "Poupança"
    elif banco in ["BTG", "XP"]:
        subgrupo = "Corretora"
```

**Alternativas:**
- Usar padrões de estabelecimento (Sanchez Dare → Transferência)
- Criar tabela banco_subgrupo_mapping
- Machine learning em cima de base_padroes

---

### 7. Validação de Formato de Arquivo

**Objetivo:** Validar estrutura do arquivo antes de processar

**Features:**
- Detectar colunas obrigatórias por banco
- Validar tipos de dados (datas, valores)
- Mensagem clara se arquivo inválido
- Sugestão de correção

**Benefício:** Evitar uploads que vão falhar

---

### 8. Histórico de Upload (já está na Frente 11)

**Nota:** Painel de uploads já está planejado na Frente 11  
Não duplicar - apenas referenciar

---

### 9. Testes de Performance

**Objetivo:** Validar performance com arquivos grandes

**Cenários:**
- Upload de 500+ transações
- Upload de 5 arquivos simultâneos
- Classificação em massa (1000+ transações)
- Regeneração de base_padroes com 10k registros

**Métricas:**
- Tempo de upload (< 5s)
- Tempo de preview (< 2s)
- Tempo de confirmação (< 3s)
- Uso de memória (< 500MB)

---

### 10. Testes de Casos Extremos

**Objetivo:** Validar edge cases

**Cenários:**
- Arquivo com 0 transações
- Arquivo com transações duplicadas (100%)
- Arquivo com formato inválido
- Arquivo com caracteres especiais
- Arquivo com datas futuras/passadas extremas
- Arquivo com valores negativos/zero
- Usuário com 0 grupos configurados
- Upload durante outro upload em andamento

---

## 📊 Documentação Existente

**Arquivos criados (mover para esta pasta):**

1. **PASSO_A_PASSO_TESTES_UPLOAD.md** (800+ linhas)
   - 6 uploads sequenciais com validações
   - 7 seções de funcionalidades completas
   - Checklist de 40+ itens
   - Template de relatório

2. **test_uploads_automated.sh** (300+ linhas bash)
   - Login e token management
   - 6 uploads com preview+confirm
   - Validações SQL após cada upload
   - Dashboard e transaction tests
   - Geração de relatório final

3. **VALIDACAO_CAMPOS_COMPLETA.md**
   - Análise de 28 campos de JournalEntry
   - Validação campo por campo
   - 27/28 funcionando (categoria_orcamento_id nullable)

4. **MAPEAMENTO_UPLOAD.md**
   - Fluxo completo com Fase 0
   - Classificação 3 níveis
   - Deduplicação

5. **RESUMO_VALIDACAO_UPLOAD.md**
   - Resumo executivo
   - Upload está 96% funcional

---

## 🎯 Quando Executar

**Depois de:**
- ✅ Todas as 11 frentes críticas concluídas
- ✅ Sistema em produção e estável
- ✅ Feedback de usuários reais coletado
- ✅ Bugs críticos corrigidos

**Priorizar se:**
- Usuários reportarem problemas com upload
- Taxa de erro de classificação > 30%
- Performance degradar (upload > 10s)
- Novos bancos precisarem ser suportados

---

## 📅 Estimativa de Tempo

**Se todas as melhorias forem implementadas:**
- Sub-frente 1 (Testes): 4-5h
- Sub-frente 2 (Base Bancos): 2-3h
- Sub-frente 3 (Botão +): 3-4h
- Sub-frente 4 (Filtros): 2h
- Sub-frente 5 (Mapeamento): 2h
- Sub-frente 6 (Subgrupo): 2-3h
- Sub-frente 7 (Validação): 3h
- Sub-frente 9 (Performance): 3h
- Sub-frente 10 (Edge cases): 4h

**Total:** ~25-30h (3-4 dias)

---

## 🚨 Nota Importante

**Esta frente é BACKLOG.** Não deve ser executada agora.

**Foco atual:** Finalizar sistema básico (Frentes 1-11)

**Revisitar:** Após v1.0 em produção

---

**Última Atualização:** 13/02/2026  
**Motivo:** Separar melhorias futuras de fixes críticos (upload já 96% funcional)
