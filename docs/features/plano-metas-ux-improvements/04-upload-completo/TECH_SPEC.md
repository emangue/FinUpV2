# TECH SPEC — Upload Completo
> Sub-projeto 04 | Sprints 3, 3.5, 4, 5

---

## 1. Arquitetura

```
Frontend (Next.js)                   Backend (FastAPI)
─────────────────────────────────────────────────────────
DropZoneMulti                        POST /upload/detect
  FileDetectionCard × N           ── GET  /upload/history
  BatchClassifyModal              ── DELETE /upload/{id}/rollback
  UploadHistoryList               ── GET  /upload/{id}/rollback/preview
  RollbackPreviewModal            ── POST /upload/import-planilha
                                  ── POST /upload/confirmar
                                  └── (processadores existentes para import real)
```

---

## 2. Banco de Dados — Migrations

### 2a. `upload_history` — nova tabela (Sprint 3)

```python
# app/domains/upload/models.py
class UploadHistory(Base):
    __tablename__ = "upload_history"

    id               = Column(Integer, primary_key=True)
    user_id          = Column(Integer, ForeignKey("users.id"), nullable=False)
    banco            = Column(String, nullable=False)      # "nubank", "itau", "btg"
    tipo             = Column(String, nullable=False)      # "extrato", "fatura", "planilha"
    periodo_inicio   = Column(Date, nullable=False)
    periodo_fim      = Column(Date, nullable=False)
    arquivo_hash     = Column(String, nullable=True)       # SHA-256 do arquivo original
    total_transacoes = Column(Integer, default=0)
    is_duplicate_warning = Column(Boolean, default=False)
    created_at       = Column(DateTime, default=func.now())

    # Relacionamentos reversos (cascade delete)
    journal_entries  = relationship("JournalEntry", back_populates="upload_history",
                                    cascade="all, delete-orphan")
```

### 2b. `journal_entries.upload_history_id` — nova coluna

```python
# Migration Alembic
def upgrade():
    op.add_column("journal_entries",
        sa.Column("upload_history_id", sa.Integer,
                  sa.ForeignKey("upload_history.id", ondelete="CASCADE"),
                  nullable=True))

def downgrade():
    op.drop_column("journal_entries", "upload_history_id")
```

### 2c. `base_marcacoes.upload_history_id` — nova coluna

```python
def upgrade():
    op.add_column("base_marcacoes",
        sa.Column("upload_history_id", sa.Integer,
                  sa.ForeignKey("upload_history.id", ondelete="SET NULL"),
                  nullable=True))
```

### 2d. `base_parcelas.upload_history_id` — nova coluna

```python
def upgrade():
    op.add_column("base_parcelas",
        sa.Column("upload_history_id", sa.Integer,
                  sa.ForeignKey("upload_history.id", ondelete="SET NULL"),
                  nullable=True))
```

---

## 3. Backend — S20: Detecção automática

### Fingerprints por processador

```python
# app/domains/upload/fingerprints.py
from dataclasses import dataclass
from typing import Optional
import re, hashlib

@dataclass
class DetectionResult:
    banco: str                   # "nubank", "itau", "btg", "bb", "mercadopago", "generico"
    tipo: str                    # "extrato", "fatura", "planilha"
    periodo_inicio: Optional[str]  # "2025-11-01"
    periodo_fim: Optional[str]     # "2025-11-30"
    confianca: float               # 0.0 – 1.0
    arquivo_hash: str

FINGERPRINTS = {
    "nubank_extrato": {
        "extensao": [".csv"],
        "cabecalho_obrigatorio": ["Data", "Descrição", "Valor"],
        "conteudo_regex": r"nubank|roxinha",
        "banco": "nubank", "tipo": "extrato"
    },
    "itau_fatura": {
        "extensao": [".xls", ".xlsx"],
        "cabecalho_obrigatorio": ["Lançamento", "Valor (R$)"],
        "conteudo_regex": r"ita[uú]",
        "banco": "itau", "tipo": "fatura"
    },
    "btg_extrato": {
        "extensao": [".csv"],
        "cabecalho_obrigatorio": ["Data", "Histórico", "Valor"],
        "conteudo_regex": r"btg|pactual",
        "banco": "btg", "tipo": "extrato"
    },
    "bb_ofx": {
        "extensao": [".ofx"],
        "conteudo_regex": r"banco do brasil|001\.ofx",
        "banco": "bb", "tipo": "extrato"
    },
    "mercadopago": {
        "extensao": [".csv"],
        "cabecalho_obrigatorio": ["DATA", "DESCRIÇÃO", "VALOR"],
        "conteudo_regex": r"mercado\s*pago",
        "banco": "mercadopago", "tipo": "extrato"
    },
}

class DetectionEngine:
    def detect(self, filename: str, content_sample: str, file_bytes: bytes) -> DetectionResult:
        ext = Path(filename).suffix.lower()
        arquivo_hash = hashlib.sha256(file_bytes).hexdigest()

        for key, fp in FINGERPRINTS.items():
            if ext not in fp.get("extensao", [ext]):
                continue
            if re.search(fp.get("conteudo_regex", ""), content_sample, re.IGNORECASE):
                periodo = self._extrair_periodo(content_sample, fp["tipo"])
                return DetectionResult(
                    banco=fp["banco"],
                    tipo=fp["tipo"],
                    periodo_inicio=periodo[0],
                    periodo_fim=periodo[1],
                    confianca=0.9,
                    arquivo_hash=arquivo_hash
                )

        # Fallback: planilha genérica
        return DetectionResult(
            banco="generico", tipo="planilha",
            periodo_inicio=None, periodo_fim=None,
            confianca=0.3, arquivo_hash=arquivo_hash
        )

    def _extrair_periodo(self, content: str, tipo: str) -> tuple[Optional[str], Optional[str]]:
        # Regex para extrair datas do conteúdo do arquivo
        datas = re.findall(r"\d{2}/\d{2}/\d{4}", content[:2000])
        if datas:
            from datetime import datetime
            parsed = [datetime.strptime(d, "%d/%m/%Y") for d in datas if d]
            return str(min(parsed).date()), str(max(parsed).date())
        return None, None
```

