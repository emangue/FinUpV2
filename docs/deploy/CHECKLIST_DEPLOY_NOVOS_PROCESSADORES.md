# 📋 Checklist Deploy - Branch `feature/novos-processadores-upload`

**Data:** 22/02/2026  
**Branch:** `feature/novos-processadores-upload`  
**Status Git:** ✅ Tudo commitado, working tree limpo  
**Commits:** 15 commits à frente da `main`

---

## 🎯 Resumo das Mudanças

### Backend (Python/FastAPI)

#### **1. Novos Processadores de Upload**
- ✅ **BTG Pactual Fatura PDF** (`btg_fatura_pdf.py`) - com suporte a senha
- ✅ **BTG Pactual Fatura XLSX** (`btg_fatura_xlsx.py`) - com desencriptação (msoffcrypto-tool)
- ✅ **Mercado Pago Fatura PDF** (`mercadopago_fatura_pdf.py`) - OCR com rapidocr-onnxruntime
- 🔄 **Itaú Fatura PDF** (`itau_fatura_pdf.py`) - atualizado para suportar senha

#### **2. Novas Dependências Python** ⚠️
```bash
msoffcrypto-tool>=4.12.0   # Decriptação XLSX com senha (BTG)
PyMuPDF>=1.24.0            # Renderização PDF → imagem (Mercado Pago OCR)
rapidocr-onnxruntime>=1.4.0  # OCR via ONNX (~50MB, SEM PyTorch!)
```

#### **3. Mudanças em Upload Service/Router**
- Campo `senha: Optional[str]` no endpoint `/upload/preview`
- Compatibilidade backward: processadores antigos continuam funcionando sem senha

#### **4. Melhorias em Transações**
- Fix: agregação de subgrupos (não soma mais valor absoluto)
- Fix: restauração da classe `PropagateInfoResponse`
- Auto-refresh de subgrupos após edição de transação

---

### Frontend (Next.js/TypeScript)

#### **1. Nova Dependência**
```json
"sonner": "^2.0.7"  // Toast notifications bonitos (substitui alert/confirm)
```

#### **2. Upload Flow**
- Campo de senha na tela de upload
- Preview com dialogs bonitos (sem alert/confirm nativo)
- Toast notifications com Sonner

#### **3. Dashboard Orçamento**
- Grupos de despesas **clicáveis** → navega para transações filtradas
- Gráfico de **Investimentos clicável** → navega para transações de investimentos
- Drill-down em subgrupos (collapse quando grupo selecionado)

#### **4. Página de Transações - Major Refactor**
- Filtros **simplificados**: toggle mês/ano (removido range "De/Até")
- Filtros **reorganizados**: movidos para antes do Resumo
- Badge de contagem de filtros ativos
- Auto-abertura quando vem de orçamento (`?from=orcamento`)
- Chips de filtro clicáveis para remover

---

## 🚀 Passo-a-Passo do Deploy

### **Fase 1: Backup** 🛡️

```bash
# No servidor (SSH)
ssh minha-vps-hostinger
cd /var/www/finup
./scripts/deploy/backup_daily.sh
```

**Validação:**
```bash
ls -lh app_dev/backend/database/backups_daily/ | tail -5
# Deve mostrar backup de hoje com ~30-50MB
```

---

### **Fase 2: Git Pull** 📥

```bash
# No servidor
cd /var/www/finup

# Verificar branch atual (deve estar em main)
git branch --show-current

# Fazer merge da feature branch ou trocar para ela
# Opção A: Merge na main (RECOMENDADO para produção)
git checkout main
git pull origin main
git merge feature/novos-processadores-upload  # Ou fazer PR no GitHub antes

# Opção B: Deploy direto da feature branch (PARA TESTES)
git fetch origin
git checkout feature/novos-processadores-upload
git pull origin feature/novos-processadores-upload
```

**Validação:**
```bash
git log --oneline -5
# Deve mostrar: b8dc1b8f feat(orcamento): torna gráfico de Investimentos...
```

---

### **Fase 3: Instalar Dependências Python** 📦

```bash
cd /var/www/finup/app_dev
source venv/bin/activate

# Instalar novas dependências
pip install -r backend/requirements.txt

# Validar instalação
pip list | grep -E "msoffcrypto|PyMuPDF|rapidocr"
# Deve mostrar:
# msoffcrypto-tool  4.x.x
# PyMuPDF           1.24.x
# rapidocr-onnxruntime  1.x.x
```

**⚠️ ATENÇÃO:** `rapidocr-onnxruntime` pode demorar ~2-3min para instalar (download de modelos ONNX ~50MB)

---

### **Fase 4: Instalar Dependências Frontend** 📦

```bash
cd /var/www/finup/app_dev/frontend

# Instalar sonner
npm install

# Validar
npm list sonner
# Deve mostrar: sonner@2.0.7
```

---

### **Fase 5: Build Frontend** 🏗️

```bash
cd /var/www/finup/app_dev/frontend

# Limpar build anterior
rm -rf .next

# Build
npm run build
```

**Validação:**
```bash
ls -lh .next/
# Deve mostrar pasta .next com ~50-100MB
```

