"""
Sprint 3: Detecção inteligente de banco/tipo/período
Mapeia arquivos para processadores via fingerprints (cabecalho + regex)
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import re
import hashlib
from datetime import datetime


@dataclass
class DetectionResult:
    """Resultado da detecção de um arquivo de upload"""
    banco: str  # "nubank", "itau", "btg", "bb", "mercadopago", "generico"
    tipo: str  # "extrato", "fatura", "planilha"
    periodo_inicio: Optional[str]  # "2025-11-01"
    periodo_fim: Optional[str]  # "2025-11-30"
    confianca: float  # 0.0 – 1.0
    arquivo_hash: str
    mes_fatura: Optional[str] = None  # "202511" para duplicata check


FINGERPRINTS = {
    "nubank_extrato": {
        "extensao": [".csv"],
        "cabecalho_obrigatorio": ["Data", "Descrição", "Valor"],
        "conteudo_regex": r"nubank|roxinha",
        "banco": "nubank",
        "tipo": "extrato",
    },
    "itau_extrato": {
        "extensao": [".xlsx", ".xls"],
        "conteudo_regex": r"ita[uú]|itau",
        "conteudo_estrutura": ["SALDO ANTERIOR", "SALDO TOTAL"],  # Extrato Conta Corrente Itaú XLS
        "cabecalho_em_conteudo": ["Data", "Lançamento", "Valor"],  # colunas em qualquer linha
        "banco": "itau",
        "tipo": "extrato",
    },
    "itau_fatura": {
        "extensao": [".xls", ".xlsx", ".csv", ".pdf"],
        "cabecalho_obrigatorio": ["Lançamento", "Valor"],  # aceita "lançamento"/"valor" (CSV real)
        "conteudo_regex": r"ita[uú]|itau",
        "conteudo_estrutura": ["Total desta fatura", "Vencimento"],  # PDF Itaú fatura
        "banco": "itau",
        "tipo": "fatura",
    },
    "btg_extrato": {
        "extensao": [".csv", ".xlsx"],
        "cabecalho_obrigatorio": ["Data", "Histórico", "Valor"],
        "conteudo_regex": r"btg|pactual",
        "banco": "btg",
        "tipo": "extrato",
    },
    "btg_fatura": {
        "extensao": [".xlsx", ".pdf"],
        "conteudo_regex": r"btg|pactual",
        "conteudo_estrutura": ["Total da Fatura", "BTG", "Pactual"],  # exige 2, sendo 1 banco-específico
        "banco": "btg",
        "tipo": "fatura",
    },
    "bb_ofx": {
        "extensao": [".ofx"],
        "conteudo_regex": r"banco do brasil|bb\.ofx|001\.ofx",
        "banco": "bb",
        "tipo": "extrato",
    },
    "mercadopago_extrato": {
        "extensao": [".csv", ".xlsx", ".pdf"],
        "cabecalho_obrigatorio": ["DATA", "DESCRIÇÃO", "VALOR"],
        "conteudo_regex": r"mercado\s*pago|mercadopago",
        "conteudo_estrutura": ["INITIAL_BALANCE", "RELEASE_DATE", "TRANSACTION_NET_AMOUNT"],  # MP XLSX
        "banco": "mercadopago",
        "tipo": "extrato",
    },
    "mercadopago_fatura": {
        "extensao": [".pdf"],
        "conteudo_regex": r"mercado\s*pago|mercadopago",
        "banco": "mercadopago",
        "tipo": "fatura",
    },
}


class DetectionEngine:
    """Detecta banco, tipo e período a partir do conteúdo do arquivo"""

    def detect(self, filename: str, content_sample: str, file_bytes: bytes) -> DetectionResult:
        ext = Path(filename).suffix.lower()
        arquivo_hash = hashlib.sha256(file_bytes).hexdigest()
        content_lower = content_sample.lower()

        for key, fp in FINGERPRINTS.items():
            exts = fp.get("extensao", [])
            if ext not in exts:
                continue
            regex = fp.get("conteudo_regex", "")
            cabecalho = fp.get("cabecalho_obrigatorio", [])
            estrutura = fp.get("conteudo_estrutura", [])
            cabecalho_em_conteudo = fp.get("cabecalho_em_conteudo", [])

            # 1. Match por estrutura no conteúdo (mais específico: SALDO ANTERIOR, INITIAL_BALANCE)
            if estrutura and self._estrutura_presente(content_sample, estrutura):
                periodo_inicio, periodo_fim = self._extrair_periodo(content_sample, fp["tipo"])
                mes_fatura = self._periodo_to_mes_fatura(periodo_inicio, periodo_fim)
                return DetectionResult(
                    banco=fp["banco"],
                    tipo=fp["tipo"],
                    periodo_inicio=periodo_inicio,
                    periodo_fim=periodo_fim,
                    confianca=0.9,
                    arquivo_hash=arquivo_hash,
                    mes_fatura=mes_fatura,
                )

            # 2. Match por colunas em qualquer linha (ex: extrato Itaú XLS)
            if cabecalho_em_conteudo and self._cabecalho_em_conteudo(content_sample, cabecalho_em_conteudo):
                periodo_inicio, periodo_fim = self._extrair_periodo(content_sample, fp["tipo"])
                mes_fatura = self._periodo_to_mes_fatura(periodo_inicio, periodo_fim)
                return DetectionResult(
                    banco=fp["banco"],
                    tipo=fp["tipo"],
                    periodo_inicio=periodo_inicio,
                    periodo_fim=periodo_fim,
                    confianca=0.85,
                    arquivo_hash=arquivo_hash,
                    mes_fatura=mes_fatura,
                )

            # 3. Match por cabeçalho na primeira linha (CSV)
            if cabecalho and self._cabecalho_presente(content_sample, cabecalho):
                periodo_inicio, periodo_fim = self._extrair_periodo(content_sample, fp["tipo"])
                mes_fatura = self._periodo_to_mes_fatura(periodo_inicio, periodo_fim)
                return DetectionResult(
                    banco=fp["banco"],
                    tipo=fp["tipo"],
                    periodo_inicio=periodo_inicio,
                    periodo_fim=periodo_fim,
                    confianca=0.85,
                    arquivo_hash=arquivo_hash,
                    mes_fatura=mes_fatura,
                )

            # 4. Match por conteúdo (regex) — menos específico
            if regex and re.search(regex, content_sample, re.IGNORECASE):
                periodo_inicio, periodo_fim = self._extrair_periodo(content_sample, fp["tipo"])
                mes_fatura = self._periodo_to_mes_fatura(periodo_inicio, periodo_fim)
                return DetectionResult(
                    banco=fp["banco"],
                    tipo=fp["tipo"],
                    periodo_inicio=periodo_inicio,
                    periodo_fim=periodo_fim,
                    confianca=0.8,
                    arquivo_hash=arquivo_hash,
                    mes_fatura=mes_fatura,
                )

        # 5. Fallback por filename — só quando conteúdo não identificou (confiança menor)
        filename_norm = filename.lower().replace("ú", "u").replace("ú", "u")
        if "itau" in filename_norm and ext in (".csv", ".xls", ".xlsx", ".pdf"):
            periodo_inicio, periodo_fim = self._extrair_periodo(content_sample, "fatura")
            mes_fatura = self._extrair_mes_do_filename(filename)
            return DetectionResult(
                banco="itau",
                tipo="fatura",
                periodo_inicio=periodo_inicio,
                periodo_fim=periodo_fim,
                confianca=0.6,
                arquivo_hash=arquivo_hash,
                mes_fatura=mes_fatura,
            )
        if ("btg" in filename_norm or "pactual" in filename_norm) and "fatura" in filename_norm and ext in (".xlsx", ".pdf"):
            periodo_inicio, periodo_fim = self._extrair_periodo(content_sample, "fatura")
            mes_fatura = self._extrair_mes_do_filename(filename)
            return DetectionResult(
                banco="btg",
                tipo="fatura",
                periodo_inicio=periodo_inicio,
                periodo_fim=periodo_fim,
                confianca=0.6,
                arquivo_hash=arquivo_hash,
                mes_fatura=mes_fatura,
            )
        if filename_norm.startswith("mp") and ext in (".xlsx", ".pdf") and re.search(r"\d{6}", filename):
            periodo_inicio, periodo_fim = self._extrair_periodo(content_sample, "extrato")
            mes_fatura = re.search(r"(\d{4})(\d{2})", filename)
            mes = f"{mes_fatura.group(1)}{mes_fatura.group(2)}" if mes_fatura else None
            return DetectionResult(
                banco="mercadopago",
                tipo="extrato",
                periodo_inicio=periodo_inicio,
                periodo_fim=periodo_fim,
                confianca=0.6,
                arquivo_hash=arquivo_hash,
                mes_fatura=mes,
            )

        # Fallback: planilha genérica
        return DetectionResult(
            banco="generico",
            tipo="planilha",
            periodo_inicio=None,
            periodo_fim=None,
            confianca=0.3,
            arquivo_hash=arquivo_hash,
            mes_fatura=None,
        )

    def _extrair_periodo(self, content: str, tipo: str) -> tuple[Optional[str], Optional[str]]:
        """Extrai período (início, fim) do conteúdo do arquivo"""
        # DD/MM/YYYY
        datas = re.findall(r"\d{2}/\d{2}/\d{4}", content[:3000])
        if datas:
            try:
                parsed = []
                for d in datas:
                    try:
                        parsed.append(datetime.strptime(d, "%d/%m/%Y"))
                    except ValueError:
                        continue
                if parsed:
                    min_d = min(parsed).date()
                    max_d = max(parsed).date()
                    return str(min_d), str(max_d)
            except (ValueError, TypeError):
                pass
        # YYYY-MM-DD
        datas_iso = re.findall(r"\d{4}-\d{2}-\d{2}", content[:3000])
        if datas_iso:
            try:
                parsed = [datetime.strptime(d, "%Y-%m-%d").date() for d in datas_iso]
                if parsed:
                    return str(min(parsed)), str(max(parsed))
            except (ValueError, TypeError):
                pass
        # YYYYMM (mes_fatura em extratos)
        mes_ref = re.search(r"(\d{4})(\d{2})", content[:1500])
        if mes_ref:
            y, m = mes_ref.groups()
            d = f"{y}-{m}-01"
            return d, d
        return None, None

    def _periodo_to_mes_fatura(self, inicio: Optional[str], fim: Optional[str]) -> Optional[str]:
        """Converte periodo_inicio/fim em mes_fatura (YYYYMM) para duplicata check"""
        if not inicio:
            return None
        try:
            if "-" in inicio:
                parts = inicio.split("-")
                if len(parts) >= 2:
                    return f"{parts[0]}{parts[1]}"
            return None
        except (IndexError, TypeError):
            return None

    def _cabecalho_presente(self, content: str, colunas: list) -> bool:
        """Verifica se as colunas obrigatórias aparecem na primeira linha (ex: Lançamento, Valor)"""
        import unicodedata

        def _norm(s: str) -> str:
            nfd = unicodedata.normalize("NFD", s.lower())
            return "".join(c for c in nfd if unicodedata.category(c) != "Mn")

        primeira_linha = _norm(content.split("\n")[0] if content else "")
        for col in colunas:
            if _norm(col) not in primeira_linha:
                return False
        return True

    def _estrutura_presente(self, content: str, marcadores: list) -> bool:
        """Verifica se pelo menos 2 marcadores de estrutura aparecem no conteúdo."""
        content_lower = content.lower()
        matches = sum(1 for m in marcadores if m.lower() in content_lower)
        return matches >= 2

    def _cabecalho_em_conteudo(self, content: str, colunas: list) -> bool:
        """Verifica se as colunas aparecem em qualquer lugar do conteúdo (ex: extrato XLS)."""
        import unicodedata

        def _norm(s: str) -> str:
            nfd = unicodedata.normalize("NFD", s.lower())
            return "".join(c for c in nfd if unicodedata.category(c) != "Mn")

        conteudo_norm = _norm(content)
        for col in colunas:
            if _norm(col) not in conteudo_norm:
                return False
        return True

    def _extrair_mes_do_filename(self, filename: str) -> Optional[str]:
        """Extrai YYYYMM do filename (ex: fatura-202602.csv -> 202602)"""
        match = re.search(r"(\d{4})[-_]?(\d{2})", filename)
        if match:
            return f"{match.group(1)}{match.group(2)}"
        return None