### Endpoint de detecção

```python
# app/domains/upload/router.py

@router.post("/detect")
async def detect_arquivo(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Detecta banco/tipo/período + verifica duplicata."""
    file_bytes = await file.read()
    content_sample = file_bytes[:4096].decode("utf-8", errors="ignore")

    engine = DetectionEngine()
    result = engine.detect(file.filename, content_sample, file_bytes)

    # S30: verificar duplicata
    duplicata = None
    if result.periodo_inicio and result.banco != "generico":
        existing = db.query(UploadHistory).filter(
            UploadHistory.user_id == user_id,
            UploadHistory.banco == result.banco,
            UploadHistory.tipo == result.tipo,
            UploadHistory.periodo_inicio == result.periodo_inicio,
            UploadHistory.periodo_fim == result.periodo_fim,
        ).first()
        if existing:
            duplicata = {
                "upload_id": existing.id,
                "data_importacao": existing.created_at.isoformat(),
                "total_transacoes": existing.total_transacoes
            }

    return {
        **asdict(result),
        "filename": file.filename,
        "duplicata_detectada": duplicata
    }
```

---

## 4. Backend — S31: Rollback de upload

### Endpoint de preview

```python
@router.get("/{upload_id}/rollback/preview")
def rollback_preview(
    upload_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    upload = db.query(UploadHistory).filter(
        UploadHistory.id == upload_id,
        UploadHistory.user_id == user_id
    ).first_or_404()

    total_tx = db.query(func.count(JournalEntry.id)).filter(
        JournalEntry.upload_history_id == upload_id
    ).scalar()

    total_marcacoes = db.query(func.count(BaseMarcacao.id)).filter(
        BaseMarcacao.upload_history_id == upload_id
    ).scalar()

    total_parcelas = db.query(func.count(BaseParcela.id)).filter(
        BaseParcela.upload_history_id == upload_id
    ).scalar()

    # Verificar vínculos de investimento
    tx_ids = db.query(JournalEntry.id).filter(
        JournalEntry.upload_history_id == upload_id
    ).subquery()
    total_vinculos = db.query(func.count(InvestimentoTransacao.id)).filter(
        InvestimentoTransacao.journal_entry_id.in_(tx_ids)
    ).scalar()

    return {
        "upload": {"id": upload.id, "banco": upload.banco, "tipo": upload.tipo,
                   "periodo_inicio": str(upload.periodo_inicio),
                   "periodo_fim": str(upload.periodo_fim)},
        "preview": {
            "total_transacoes": total_tx,
            "total_marcacoes": total_marcacoes,
            "total_parcelas": total_parcelas,
            "total_vinculos_investimento": total_vinculos,
            "tem_vinculos": total_vinculos > 0
        }
    }
```

### Endpoint de rollback (DELETE)