**⚠️ Se OOM (Out of Memory):**
```bash
# Build localmente e fazer tar+scp (ver DEPLOY_BUILD_LOCAL.sh)
# OU aumentar memória da VM temporariamente
```

---

### **Fase 6: Verificar Banco de Dados** 🗄️

#### **6.1. Migrations Alembic**
```bash
cd /var/www/finup/app_dev/backend

# Verificar migration atual
alembic current
# Comparar com: alembic heads (deve estar igual)

# Se necessário, rodar migrations pendentes
alembic upgrade head
```

**⚠️ IMPORTANTE:** Esta branch **NÃO tem migrations novas**, mas sempre validar!

#### **6.2. Dados de Compatibilidade (bank_format_compatibility)**

Validar se os 3 novos formatos estão cadastrados:

```bash
# No servidor PostgreSQL
psql -U finup_user -d finup_db -c "
SELECT banco, tipo_documento, formato_arquivo 
FROM bank_format_compatibility 
WHERE banco IN ('BTG Pactual', 'Mercado Pago') 
ORDER BY banco, tipo_documento;
"
```

**Esperado:**
```
     banco       | tipo_documento | formato_arquivo
-----------------+----------------+-----------------
 BTG Pactual     | fatura         | excel
 BTG Pactual     | fatura         | pdf
 Mercado Pago    | fatura         | pdf
```

**Se NÃO existir, inserir manualmente:**
```sql
INSERT INTO bank_format_compatibility (banco, tipo_documento, formato_arquivo) 
VALUES 
  ('BTG Pactual', 'fatura', 'excel'),
  ('BTG Pactual', 'fatura', 'pdf'),
  ('Mercado Pago', 'fatura', 'pdf')
ON CONFLICT DO NOTHING;
```

---

### **Fase 7: Restart Servidores** 🔄

```bash
cd /var/www/finup

# Parar tudo
./scripts/deploy/quick_stop.sh

# Aguardar 2 segundos
sleep 2

# Iniciar tudo
./scripts/deploy/quick_start.sh
```

**Validação:**
```bash
# Backend (porta 8000)
curl -s http://localhost:8000/api/health | jq
# Esperado: {"status":"healthy","database":"connected"}

# Frontend (porta 3003)
curl -s http://localhost:3003 | head -5
# Esperado: HTML da página (<!DOCTYPE html>)
```

---

### **Fase 8: Testes de Fumaça (Smoke Tests)** 🧪

#### **8.1. Backend - Processadores Registrados**

```bash
curl -s http://localhost:8000/api/v1/upload/formats | jq '.[] | select(.banco | contains("BTG") or contains("Mercado"))'
```

**Esperado:**
```json
{
  "banco": "BTG Pactual",
  "tipo_documento": "fatura",
  "formato_arquivo": "excel"
}
{
  "banco": "BTG Pactual",
  "tipo_documento": "fatura",
  "formato_arquivo": "pdf"
}
{
  "banco": "Mercado Pago",
  "tipo_documento": "fatura",
  "formato_arquivo": "pdf"
}
```

#### **8.2. Frontend - Página de Upload**

```bash
# Via navegador
# https://meufinup.com.br/mobile/upload
# - Campo de senha deve aparecer
# - Seleção de banco deve mostrar BTG Pactual e Mercado Pago
```

#### **8.3. Frontend - Dashboard Orçamento**

```bash
# Via navegador
# https://meufinup.com.br/mobile/dashboard
# Aba Orçamento:
# - Clicar em qualquer grupo de despesa → deve navegar para /mobile/transactions?grupo=X
# - Clicar no gráfico de Investimentos → deve navegar para /mobile/transactions?grupo=Investimentos
```

#### **8.4. Frontend - Transações**

```bash
# Via navegador
# https://meufinup.com.br/mobile/transactions
# - Filtros devem estar fechados por padrão
# - Badge de contagem deve aparecer se houver filtros ativos
# - Toggle mês/ano deve funcionar (sem campo "De/Até")
# - Chips de filtro clicáveis para remover
```

---

## ⚠️ Problemas Conhecidos e Soluções

### **1. ModuleNotFoundError: rapidocr**

**Sintoma:**
```
ModuleNotFoundError: No module named 'rapidocr_onnxruntime'
```

**Solução:**
```bash
source /var/www/finup/app_dev/venv/bin/activate
pip install rapidocr-onnxruntime>=1.4.0
```

---

### **2. Out of Memory ao fazer npm run build**

**Sintoma:**
```
FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory
```

**Solução Opção A - Aumentar NODE_OPTIONS:**
```bash
export NODE_OPTIONS="--max-old-space-size=2048"
npm run build
```

**Solução Opção B - Build Local + Upload:**
```bash
# Local
cd app_dev/frontend
npm run build
tar czf build.tar.gz .next

# Upload
scp build.tar.gz minha-vps-hostinger:/var/www/finup/app_dev/frontend/

# Servidor
cd /var/www/finup/app_dev/frontend
rm -rf .next
tar xzf build.tar.gz
rm build.tar.gz
```

