"""
Processador de planilha genérica CSV/XLSX
Sprint 5: Colunas obrigatórias Data, Descrição/Lançamento, Valor
"""
import re
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from datetime import datetime
import pandas as pd

from .base import RawTransaction

# Variações comuns de nomes de colunas (case-insensitive)
COL_DATA_ALIASES = ["data", "data transação", "data da transação", "dt", "date", "data transacao"]
COL_DESCRICAO_ALIASES = ["descrição", "descricao", "lançamento", "lancamento", "histórico", "historico", "estabelecimento", "desc"]
COL_VALOR_ALIASES = ["valor", "valor (r$)", "valor (rs)", "valor r$", "amount", "valor_reais", "valor_reais"]


def _normalize_col(s: str) -> str:
    """Remove acentos e lowercase para comparação"""
    if not s or not isinstance(s, str):
        return ""
    s = str(s).strip().lower()
    # Remove acentos básicos
    replacements = {"á": "a", "à": "a", "â": "a", "ã": "a", "é": "e", "ê": "e", "í": "i", "ó": "o", "ô": "o", "õ": "o", "ú": "u", "ç": "c"}
    for old, new in replacements.items():
        s = s.replace(old, new)
    return s


def _find_column(headers: List[str], aliases: List[str]) -> Optional[str]:
    """Encontra coluna por lista de aliases (case-insensitive)"""
    normalized_headers = {_normalize_col(h): h for h in headers if h}
    for alias in aliases:
        if _normalize_col(alias) in normalized_headers:
            return normalized_headers[_normalize_col(alias)]
    return None


def detect_column_mapping(headers: List[str]) -> Tuple[Optional[str], Optional[str], Optional[str], List[str]]:
    """
    Detecta mapeamento automático de colunas.
    Retorna: (col_data, col_descricao, col_valor, colunas_faltando)
    """
    col_data = _find_column(headers, COL_DATA_ALIASES)
    col_descricao = _find_column(headers, COL_DESCRICAO_ALIASES)
    col_valor = _find_column(headers, COL_VALOR_ALIASES)

    faltando = []
    if not col_data:
        faltando.append("Data")
    if not col_descricao:
        faltando.append("Descrição")
    if not col_valor:
        faltando.append("Valor")

    return col_data, col_descricao, col_valor, faltando


def _parse_date(val) -> str:
    """Converte valor para string DD/MM/YYYY"""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    if isinstance(val, str) and val.strip():
        # Já string - tentar parse
        val = val.strip()
        # DD/MM/YYYY ou DD-MM-YYYY
        m = re.match(r"(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})", val)
        if m:
            return f"{m.group(1).zfill(2)}/{m.group(2).zfill(2)}/{m.group(3)}"
        # YYYY-MM-DD
        m = re.match(r"(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})", val)
        if m:
            return f"{m.group(3).zfill(2)}/{m.group(2).zfill(2)}/{m.group(1)}"
        return val[:10] if len(val) >= 10 else val
    try:
        dt = pd.to_datetime(val)
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return str(val)[:10] if val else ""


def _parse_valor(val) -> float:
    """Converte valor para float. Aceita: 49.90 (US), 49,90 (BR), 1.234,56 (BR milhar)"""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    s = re.sub(r"[R$\s]", "", s)
    # BR: 1.234,56 ou 49,90 → remove . (milhar), troca , por .
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        # Só vírgula: 49,90
        s = s.replace(",", ".")
    # else: 49.90 (US) - mantém
    try:
        return float(s) if s else 0.0
    except ValueError:
        return 0.0


def process_planilha_generica(
    file_path: Path,
    nome_arquivo: str,
    mapeamento: Optional[Dict[str, str]] = None,
) -> List[RawTransaction]:
    """
    Processa planilha CSV ou XLSX genérica.

    Args:
        file_path: Caminho do arquivo
        nome_arquivo: Nome original do arquivo
        mapeamento: Opcional. Ex: {"Data": "data_transacao", "Descrição": "desc", "Valor": "valor_reais"}
                   Se None, usa detecção automática.

    Returns:
        Lista de RawTransaction

    Raises:
        ValueError: Se colunas obrigatórias faltando
    """
    ext = (file_path.suffix or "").lower()
    if ext in (".xls", ".xlsx", ".xlsm"):
        df = pd.read_excel(file_path, dtype=str)
    else:
        # CSV - tentar UTF-8, depois latin-1
        try:
            df = pd.read_csv(file_path, dtype=str, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, dtype=str, encoding="latin-1")

    headers = [str(h).strip() for h in df.columns.tolist()]
    if not headers:
        raise ValueError("Arquivo sem cabeçalho")

    if mapeamento:
        col_data = mapeamento.get("Data") or mapeamento.get("data")
        col_descricao = mapeamento.get("Descrição") or mapeamento.get("Descricao") or mapeamento.get("Lancamento")
        col_valor = mapeamento.get("Valor") or mapeamento.get("valor")
        faltando = []
        if not col_data or col_data not in headers:
            faltando.append("Data")
        if not col_descricao or col_descricao not in headers:
            faltando.append("Descrição")
        if not col_valor or col_valor not in headers:
            faltando.append("Valor")
        if faltando:
            raise ValueError(f"Colunas ausentes: {', '.join(faltando)}")
    else:
        col_data, col_descricao, col_valor, faltando = detect_column_mapping(headers)
        if faltando:
            raise ValueError(f"Colunas ausentes: {', '.join(faltando)}")

    now = datetime.now()
    results = []

    for idx, row in df.iterrows():
        data_str = _parse_date(row.get(col_data))
        desc = str(row.get(col_descricao, "") or "").strip()
        valor = _parse_valor(row.get(col_valor))

        if not desc and valor == 0:
            continue  # Linha vazia

        if not desc:
            desc = "(sem descrição)"

        results.append(
            RawTransaction(
                banco="Planilha genérica",
                tipo_documento="planilha",
                nome_arquivo=nome_arquivo,
                data_criacao=now,
                data=data_str or now.strftime("%d/%m/%Y"),
                lancamento=desc,
                valor=valor,
            )
        )

    return results