```python
@router.delete("/{upload_id}/rollback")
def rollback_upload(
    upload_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    upload = db.query(UploadHistory).filter(
        UploadHistory.id == upload_id,
        UploadHistory.user_id == user_id
    ).first_or_404()

    try:
        # Ordem de deleção respeita FK constraints
        # 1. Desvincular investimentos (set null ou deletar)
        tx_ids = [r[0] for r in db.query(JournalEntry.id).filter(
            JournalEntry.upload_history_id == upload_id
        ).all()]
        if tx_ids:
            db.query(InvestimentoTransacao).filter(
                InvestimentoTransacao.journal_entry_id.in_(tx_ids)
            ).delete(synchronize_session=False)

        # 2. Deletar marcações (FK nullable → já orphan com SET NULL, mas garantir)
        db.query(BaseMarcacao).filter(
            BaseMarcacao.upload_history_id == upload_id
        ).delete(synchronize_session=False)

        # 3. Deletar parcelas
        db.query(BaseParcela).filter(
            BaseParcela.upload_history_id == upload_id
        ).delete(synchronize_session=False)

        # 4. Deletar UploadHistory → cascade deleta journal_entries
        db.delete(upload)
        db.commit()

        return {"success": True, "mensagem": "Upload desfeito com sucesso"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro no rollback: {str(e)}")
```

### Endpoint de histórico

```python
@router.get("/history")
def listar_historico(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    uploads = db.query(UploadHistory).filter(
        UploadHistory.user_id == user_id
    ).order_by(UploadHistory.created_at.desc()).limit(50).all()

    return [
        {
            "id": u.id,
            "banco": u.banco,
            "tipo": u.tipo,
            "periodo_inicio": str(u.periodo_inicio),
            "periodo_fim": str(u.periodo_fim),
            "total_transacoes": u.total_transacoes,
            "is_duplicate_warning": u.is_duplicate_warning,
            "created_at": u.created_at.isoformat()
        }
        for u in uploads
    ]
```

---

## 5. Backend — S23: Import planilha genérica

```python
# app/domains/upload/schemas.py
class ImportPlanilhaConfirm(BaseModel):
    session_id: str                       # UUID da sessão de preview
    mapeamento_grupos: dict[str, int]     # estabelecimento_base → grupo_id

@router.post("/import-planilha")
async def preview_planilha(file: UploadFile = File(...), ...):
    """Valida colunas, retorna preview + estabelecimentos não classificados."""
    df = pd.read_csv(file.file) if file.filename.endswith(".csv") else pd.read_excel(file.file)

    COLUNAS_OBRIGATORIAS = {"Data", "Descrição", "Valor"}
    faltando = COLUNAS_OBRIGATORIAS - set(df.columns)
    if faltando:
        raise HTTPException(400, detail=f"Colunas ausentes: {', '.join(faltando)}")

    # Retornar preview + estabelecimentos únicos sem grupo
    session_id = str(uuid4())
    cache[session_id] = df  # Cache temporário (Redis ou dict em memória)

    estabelecimentos = df["Descrição"].unique()[:100]
    return {"session_id": session_id, "preview": df.head(5).to_dict(), "estabelecimentos": estabelecimentos}

@router.post("/confirmar")
def confirmar_importacao(data: ImportPlanilhaConfirm, ...):
    """Executa import real com grupos mapeados."""
    df = cache.pop(data.session_id)
    # Processar cada linha como JournalEntry com upload_history_id
    ...
```

---

## 6. Frontend — Componentes

### `DropZoneMulti` (`features/upload/components/drop-zone-multi.tsx`)

```tsx
export function DropZoneMulti({ onImportComplete }: Props) {
  const [files, setFiles] = useState<FileDetectionState[]>([])

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const detections = acceptedFiles.map(f => ({
      file: f, status: "detectando" as const,
      result: null as DetectionResult | null
    }))
    setFiles(detections)

    // Detectar em paralelo
    await Promise.all(
      acceptedFiles.map(async (f, i) => {
        const form = new FormData()
        form.append("file", f)
        const res = await fetch("/api/upload/detect", { method: "POST", body: form })
        const data = await res.json()
        setFiles(prev => prev.map((item, idx) =>
          idx === i ? { ...item, status: "ok", result: data } : item
        ))
      })
    )
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { "text/csv": [], "application/vnd.ms-excel": [], "application/octet-stream": [] },
    maxFiles: 10
  })

  return (
    <div>
      <div {...getRootProps()} className={cn(
        "border-2 border-dashed rounded-xl p-8 text-center transition-colors",
        isDragActive ? "border-primary bg-primary/5" : "border-muted"
      )}>
        <input {...getInputProps()} />
        <CloudUpload className="mx-auto mb-2 text-muted-foreground" size={32} />
        <p>{isDragActive ? "Solte os arquivos" : "Arraste arquivos ou clique para selecionar"}</p>
        <p className="text-xs text-muted-foreground mt-1">Até 10 arquivos — Nubank, Itaú, BTG, BB, MercadoPago, CSV</p>
      </div>

      {files.length > 0 && (
        <div className="mt-4 space-y-2">
          {files.map((f, i) => <FileDetectionCard key={i} fileState={f} />)}
        </div>
      )}
    </div>
  )
}
```

