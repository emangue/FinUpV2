#!/usr/bin/env python3
"""
Diagnóstico: classe_ativo dos investimentos

Verifica qual classe_ativo cada investimento tem na base.
Útil para entender por que FGTS/Automóvel aparecem em Passivo quando deveriam ser Ativo.

Uso:
  cd app_dev/backend && python ../../scripts/diagnostic/verificar_classe_ativo_investimentos.py
"""
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND = ROOT / "app_dev" / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

from dotenv import load_dotenv
load_dotenv(BACKEND / ".env")

from sqlalchemy import create_engine, text


def main():
    db_path = BACKEND / "database" / "financas_dev.db"
    if not db_path.exists():
        print(f"❌ Banco não encontrado: {db_path}")
        return 1

    engine = create_engine(f"sqlite:///{db_path}")

    with engine.connect() as conn:
        # Listar investimentos com tipo_investimento e classe_ativo
        r = conn.execute(text("""
            SELECT p.id, p.user_id, p.nome_produto, p.tipo_investimento,
                   p.classe_ativo,
                   (SELECT SUM(h.valor_total) FROM investimentos_historico h
                    WHERE h.investimento_id = p.id
                    AND h.anomes = (SELECT MAX(anomes) FROM investimentos_historico
                                   WHERE investimento_id = p.id)) as valor_ultimo_mes
            FROM investimentos_portfolio p
            WHERE p.ativo = 1
            ORDER BY p.tipo_investimento, p.classe_ativo
        """))
        rows = r.fetchall()

    print("=" * 90)
    print("INVESTIMENTOS: tipo_investimento x classe_ativo")
    print("=" * 90)
    print(f"{'id':<6} {'user':<5} {'tipo_investimento':<22} {'classe_ativo':<12} {'valor':>15} nome_produto")
    print("-" * 90)

    tipos_suspeitos = []
    for row in rows:
        id_, user_id, nome, tipo, classe, valor = row
        classe_str = classe if classe else "(NULL)"
        valor_str = f"{float(valor or 0):,.2f}" if valor else "-"
        if tipo in ("FGTS", "Automóvel") and classe != "Ativo":
            tipos_suspeitos.append((tipo, classe_str, nome))
        print(f"{id_:<6} {user_id:<5} {tipo:<22} {classe_str:<12} {valor_str:>15} {nome[:40]}")

    print("=" * 90)
    if tipos_suspeitos:
        print("\n⚠️  SUSPEITOS (FGTS/Automóvel com classe_ativo != Ativo):")
        for tipo, classe, nome in tipos_suspeitos:
            print(f"   - {tipo}: classe_ativo={classe} | {nome}")
        print("\n→ Esses investimentos aparecem na aba Passivo porque têm classe_ativo='Passivo' ou NULL.")
        print("→ Corrija no banco: UPDATE investimentos_portfolio SET classe_ativo='Ativo' WHERE id IN (...);")
    else:
        print("\n✅ FGTS e Automóvel não encontrados com classe_ativo incorreta.")
        print("   Se ainda aparecem em Passivo, verifique se há duplicatas ou outro user_id.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
