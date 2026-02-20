# 🔧 Plano de Implementação - Fase 6: Atualização base_padroes

**Data:** 13/02/2026  
**Prioridade:** 🔴 CRÍTICA (BLOQUEANTE para testes)  
**Tempo Estimado:** 2-3 horas  
**Objetivo:** Implementar atualização automática de `base_padroes` após confirmar upload

---

## 🎯 Contexto

**Problema identificado:**
- `base_padroes` **NÃO é atualizada** após upload confirmado
- Sistema **NÃO aprende** padrões de valor por estabelecimento
- Classificação futura **menos precisa** (não usa histórico de valores)
- Alertas de valores anormais **não funcionam**

**Impacto:**
- ❌ Usuário não recebe sugestões baseadas em histórico
- ❌ Sistema não detecta valores muito acima/abaixo do padrão
- ❌ Confiança da classificação sempre baixa (sem histórico)

---

## 📋 Análise Técnica

### Estrutura da Tabela `base_padroes`

**Campos principais:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `user_id` | Integer | ID do usuário |
| `padrao_estabelecimento` | Text | Ex: "CONTA VIVO [50-100]" |
| `padrao_num` | Text | Hash único (FNV-1a) |
| `contagem` | Integer | Quantidade de ocorrências |
| `valor_medio` | Float | Média dos valores |
| `valor_min` | Float | Valor mínimo |
| `valor_max` | Float | Valor máximo |
| `desvio_padrao` | Float | Desvio padrão |
| `coef_variacao` | Float | Coeficiente de variação |
| `percentual_consistencia` | Integer | % de consistência |
| `confianca` | Text | 'alta', 'media', 'baixa' |
| `grupo_sugerido` | Text | Grupo mais frequente |
| `subgrupo_sugerido` | Text | Subgrupo mais frequente |
| `faixa_valor` | Text | Ex: "50-100", "FIXO 57.00" |
| `exemplos` | Text | Lista separada por "; " |
| `data_criacao` | DateTime | Data de criação |

---

## 🔧 Implementação

### Localização:
**Arquivo:** `app_dev/backend/app/domains/upload/service.py`  
**Método:** `confirm_upload()` (linha ~730)

---

### PASSO 1: Criar método `_fase6_update_base_padroes()`

**Inserir após `_fase5_update_base_parcelas()` (linha ~1008):**