### `FileDetectionCard` (`features/upload/components/file-detection-card.tsx`)

```tsx
export function FileDetectionCard({ fileState, onChange }: Props) {
  const { file, status, result } = fileState
  const [banco, setBanco] = useState(result?.banco ?? "")
  const [tipo, setTipo] = useState(result?.tipo ?? "")

  if (status === "detectando") {
    return (
      <div className="flex items-center gap-3 p-3 border rounded-lg">
        <Loader2 className="animate-spin text-muted-foreground" size={18} />
        <span className="text-sm">{file.name}</span>
      </div>
    )
  }

  return (
    <div className="p-3 border rounded-lg space-y-2">
      <div className="flex items-center gap-2">
        {status === "ok" ? <CheckCircle className="text-green-500" size={18} /> : <XCircle className="text-red-500" size={18} />}
        <span className="text-sm font-medium">{file.name}</span>
        {result?.confianca && result.confianca < 0.6 && (
          <Badge variant="outline" className="text-xs">Verificar</Badge>
        )}
      </div>

      {result?.duplicata_detectada && (
        <Alert variant="warning">
          <AlertTriangle size={14} />
          <AlertDescription className="text-xs">
            Já importado em {formatDate(result.duplicata_detectada.data_importacao)}
            ({result.duplicata_detectada.total_transacoes} transações)
          </AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-3 gap-2">
        <Select value={banco} onValueChange={setBanco}>
          <SelectTrigger><SelectValue placeholder="Banco" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="nubank">Nubank</SelectItem>
            <SelectItem value="itau">Itaú</SelectItem>
            <SelectItem value="btg">BTG</SelectItem>
            <SelectItem value="bb">BB</SelectItem>
            <SelectItem value="mercadopago">MercadoPago</SelectItem>
            <SelectItem value="generico">Outro</SelectItem>
          </SelectContent>
        </Select>

        <Select value={tipo} onValueChange={setTipo}>
          <SelectTrigger><SelectValue placeholder="Tipo" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="extrato">Extrato</SelectItem>
            <SelectItem value="fatura">Fatura</SelectItem>
            <SelectItem value="planilha">Planilha</SelectItem>
          </SelectContent>
        </Select>

        <div className="text-xs text-muted-foreground flex items-center">
          {result?.periodo_inicio ? `${result.periodo_inicio} → ${result.periodo_fim}` : "Período não detectado"}
        </div>
      </div>
    </div>
  )
}
```

### `UploadHistoryList` (`features/upload/components/upload-history-list.tsx`)

```tsx
export function UploadHistoryList() {
  const { data: uploads, mutate } = useSWR("/api/upload/history", fetcher)
  const [rollbackTarget, setRollbackTarget] = useState<UploadHistoryItem | null>(null)

  return (
    <div className="space-y-2">
      <h2 className="text-base font-semibold">Meus Uploads</h2>
      {uploads?.map(upload => (
        <div key={upload.id} className="flex items-center justify-between p-3 border rounded-lg">
          <div>
            <p className="text-sm font-medium capitalize">{upload.banco} — {upload.tipo}</p>
            <p className="text-xs text-muted-foreground">
              {formatDate(upload.periodo_inicio)} → {formatDate(upload.periodo_fim)} •{" "}
              {upload.total_transacoes} transações • {formatDate(upload.created_at)}
            </p>
            {upload.is_duplicate_warning && (
              <Badge variant="outline" className="text-xs mt-1">⚠️ Importado como duplicata</Badge>
            )}
          </div>
          <Button variant="ghost" size="sm" onClick={() => setRollbackTarget(upload)}>
            <Undo2 size={15} className="mr-1" /> Desfazer
          </Button>
        </div>
      ))}

      {rollbackTarget && (
        <RollbackPreviewModal
          upload={rollbackTarget}
          onClose={() => setRollbackTarget(null)}
          onSuccess={() => { mutate(); setRollbackTarget(null) }}
        />
      )}
    </div>
  )
}
```

