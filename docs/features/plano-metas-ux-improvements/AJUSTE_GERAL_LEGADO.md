# Ajuste Geral — Garantir Alinhamento ao Legado

**Data:** 28/02/2026  
**Objetivo:** Ações concretas para que cada pasta seja parte coerente do grande plano legado.  
**Base:** `COMPARATIVO_GERAL_LEGADO.md`

---

## 1. Ajustes por pasta

### 01-admin-gestao-usuarios

| # | Ação | Prioridade | Responsável |
|---|------|------------|-------------|
| 1.1 | Adicionar seção "Mapeamento Legado" no PLANO.md: Sprint 0, 2n (gestão contas) | Baixa | — |
| 1.2 | Documentar que grupos por usuário é evolução além do legado (correção de modelo) | Baixa | — |

**Status:** Já alinhado. Ajustes são documentação.

---

### 02-ux-fundacao

| # | Ação | Prioridade | Responsável |
|---|------|------------|-------------|
| 2.1 | Garantir EmptyStatePlano: CTA principal → /mobile/plano, secundário → /mobile/construir-plano | Média | — |
| 2.2 | Verificar que tab Plano no BottomNav aponta para /mobile/plano (já feito na Fase 1) | — | ✅ |
| 2.3 | Adicionar no PLANO.md: "Atende S19, S27, B1–B4 do PRD legado" | Baixa | — |

**Status:** Pequenos ajustes de documentação e empty state.

---

### 03-onboarding-grupos

| # | Ação | Prioridade | Responsável |
|---|------|------------|-------------|
| 3.1 | Checklist "Crie seu Plano" → href /mobile/plano (já feito) | — | ✅ |
| 3.2 | Nudge S29 "Crie seu Plano" — adicionar em NudgeBanners: quando `primeiro_upload && !plano_criado` → "Ótimo início! Crie seu Plano" + CTA /mobile/plano | Média | NudgeBanners.tsx |
| 3.3 | "Import planilha" na choose-path: pode ser link para /mobile/upload com ?tipo=planilha | Baixa | — |
| 3.4 | Adicionar no PLANO.md: "Atende S24, S25, S26, S28, S29 do PRD legado" | Baixa | — |

**Status:** Verificar NudgeBanners; resto documentação.

---

### 04-upload-completo

| # | Ação | Prioridade | Responsável |
|---|------|------------|-------------|
| 4.1 | Documentar no PLANO.md: "Fase 6 (parcelas → base_expectativas) pertence ao 05-plano Fase 4" | Média | — |
| 4.2 | Se houver menção a base_expectativas no upload: apontar dependência de 05 | Média | — |
| 4.3 | Adicionar no PLANO.md: "Atende S20, S21, S22, S23, S30, S31 do PRD legado" | Baixa | — |

**Status:** Esclarecer fronteira 04 ↔ 05.

---

### 05-plano-financeiro

| # | Ação | Prioridade | Responsável |
|---|------|------------|-------------|
| 5.1 | Seguir PLANO_DE_AJUSTE: Fases 2–5 (cashflow, recibo, aposentadoria, expectativas, wizard) | Alta | — |
| 5.2 | Manter COMPARATIVO_FASE2_LEGADO e COMPARATIVO_LEGADO_VS_ATUAL atualizados | Média | — |
| 5.3 | Adicionar no PRD.md: "Atende S5, S7, S8, S9, S10 do PRD legado; wizard e cashflow em PLANO_DE_AJUSTE" | Baixa | — |
| 5.4 | Garantir que toda edição do plano passa por /mobile/construir-plano (regra já definida) | Alta | ✅ |

**Status:** Em execução. PLANO_DE_AJUSTE é a bússola.

---

### 06-patrimonio-investimentos

| # | Ação | Prioridade | Responsável |
|---|------|------------|-------------|
| 6.1 | Verificar badge dinâmico na tab Carteira (aportes pendentes) — S19.4 do legado | Média | — |
| 6.2 | Documentar integração com 05: aporte do plano alimenta projeção aposentadoria | Média | — |
| 6.3 | Adicionar no PLANO.md: "Atende S11–S18 do PRD legado" | Baixa | — |

**Status:** Validar badge; documentar integração.

---

## 2. Ajustes no ROADMAP

| # | Ação |
|---|------|
| R.1 | Adicionar seção "Documentos de alinhamento" com links para COMPARATIVO_GERAL_LEGADO e AJUSTE_GERAL_LEGADO |
| R.2 | Em "Próximos passos", incluir: "Revisar AJUSTE_GERAL_LEGADO.md para garantir alinhamento por pasta" |
| R.3 | Manter referência ao PLANO_DE_AJUSTE para 05-plano |

---

## 3. Ajustes na VISAO_FLUXO_DADOS

| # | Ação |
|---|------|
| V.1 | Adicionar referência ao COMPARATIVO_GERAL_LEGADO na seção de documentos |
| V.2 | Manter coerência: 3 camadas, fluxo extrato → plano → patrimônio |

---

## 4. Checklist de validação (por pasta)

Antes de considerar uma pasta "alinhada ao legado":

- [ ] PLANO.md ou PRD.md cita os itens do legado que atende (S1–S31, 2n, 2o)
- [ ] Dependências entre pastas estão corretas no ROADMAP
- [ ] CTAs e rotas apontam para os destinos corretos (/mobile/plano, /mobile/construir-plano)
- [ ] Nenhuma pasta assume responsabilidade de outra sem documentar

---

## 5. Ordem de execução sugerida

1. **Imediato:** Ajustes 5.1 (PLANO_DE_AJUSTE Fase 2), 2.1 (EmptyStatePlano), 3.2 (NudgeBanners)
2. **Documentação:** 1.1, 2.3, 3.4, 4.1–4.3, 5.3, 6.1–6.3
3. **ROADMAP:** R.1, R.2, R.3
4. **Validação:** 6.1 (badge Carteira)

---

## 6. Referências

- **Comparativo geral:** `COMPARATIVO_GERAL_LEGADO.md`
- **Comparativo 05:** `05-plano-financeiro/COMPARATIVO_LEGADO_VS_ATUAL.md`
- **Comparativo Fase 2:** `05-plano-financeiro/COMPARATIVO_FASE2_LEGADO.md`
- **Plano de ajuste 05:** `05-plano-financeiro/PLANO_DE_AJUSTE.md`
- **Legado:** `_legado/PRD.md`, `_legado/PLANO_IMPLEMENTACAO.md`, `_legado/02-TECH_SPEC/TECH_SPEC.md`
