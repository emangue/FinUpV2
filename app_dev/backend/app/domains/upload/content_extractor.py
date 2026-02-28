"""
Extrai texto legível de arquivos binários para detecção por conteúdo.
Prioridade: conteúdo é a validação principal; filename é fallback.
"""
import io
import tempfile
from pathlib import Path
from typing import Optional


def extract_content_sample(file_bytes: bytes, filename: str) -> str:
    """
    Extrai amostra de texto do arquivo para detecção.
    - CSV: decode UTF-8 direto (já feito no router)
    - XLS/XLSX: lê células das primeiras linhas
    - PDF: extrai texto da primeira página

    Retorna string vazia se não conseguir extrair.
    """
    ext = Path(filename).suffix.lower()
    if ext == ".csv" or ext == ".txt":
        return file_bytes[:8192].decode("utf-8", errors="ignore")

    if ext in (".xls", ".xlsx"):
        return _extract_excel(file_bytes, ext)

    if ext == ".pdf":
        return _extract_pdf(file_bytes)

    if ext == ".ofx":
        return file_bytes[:8192].decode("utf-8", errors="ignore")

    return file_bytes[:4096].decode("utf-8", errors="ignore")


def _extract_excel(file_bytes: bytes, ext: str) -> str:
    """Extrai texto das primeiras linhas do Excel."""
    try:
        if ext == ".xls":
            import xlrd
            wb = xlrd.open_workbook(file_contents=file_bytes)
            sheet = wb.sheet_by_index(0)
            lines = []
            for row_idx in range(min(25, sheet.nrows)):
                row_vals = [str(sheet.cell_value(row_idx, col_idx)) for col_idx in range(min(10, sheet.ncols))]
                lines.append(" ".join(row_vals))
            return "\n".join(lines)
        else:
            import openpyxl
            wb = openpyxl.load_workbook(io.BytesIO(file_bytes), read_only=True, data_only=True)
            sheet = wb.active
            lines = []
            for i, row in enumerate(sheet.iter_rows(max_row=25, values_only=True)):
                if row:
                    lines.append(" ".join(str(c) if c is not None else "" for c in row[:10]))
            wb.close()
            return "\n".join(lines)
    except Exception:
        return file_bytes[:4096].decode("utf-8", errors="ignore")


def _extract_pdf(file_bytes: bytes) -> str:
    """Extrai texto da primeira página do PDF."""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            if pdf.pages:
                page = pdf.pages[0]
                text = page.extract_text()
                return text or ""
    except Exception:
        pass
    return file_bytes[:4096].decode("utf-8", errors="ignore")