### `RollbackPreviewModal` (`features/upload/components/rollback-preview-modal.tsx`)

```tsx
export function RollbackPreviewModal({ upload, onClose, onSuccess }: Props) {
  const [confirmed, setConfirmed] = useState(false)
  const [loading, setLoading] = useState(false)
  const { data: preview } = useSWR(`/api/upload/${upload.id}/rollback/preview`, fetcher)

  const handleRollback = async () => {
    setLoading(true)
    const res = await fetch(`/api/upload/${upload.id}/rollback`, { method: "DELETE" })
    setLoading(false)
    if (res.ok) onSuccess()
  }

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>↩️ Desfazer importação</DialogTitle>
          <DialogDescription className="capitalize">
            {upload.banco} — {upload.tipo} • {formatDate(upload.periodo_inicio)} → {formatDate(upload.periodo_fim)}
          </DialogDescription>
        </DialogHeader>

        {preview && (
          <div className="space-y-2 text-sm">
            <p className="font-medium">Serão removidos permanentemente:</p>
            <ul className="list-disc list-inside space-y-1 text-muted-foreground">
              <li>{preview.total_transacoes} transações</li>
              <li>{preview.total_marcacoes} marcações associadas</li>
              <li>{preview.total_parcelas} parcelas associadas</li>
            </ul>
            {preview.tem_vinculos && (
              <Alert variant="destructive">
                <AlertTriangle size={14} />
                <AlertDescription>
                  ⚠️ {preview.total_vinculos_investimento} transações têm vínculos de investimento —
                  esses vínculos também serão desfeitos.
                </AlertDescription>
              </Alert>
            )}
            <div className="flex items-center gap-2 mt-3">
              <Checkbox id="confirm" onCheckedChange={v => setConfirmed(!!v)} />
              <label htmlFor="confirm" className="text-sm cursor-pointer">
                Entendo que esta ação é irreversível
              </label>
            </div>
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Cancelar</Button>
          <Button variant="destructive" disabled={!confirmed || loading} onClick={handleRollback}>
            {loading ? <Loader2 className="animate-spin mr-2" size={14} /> : null}
            Confirmar remoção
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
```

---

## 7. Integração no fluxo de upload existente

Ao finalizar qualquer upload bem-sucedido (processadores existentes), salvar o `UploadHistory`:

```python
# app/domains/upload/service.py (adicionar ao final do método de import)
def _registrar_historico(self, user_id: int, banco: str, tipo: str,
                          periodo_inicio: date, periodo_fim: date,
                          arquivo_hash: str, total_tx: int,
                          is_dup: bool) -> int:
    uh = UploadHistory(
        user_id=user_id, banco=banco, tipo=tipo,
        periodo_inicio=periodo_inicio, periodo_fim=periodo_fim,
        arquivo_hash=arquivo_hash, total_transacoes=total_tx,
        is_duplicate_warning=is_dup
    )
    self.db.add(uh)
    self.db.flush()  # Obter ID antes de commitar
    return uh.id
    # Depois: setar upload_history_id em cada JournalEntry criado
```

---

## 8. Checklist de Implementação

### Sprint 3 — Detecção + Duplicata
- [ ] Criar `fingerprints.py` com `DetectionEngine`
- [ ] Migration `upload_history` + FK em `journal_entries`
- [ ] Endpoint `POST /upload/detect` com S30 embutido
- [ ] Integrar `_registrar_historico()` no fluxo existente
- [ ] Testar com arquivos Nubank, Itaú, BTG

### Sprint 3.5 — Rollback
- [ ] Migrations FK em `base_marcacoes` e `base_parcelas`
- [ ] Endpoint `GET /upload/{id}/rollback/preview`
- [ ] Endpoint `DELETE /upload/{id}/rollback`
- [ ] Endpoint `GET /upload/history`
- [ ] Componente `UploadHistoryList`
- [ ] Componente `RollbackPreviewModal`
- [ ] Testar rollback com e sem vínculos de investimento

### Sprint 4 — Multi-arquivo + Batch classify
- [ ] Componente `DropZoneMulti` (react-dropzone)
- [ ] Componente `FileDetectionCard`
- [ ] Componente `BatchClassifyModal`
- [ ] Fluxo de importação paralela com progress por arquivo

### Sprint 5 — Planilha genérica
- [ ] Endpoint `POST /upload/import-planilha` (pandas)
- [ ] Endpoint `POST /upload/confirmar`
- [ ] UI de preview de planilha com mapeamento de colunas
- [ ] Integrar no `DropZoneMulti` (detectado como `tipo: planilha`)
