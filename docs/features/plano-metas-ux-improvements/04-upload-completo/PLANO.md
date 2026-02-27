# PLANO DE IMPLEMENTAÇÃO — Upload Completo
> Sub-projeto 04 | Sprints 3, 3.5, 4, 5 | Estimativa: ~32h  
> **Pré-requisito:** Sub-projeto 03 (grupos padrão commitado)

---

## Sprint 3 — Detecção inteligente + Alerta de duplicata (~10h)

### Backend (6h)

| Task | Descrição | Est. |
|------|-----------|------|
| A.01 | Migration: criar tabela `upload_history` + FK `journal_entries.upload_history_id` | 1h |
| A.02 | Criar `app/domains/upload/fingerprints.py` com `DetectionEngine` + `FINGERPRINTS` dict | 2h |
| A.03 | Endpoint `POST /upload/detect` — detecção + S30 (verificar duplicata) | 1h |
| A.04 | Integrar `_registrar_historico()` no fluxo existente de import (setar `upload_history_id` em cada JournalEntry criado) | 1.5h |
| A.05 | Testes: arquivo Nubank, Itaú, BTG + arquivo desconhecido (fallback) | 0.5h |

### Frontend (4h)

| Task | Descrição | Est. |
|------|-----------|------|
| F.01 | Componente `FileDetectionCard` com campos banco/tipo/período e alerta de duplicata | 2h |
| F.02 | Integrar `FileDetectionCard` no fluxo de upload existente (substituir campos manuais) | 1h |
| F.03 | Modal de aviso de duplicata com opções "Cancelar" e "Carregar de qualquer forma" | 1h |

---

## Sprint 3.5 — Rollback de upload (~8h)

### Backend (4h)

| Task | Descrição | Est. |
|------|-----------|------|
| A.06 | Migrations: FK `base_marcacoes.upload_history_id` + `base_parcelas.upload_history_id` | 0.5h |
| A.07 | Endpoint `GET /upload/{id}/rollback/preview` — contagens + flag vínculos | 1h |
| A.08 | Endpoint `DELETE /upload/{id}/rollback` — transação atômica na ordem correta | 1.5h |
| A.09 | Endpoint `GET /upload/history` — lista com paginação | 0.5h |
| A.10 | Teste rollback: com e sem vínculos de investimento | 0.5h |

### Frontend (4h)

| Task | Descrição | Est. |
|------|-----------|------|
| F.04 | Componente `UploadHistoryList` (useSWR + lista de uploads com badge duplicata) | 1.5h |
| F.05 | Componente `RollbackPreviewModal` (preview + checkbox confirmação + botão destructive) | 2h |
| F.06 | Adicionar "Meus Uploads" no menu de perfil → rota `/mobile/uploads` | 0.5h |

---

## Sprint 4 — Multi-arquivo + Classificação em lote (~9h)

### Frontend (6h)

| Task | Descrição | Est. |
|------|-----------|------|
| F.07 | Instalar `react-dropzone`, criar componente `DropZoneMulti` | 1.5h |
| F.08 | Detecção em paralelo (Promise.all) com atualização de estado por arquivo | 1.5h |
| F.09 | Progresso de importação por arquivo (estado: detectando → ok / erro) | 1h |
| F.10 | Componente `BatchClassifyModal` — agrupar por `estabelecimento_base`, dropdown de grupo, "Salvar tudo" | 2h |

### Backend (3h)

| Task | Descrição | Est. |
|------|-----------|------|
| A.11 | Endpoint `POST /upload/batch` — aceita lista de arquivos, processa em loop | 1.5h |
| A.12 | `GET /upload/estabelecimentos/sugestoes` — retorna grupos históricos por estabelecimento | 1h |
| A.13 | Testes de importação paralela (3 arquivos simultâneos) | 0.5h |

---

## Sprint 5 — Planilha genérica (~5h)

### Backend (3h)

| Task | Descrição | Est. |
|------|-----------|------|
| A.14 | Endpoint `POST /upload/import-planilha` — validar colunas obrigatórias + retornar preview | 1.5h |
| A.15 | Endpoint `POST /upload/confirmar` — executar import com grupos mapeados + registrar historico | 1h |
| A.16 | Teste com CSV sem cabeçalho correto (erro claro) + CSV válido | 0.5h |

### Frontend (2h)

| Task | Descrição | Est. |
|------|-----------|------|
| F.11 | UI de preview de planilha: 5 primeiras linhas + indicação de colunas mapeadas/faltando | 1h |
| F.12 | Integrar planilha no `DropZoneMulti` (quando `tipo: planilha` detectado, redirecionar ao fluxo de preview) | 1h |

---

## Validação pelo Usuário

Após cada sprint:

**Sprint 3:**
1. [ ] Selecionar arquivo Nubank CSV → banco e período detectados automaticamente
2. [ ] Selecionar arquivo sem reconhecimento → campos ficam editáveis
3. [ ] Selecionar arquivo já importado → alerta de duplicata exibido, opção de carregar mesmo assim funciona

**Sprint 3.5:**
4. [ ] Acessar Menu → Meus Uploads → lista de uploads exibida
5. [ ] Clicar "Desfazer" → preview com contagens exato exibido
6. [ ] Confirmar rollback → upload removido, transações somem, dashboard atualiza

**Sprint 4:**
7. [ ] Arrastar 3 arquivos de uma vez → cada um detectado independentemente
8. [ ] Um arquivo falha → erro só no card dele, outros continuam
9. [ ] Estabelecimentos novos → tela de classificação em lote exibida

**Sprint 5:**
10. [ ] Upload de CSV genérico → colunas obrigatórias validadas
11. [ ] CSV sem coluna "Data" → mensagem "Coluna ausente: Data" exibida
12. [ ] CSV válido → preview exibido, confirmar import funciona

---

## Ordem de Execução

```
A.01 (migration)
  ↓
A.02 (fingerprints.py) → A.03 (endpoint detect) → A.04 (integrar historico)
  ↓
F.01 → F.02 → F.03 (Sprint 3 front)
  ↓
A.06 (migrations FK) → A.07 (preview) → A.08 (rollback) → A.09 (history)
  ↓
F.04 → F.05 → F.06 (Sprint 3.5 front)
  ↓
F.07 → F.08 → F.09 → F.10 (Sprint 4 front)
A.11 → A.12 → A.13 (Sprint 4 back em paralelo)
  ↓
A.14 → A.15 → A.16 (Sprint 5 back)
F.11 → F.12 (Sprint 5 front)
```

---

## Commit por Sprint

```bash
# Sprint 3
git add app_dev/backend/app/domains/upload/ app_dev/backend/migrations/ app_dev/frontend/src/features/upload/
git commit -m "feat(upload): S20+S30 — detecção automática + alerta de duplicata"

# Sprint 3.5
git add app_dev/backend/app/domains/upload/ app_dev/backend/migrations/ app_dev/frontend/src/features/upload/
git commit -m "feat(upload): S31 — rollback de upload com preview e transação atômica"

# Sprint 4
git add app_dev/frontend/src/features/upload/ app_dev/backend/app/domains/upload/
git commit -m "feat(upload): S21+S22 — multi-arquivo com detecção paralela + classificação em lote"

# Sprint 5
git add app_dev/backend/app/domains/upload/ app_dev/frontend/src/features/upload/
git commit -m "feat(upload): S23 — importação de planilha genérica CSV/XLS"
```