```python
def _fase6_update_base_padroes(self, user_id: int, upload_history_id: int) -> dict:
    """
    Fase 6: Atualiza base_padroes após confirmar upload
    
    Lógica:
    1. Busca transações do upload com estabelecimento_base
    2. Agrupa por (estabelecimento_base + grupo + subgrupo)
    3. Calcula estatísticas de valor
    4. Atualiza ou cria padrão em base_padroes
    
    Args:
        user_id: ID do usuário
        upload_history_id: ID do histórico de upload
    
    Returns:
        dict com contadores
    """
    from app.domains.transactions.models import JournalEntry
    from app.domains.patterns.models import BasePadroes
    from sqlalchemy import func
    import hashlib
    
    # Buscar transações do upload com estabelecimento_base
    transacoes = self.db.query(JournalEntry).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.upload_history_id == upload_history_id,
        JournalEntry.EstabelecimentoBase.isnot(None),
        JournalEntry.EstabelecimentoBase != ''
    ).all()
    
    if not transacoes:
        return {'atualizados': 0, 'novos': 0}
    
    # Agrupar por (EstabelecimentoBase, GRUPO, SUBGRUPO)
    grupos = {}
    for t in transacoes:
        chave = (t.EstabelecimentoBase, t.GRUPO, t.SUBGRUPO)
        if chave not in grupos:
            grupos[chave] = []
        grupos[chave].append(t)
    
    atualizados = 0
    novos = 0
    
    for (estabelecimento_base, grupo, subgrupo), transacoes_grupo in grupos.items():
        # Calcular estatísticas
        valores = [t.ValorPositivo for t in transacoes_grupo]
        count = len(valores)
        valor_medio = sum(valores) / count
        valor_min = min(valores)
        valor_max = max(valores)
        
        # Desvio padrão (se >1 valor)
        if count > 1:
            variancia = sum((x - valor_medio) ** 2 for x in valores) / count
            desvio_padrao = variancia ** 0.5
            coef_variacao = (desvio_padrao / valor_medio * 100) if valor_medio > 0 else 0
        else:
            desvio_padrao = 0
            coef_variacao = 0
        
        # Faixa de valor
        if valor_min == valor_max:
            faixa_valor = f"FIXO {valor_medio:.2f}"
        else:
            faixa_valor = f"{valor_min:.0f}-{valor_max:.0f}"
        
        # Gerar padrao_num (hash FNV-1a do estabelecimento_base)
        padrao_texto = f"{estabelecimento_base}|{grupo}|{subgrupo}"
        padrao_num = hashlib.sha256(padrao_texto.encode()).hexdigest()[:16]
        
        # Buscar padrão existente
        padrao_existente = self.db.query(BasePadroes).filter(
            BasePadroes.user_id == user_id,
            BasePadroes.padrao_num == padrao_num
        ).first()
        
        if padrao_existente:
            # ATUALIZAR estatísticas (média ponderada com histórico)
            novo_count = padrao_existente.contagem + count
            novo_valor_medio = ((padrao_existente.valor_medio * padrao_existente.contagem) + 
                                (valor_medio * count)) / novo_count
            novo_valor_min = min(padrao_existente.valor_min or valor_min, valor_min)
            novo_valor_max = max(padrao_existente.valor_max or valor_max, valor_max)
            
            # Recalcular faixa
            if novo_valor_min == novo_valor_max:
                nova_faixa = f"FIXO {novo_valor_medio:.2f}"
            else:
                nova_faixa = f"{novo_valor_min:.0f}-{novo_valor_max:.0f}"
            
            # Atualizar
            padrao_existente.contagem = novo_count
            padrao_existente.valor_medio = novo_valor_medio
            padrao_existente.valor_min = novo_valor_min
            padrao_existente.valor_max = novo_valor_max
            padrao_existente.faixa_valor = nova_faixa
            # desvio_padrao e coef_variacao podem ser recalculados com journal completo se necessário
            
            atualizados += 1
            logger.info(f"  ✅ Padrão atualizado: {estabelecimento_base} | {grupo} > {subgrupo} | {novo_count} ocorrências")
        
        else:
            # CRIAR novo padrão
            padrao_estabelecimento = f"{estabelecimento_base} [{faixa_valor}]"
            
            # Determinar confiança (baseado em quantidade)
            if count >= 5:
                confianca = 'alta'
                percentual_consistencia = 95
            elif count >= 3:
                confianca = 'media'
                percentual_consistencia = 75
            else:
                confianca = 'baixa'
                percentual_consistencia = 50
            
            # Exemplos (primeiros 3 estabelecimentos originais)
            exemplos_lista = [t.Estabelecimento for t in transacoes_grupo[:3]]
            exemplos = "; ".join(exemplos_lista)
            
            novo_padrao = BasePadroes(
                user_id=user_id,
                padrao_estabelecimento=padrao_estabelecimento,
                padrao_num=padrao_num,
                contagem=count,
                valor_medio=valor_medio,
                valor_min=valor_min,
                valor_max=valor_max,
                desvio_padrao=desvio_padrao,
                coef_variacao=coef_variacao,
                percentual_consistencia=percentual_consistencia,
                confianca=confianca,
                grupo_sugerido=grupo,
                subgrupo_sugerido=subgrupo,
                tipo_gasto_sugerido=transacoes_grupo[0].TipoGasto,  # Pegar do primeiro
                categoria_geral_sugerida=transacoes_grupo[0].CategoriaGeral,
                faixa_valor=faixa_valor,
                segmentado=0,
                exemplos=exemplos,
                data_criacao=datetime.now(),
                status='ativo'
            )
            
            self.db.add(novo_padrao)
            novos += 1
            logger.info(f"  ➕ Novo padrão criado: {estabelecimento_base} | {grupo} > {subgrupo} | {count} ocorrências")
    
    # Commit (parte do mesmo commit do confirm_upload)
    # NÃO fazer commit aqui, será feito pelo confirm_upload
    
    return {
        'atualizados': atualizados,
        'novos': novos,
        'total_processadas': len(transacoes)
    }
```

---

### PASSO 2: Chamar Fase 6 no `confirm_upload()`

**Localizar em `confirm_upload()` (linha ~827):**

