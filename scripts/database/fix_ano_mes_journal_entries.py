#!/usr/bin/env python3
"""
Corrige Ano e Mes inconsistentes em journal_entries.

Regra: Ano e Mes devem ser derivados de MesFatura (formato YYYYMM).
- MesFatura=202601 → Ano=2026, Mes=1
- Quando Ano ou Mes não batem com MesFatura, corrige.

Uso:
  python fix_ano_mes_journal_entries.py          # Executa correção
  python fix_ano_mes_journal_entries.py --dry-run # Apenas lista o que seria corrigido
"""
import sqlite3
import sys
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent.parent / "app_dev" / "backend" / "database" / "financas_dev.db"


def extrair_ano_mes_de_mesfatura(mes_fatura: str) -> Optional[tuple]:
    """
    Extrai ano e mês de MesFatura (YYYYMM ou YYYY-MM).
    Retorna (ano, mes) ou None se inválido.
    """
    if not mes_fatura or not isinstance(mes_fatura, str):
        return None
    # Normalizar: remover hífen
    mf = mes_fatura.replace("-", "").strip()
    if len(mf) < 6:
        return None
    try:
        ano = int(mf[:4])
        mes = int(mf[4:6])
        if 1 <= mes <= 12 and 2000 <= ano <= 2100:
            return (ano, mes)
    except ValueError:
        pass
    return None


def fix_ano_mes(dry_run: bool = False) -> int:
    """Corrige Ano e Mes em journal_entries onde não batem com MesFatura."""
    print("🔧 Corrigindo Ano/Mes inconsistentes em journal_entries")
    print(f"📂 Banco: {DB_PATH}\n")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Buscar registros com MesFatura preenchido
        cursor.execute(
            """
            SELECT id, MesFatura, Ano, Mes, Estabelecimento, Data, tipodocumento
            FROM journal_entries
            WHERE MesFatura IS NOT NULL AND MesFatura != ''
            """
        )
        rows = cursor.fetchall()

        to_fix = []
        for row in rows:
            parsed = extrair_ano_mes_de_mesfatura(row["MesFatura"])
            if not parsed:
                continue
            ano_esperado, mes_esperado = parsed
            ano_atual = row["Ano"]
            mes_atual = row["Mes"]

            # Ano ou Mes incorretos (inclui NULL)
            if ano_atual != ano_esperado or mes_atual != mes_esperado:
                to_fix.append({
                    "id": row["id"],
                    "MesFatura": row["MesFatura"],
                    "Ano_atual": ano_atual,
                    "Mes_atual": mes_atual,
                    "Ano_novo": ano_esperado,
                    "Mes_novo": mes_esperado,
                    "Estabelecimento": (row["Estabelecimento"] or "")[:40],
                    "Data": row["Data"],
                    "tipodocumento": row["tipodocumento"],
                })

        if not to_fix:
            print("✅ Nenhum registro inconsistente encontrado.\n")
            return 0

        print(f"📋 Encontrados {len(to_fix)} registros inconsistentes:\n")
        for i, r in enumerate(to_fix[:15], 1):
            print(
                f"   {i}. id={r['id']} | MesFatura={r['MesFatura']} | "
                f"Ano {r['Ano_atual']}→{r['Ano_novo']} | Mes {r['Mes_atual']}→{r['Mes_novo']} | "
                f"{r['Estabelecimento']}... | {r['tipodocumento']}"
            )
        if len(to_fix) > 15:
            print(f"   ... e mais {len(to_fix) - 15} registros\n")

        if dry_run:
            print("🔍 Modo dry-run: nenhuma alteração feita.\n")
            return 0

        # Atualizar
        updated = 0
        for r in to_fix:
            cursor.execute(
                "UPDATE journal_entries SET Ano = ?, Mes = ? WHERE id = ?",
                (r["Ano_novo"], r["Mes_novo"], r["id"]),
            )
            updated += cursor.rowcount

        conn.commit()
        print(f"\n✅ {updated} registros corrigidos.\n")
        return 0

    except Exception as e:
        conn.rollback()
        print(f"❌ Erro: {e}")
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    sys.exit(fix_ano_mes(dry_run=dry_run))
