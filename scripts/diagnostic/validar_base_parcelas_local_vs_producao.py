#!/usr/bin/env python3
"""
Validação: Base Parcelas - Local vs Produção

Por que o mesmo arquivo (fatura-202601.csv) mostra:
- Local: Base Parcelas (15)
- Produção (meufinup.com.br): Base Parcelas (0)

CAUSA: A tabela base_parcelas é diferente em cada ambiente.
- Local (SQLite): populada por uploads confirmados anteriormente
- Produção (PostgreSQL): pode estar vazia ou com user_id diferente

Uso:
  Local:  cd app_dev/backend && python ../../scripts/diagnostic/validar_base_parcelas_local_vs_producao.py
  Server: cd /var/www/finup/app_dev/backend && source ../venv/bin/activate && python ../../scripts/diagnostic/validar_base_parcelas_local_vs_producao.py
"""
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND = ROOT / "app_dev" / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)


def main():
    from sqlalchemy import create_engine, text
    from app.core.config import settings

    print("=" * 70)
    print("VALIDAÇÃO: Base Parcelas - Local vs Produção")
    print("=" * 70)

    # Detectar ambiente
    is_postgres = settings.is_postgres
    db_type = "PostgreSQL (produção)" if is_postgres else "SQLite (local)"
    print(f"\n📌 Ambiente atual: {db_type}")
    if is_postgres:
        # Mascarar senha na exibição
        url_display = settings.DATABASE_URL
        if "@" in url_display:
            parts = url_display.split("@")
            user_part = parts[0].split("//")[1] if "//" in parts[0] else parts[0]
            if ":" in user_part:
                user = user_part.split(":")[0]
                url_display = url_display.replace(user_part, f"{user}:****")
        print(f"   Conexão: {url_display[:60]}...")
    else:
        print(f"   Banco: {settings.DATABASE_PATH}")

    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        # Contagem por user_id
        result = conn.execute(text("""
            SELECT user_id, COUNT(*) as total
            FROM base_parcelas
            GROUP BY user_id
            ORDER BY user_id
        """))
        rows = result.fetchall()

        print(f"\n📊 base_parcelas por user_id:")
        if not rows:
            print("   ❌ VAZIA! Nenhum registro em base_parcelas.")
            print("\n   CAUSA: base_parcelas só é populada APÓS confirmar um upload.")
            print("   SOLUÇÃO: Faça upload → confirme → no próximo upload, Base Parcelas aparecerá.")
            return 0

        total_geral = 0
        for r in rows:
            uid, count = r[0], r[1]
            total_geral += count
            print(f"   user_id={uid}: {count} parcelas")

        print(f"\n   Total: {total_geral} parcelas")

        # Amostra de parcelas (para debug)
        result2 = conn.execute(text("""
            SELECT id_parcela, estabelecimento_base, valor_parcela, qtd_parcelas, user_id
            FROM base_parcelas
            ORDER BY user_id, estabelecimento_base
            LIMIT 5
        """))
        amostra = result2.fetchall()
        print(f"\n📋 Amostra (5 primeiras):")
        for r in amostra:
            print(f"   {r[1][:35]:35} | R${r[2]:.2f} | {r[3]}x | user={r[4]}")

    print("\n" + "=" * 70)
    print("CONCLUSÃO:")
    if not rows:
        print("  → Base Parcelas (0) no preview: base_parcelas está VAZIA neste ambiente.")
        print("  → Confirme o primeiro upload para popular a base.")
    else:
        print("  → Se Base Parcelas ainda mostra 0 no preview:")
        print("    1. Verifique qual user_id está logado (deve ser o mesmo das parcelas)")
        print("    2. Compare com outro ambiente: scripts/diagnostic/exportar_base_parcelas_para_producao.py")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