```python
# ========== NOVA FASE 5: ATUALIZAR BASE_PARCELAS ==========
logger.info("🔄 Fase 5: Atualização de Base Parcelas")
try:
    resultado_parcelas = self._fase5_update_base_parcelas(user_id, history.id)
    logger.info(f"  ✅ Parcelas processadas: {resultado_parcelas['total_processadas']} | Atualizadas: {resultado_parcelas['atualizadas']} | Novas: {resultado_parcelas['novas']} | Finalizadas: {resultado_parcelas['finalizadas']}")
except Exception as e:
    # NÃO bloquear confirmação se atualização falhar
    logger.warning(f"  ⚠️ Erro na atualização de parcelas: {str(e)}")

# ========== ADICIONAR AQUI:
# ========== NOVA FASE 6: ATUALIZAR BASE_PADROES ==========
logger.info("🔄 Fase 6: Atualização de Base Padrões")
try:
    resultado_padroes = self._fase6_update_base_padroes(user_id, history.id)
    logger.info(f"  ✅ Padrões processados: {resultado_padroes['total_processadas']} | Atualizados: {resultado_padroes['atualizados']} | Novos: {resultado_padroes['novos']}")
except Exception as e:
    # NÃO bloquear confirmação se atualização falhar
    logger.warning(f"  ⚠️ Erro na atualização de padrões: {str(e)}")
```

---

### PASSO 3: Testar com Arquivo Real

**Arquivo de teste:** `MP202501.xlsx` (MercadoPago)

```bash
# 1. Fazer upload via frontend
# URL: http://localhost:3000/upload
# Arquivo: _arquivos_historicos/_csvs_historico/MP202501.xlsx
# Banco: mercadopago
# Mês: 2025-01

# 2. Verificar preview
# URL: http://localhost:3000/upload/preview/[session_id]

# 3. Confirmar upload

# 4. Validar no banco:
sqlite3 app_dev/backend/database/financas_dev.db
```

**Queries de validação:**

```sql
-- 1. Verificar journal_entries
SELECT COUNT(*), banco_origem, MesFatura
FROM journal_entries
WHERE upload_history_id = (SELECT MAX(id) FROM upload_history)
GROUP BY banco_origem, MesFatura;

-- 2. Verificar base_parcelas (se tiver parcelas)
SELECT *
FROM base_parcelas
WHERE user_id = 1
ORDER BY data_atualizacao DESC
LIMIT 5;

-- 3. Verificar base_padroes (APÓS implementar Fase 6)
SELECT 
    padrao_estabelecimento,
    contagem,
    valor_medio,
    faixa_valor,
    grupo_sugerido,
    subgrupo_sugerido,
    confianca
FROM base_padroes
WHERE user_id = 1
ORDER BY data_criacao DESC
LIMIT 10;
```

---

## 📊 Validações

### ✅ Checklist de Teste:

**Fase 6 - base_padroes:**
- [ ] Método `_fase6_update_base_padroes()` criado
- [ ] Chamada em `confirm_upload()` após Fase 5
- [ ] Upload de arquivo real processado
- [ ] Padrões novos criados em `base_padroes`
- [ ] Padrões existentes atualizados corretamente
- [ ] Estatísticas (média, min, max) calculadas
- [ ] Hash `padrao_num` gerado corretamente
- [ ] Confiança baseada em contagem
- [ ] Logs informativos visíveis

**Integração:**
- [ ] `base_parcelas` continua funcionando (Fase 5)
- [ ] `journal_entries` salva corretamente
- [ ] Preview → Journal sem erros
- [ ] Frontend redireciona para `/transactions`

---

## 🎯 Métricas de Sucesso

**Após implementar Fase 6:**
- ✅ base_padroes tem registros para estabelecimentos do upload
- ✅ Contagens corretas (quantidade de transações)
- ✅ Valores médios calculados corretamente
- ✅ Padrões existentes são atualizados (não duplicados)
- ✅ Confiança aumenta com mais ocorrências

**Exemplo esperado:**

| padrao_estabelecimento | contagem | valor_medio | grupo | subgrupo | confianca |
|------------------------|----------|-------------|-------|----------|-----------|
| CONTA VIVO [50-100] | 12 | 57.45 | Habitação | Conta | alta |
| MERCADO ABC [80-150] | 8 | 112.30 | Alimentação | Supermercado | alta |
| POSTO XYZ [150-200] | 5 | 175.80 | Transporte | Combustível | alta |

---

## 🔍 Troubleshooting

**Problema:** Padrões não sendo criados

**Verificar:**
1. `EstabelecimentoBase` está preenchido nas transações?
2. Método `_fase6_update_base_padroes()` está sendo chamado?
3. Logs mostram "Fase 6: Atualização de Base Padrões"?
4. Há erros no log?

**Debug:**
```python
# Adicionar logs extras no método:
logger.info(f"🔍 DEBUG: {len(transacoes)} transações com estabelecimento_base")
logger.info(f"🔍 DEBUG: {len(grupos)} grupos únicos identificados")
```

---

**Status:** 📋 PLANEJADO  
**Próximo passo:** Implementar método `_fase6_update_base_padroes()`