---

### **3. PDF com senha não processa (BTG)**

**Validação:**
```bash
python3 -c "import msoffcrypto; print('OK')"
```

Se der erro, reinstalar:
```bash
pip uninstall msoffcrypto-tool -y
pip install msoffcrypto-tool>=4.12.0
```

---

### **4. OCR Mercado Pago muito lento**

**Esperado:** ~3-5 segundos por página (fatura com 5 páginas = ~20s)

Se > 30s, verificar:
```bash
# Verificar modelos ONNX instalados
ls -lh venv/lib/python3.*/site-packages/rapidocr_onnxruntime/models/
# Deve mostrar: ch_PP-OCRv4_det_infer.onnx, ch_ppocr_mobile_v2.0_cls_infer.onnx, en_PP-OCRv3_rec_infer.onnx
```

---

## 📊 Resumo de Commits (15 total)

```
b8dc1b8f feat(orcamento): torna gráfico de Investimentos vs Plano clicável
bfa9823e fix(transactions): corrige fechamento de tags JSX do campo estabelecimento
ac31e7c6 refactor(transactions): move filtros para antes do resumo e fecha por padrão
9109340a refactor(transactions): simplifica filtro de período para mês específico OU ano inteiro
3f46379a feat(transactions): melhora UX do bloco de filtros avançados
a9115b9c fix(transactions): atualiza collapse de subgrupos após editar transação
a06babb5 fix(transactions): corrige agregação de subgrupos para não somar valor absoluto
db4534be feat(orcamento): permite clicar em qualquer grupo (variant resultado) para navegar
57200d31 fix(transactions): restaura classe PropagateInfoResponse removida acidentalmente
afd4050f fix(upload): substitui easyocr por rapidocr-onnxruntime no processador Mercado Pago
4188b43b feat(orcamento): ordena despesas + drill-down de subgrupos em transações
2626dd2e feat(plano): navega para gráfico de projeção ao salvar/atualizar plano
d8bd0ab2 feat(ui): migra todos alert()/confirm() nativos para sonner toast
0a584951 feat(preview): substitui confirm/alert nativos por dialogs bonitos
a8a2c7a2 fix(upload): corrige import PasswordRequiredException no service.py
```

---

## ✅ Checklist Final

Antes de considerar deploy concluído:

- [ ] ✅ Backup criado com sucesso
- [ ] ✅ Git pull/checkout da branch realizado
- [ ] ✅ Dependências Python instaladas (msoffcrypto, PyMuPDF, rapidocr)
- [ ] ✅ Dependências Frontend instaladas (sonner)
- [ ] ✅ Frontend build concluído (.next/ criado)
- [ ] ✅ Migrations Alembic em dia (se aplicável)
- [ ] ✅ bank_format_compatibility com BTG e Mercado Pago
- [ ] ✅ Backend reiniciado (porta 8000 respondendo /api/health)
- [ ] ✅ Frontend reiniciado (porta 3003 servindo HTML)
- [ ] ✅ Smoke test: upload com BTG/Mercado Pago aparece
- [ ] ✅ Smoke test: grupos clicáveis no orçamento
- [ ] ✅ Smoke test: filtros simplificados em transações
- [ ] ✅ Smoke test: sonner toast funcionando (sem alert nativo)

---

## 🎯 Diferenças vs Main (Arquivos Modificados)

**Total:** ~50 arquivos modificados (contando `_arquivo_desktop/` que não está em prod)

**App em Produção (app_dev/):**
- Backend: 12 arquivos
- Frontend: 15+ arquivos

**Principais:**
- `app_dev/backend/requirements.txt` → 3 dependências novas
- `app_dev/frontend/package.json` → 1 dependência nova (sonner)
- `app_dev/backend/app/domains/upload/processors/raw/` → 3 processadores novos
- `app_dev/backend/app/domains/transactions/` → fixes de agregação
- `app_dev/frontend/src/app/mobile/transactions/page.tsx` → refactor completo de filtros
- `app_dev/frontend/src/features/dashboard/components/orcamento-tab.tsx` → navegação clicável

---

## 🚨 Rollback Plan

Se algo der errado:

```bash
# 1. Parar servidores
./scripts/deploy/quick_stop.sh

# 2. Voltar para main
git checkout main
git pull origin main

# 3. Reinstalar dependências antigas (se necessário)
cd app_dev
source venv/bin/activate
pip install -r backend/requirements.txt

cd frontend
npm install

# 4. Rebuild frontend
npm run build

# 5. Restaurar backup do banco (se necessário)
# Ver backup em app_dev/backend/database/backups_daily/

# 6. Reiniciar
./scripts/deploy/quick_start.sh
```

---

## 📞 Contato / Suporte

**Logs em caso de erro:**

```bash
# Backend
tail -100 /var/www/finup/temp/logs/backend.log

# Frontend
tail -100 /var/www/finup/temp/logs/frontend.log

# Sistema
journalctl -u backend -n 100
```

---

**Deploy preparado por:** GitHub Copilot  
**Data:** 22/02/2026  
**Versão:** feature/novos-processadores-upload (15 commits)
