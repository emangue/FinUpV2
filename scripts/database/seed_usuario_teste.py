#!/usr/bin/env python3
"""
seed_usuario_teste.py — Recria dados do usuário de teste a partir do admin

Fluxo:
  1. Apaga TODOS os journal_entries do user_id=4 (teste@email.com)
  2. Copia todos os registros do user_id=1 (admin)
  3. Aplica fator aleatório ~10% nos valores (entre 8% e 12%)
  4. Gera IdTransacao únicos para evitar conflito com UNIQUE constraint

Uso (do Docker):
    docker exec finup_backend_dev python /app/scripts/seed_usuario_teste.py

Uso (local, com PostgreSQL exposto na 5432):
    cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
    source app_dev/venv/bin/activate
    python scripts/database/seed_usuario_teste.py
"""

import os
import sys
import random
import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# ─── Conexão ──────────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://finup_user:finup_password_dev_2026@localhost:5432/finup_db"
)

SOURCE_USER_ID = 1   # admin@financas.com — fonte dos dados
TARGET_USER_ID = 4   # teste@email.com — destino

FATOR_MIN = 0.08   # 8%
FATOR_MAX = 0.12   # 12%


def gerar_id_transacao_teste(id_original: str) -> str:
    """Gera IdTransacao único para o user de teste, derivado do original."""
    if not id_original:
        return None
    # MD5 do original + sufixo para garantir unicidade e evitar colisão
    base = f"TESTE4_{id_original}"
    return hashlib.md5(base.encode()).hexdigest()[:32]


def aplicar_fator_aleatorio(valor: float) -> float:
    """Aplica fator aleatório entre 8% e 12%, preservando o sinal."""
    if valor is None:
        return None
    fator = random.uniform(FATOR_MIN, FATOR_MAX)
    resultado = valor * fator
    # Arredondar para 2 casas decimais
    return round(resultado, 2)


def main():
    print("=" * 60)
    print("🌱 SEED: usuário de teste (user_id=4)")
    print(f"   Fonte  : user_id={SOURCE_USER_ID} (admin@financas.com)")
    print(f"   Destino: user_id={TARGET_USER_ID} (teste@email.com)")
    print(f"   Fator  : {FATOR_MIN*100:.0f}%–{FATOR_MAX*100:.0f}% dos valores reais")
    print("=" * 60)

    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # ─── 1. Contar dados existentes ───────────────────────────────────
        cur.execute("SELECT COUNT(*) as n FROM journal_entries WHERE user_id = %s", (TARGET_USER_ID,))
        count_antes = cur.fetchone()["n"]
        print(f"\n📊 Registros atuais do user {TARGET_USER_ID}: {count_antes}")

        # ─── 2. Deletar dados do user de teste ───────────────────────────
        print(f"🗑️  Deletando {count_antes} registros do user_id={TARGET_USER_ID}...")
        cur.execute("DELETE FROM journal_entries WHERE user_id = %s", (TARGET_USER_ID,))
        deletados = cur.rowcount
        print(f"   ✅ Deletados: {deletados}")

        # ─── 3. Buscar todos os dados do admin ────────────────────────────
        print(f"\n📥 Buscando registros do user_id={SOURCE_USER_ID}...")
        cur.execute("""
            SELECT
                "Data", "Estabelecimento", "Valor", "ValorPositivo",
                "TipoTransacao", "TipoGasto", "GRUPO", "SUBGRUPO",
                "CategoriaGeral", categoria_orcamento_id,
                "IdTransacao", "IdParcela", "EstabelecimentoBase",
                parcela_atual, "TotalParcelas",
                arquivo_origem, banco_origem, tipodocumento,
                origem_classificacao, "MesFatura",
                "Ano", "Mes", "NomeCartao", "IgnorarDashboard"
            FROM journal_entries
            WHERE user_id = %s
            ORDER BY "Ano", "Mes", id
        """, (SOURCE_USER_ID,))
        registros = cur.fetchall()
        print(f"   ✅ Encontrados: {len(registros)} registros")

        # ─── 4. Inserir com valores escalados ─────────────────────────────
        print(f"\n✍️  Inserindo com fator {FATOR_MIN*100:.0f}%–{FATOR_MAX*100:.0f}%...")

        inseridos = 0
        erros = 0
        agora = datetime.now()

        for row in registros:
            novo_valor = aplicar_fator_aleatorio(row["Valor"])
            novo_valor_positivo = aplicar_fator_aleatorio(row["ValorPositivo"])
            novo_id_transacao = gerar_id_transacao_teste(row["IdTransacao"])
            novo_id_parcela = (
                gerar_id_transacao_teste(row["IdParcela"])
                if row["IdParcela"] else None
            )

            try:
                cur.execute("""
                    INSERT INTO journal_entries (
                        user_id, "Data", "Estabelecimento", "Valor", "ValorPositivo",
                        "TipoTransacao", "TipoGasto", "GRUPO", "SUBGRUPO",
                        "CategoriaGeral", categoria_orcamento_id,
                        "IdTransacao", "IdParcela", "EstabelecimentoBase",
                        parcela_atual, "TotalParcelas",
                        arquivo_origem, banco_origem, tipodocumento,
                        origem_classificacao, "MesFatura",
                        "Ano", "Mes", "NomeCartao", "IgnorarDashboard",
                        session_id, upload_history_id, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s,
                        %s, %s, %s,
                        %s, %s,
                        %s, %s, %s,
                        %s, %s,
                        %s, %s, %s, %s,
                        NULL, NULL, %s
                    )
                """, (
                    TARGET_USER_ID,
                    row["Data"], row["Estabelecimento"],
                    novo_valor, novo_valor_positivo,
                    row["TipoTransacao"], row["TipoGasto"],
                    row["GRUPO"], row["SUBGRUPO"],
                    row["CategoriaGeral"], row["categoria_orcamento_id"],
                    novo_id_transacao, novo_id_parcela,
                    row["EstabelecimentoBase"],
                    row["parcela_atual"], row["TotalParcelas"],
                    row["arquivo_origem"], row["banco_origem"],
                    row["tipodocumento"], row["origem_classificacao"],
                    row["MesFatura"], row["Ano"], row["Mes"],
                    row["NomeCartao"], row["IgnorarDashboard"],
                    agora,
                ))
                inseridos += 1
            except Exception as e:
                erros += 1
                if erros <= 3:
                    print(f"   ⚠️  Erro no registro (IdTransacao={row['IdTransacao']}): {e}")

        # ─── 5. Commit ────────────────────────────────────────────────────
        conn.commit()

        # ─── 6. Resumo final ──────────────────────────────────────────────
        cur.execute("SELECT COUNT(*) as n FROM journal_entries WHERE user_id = %s", (TARGET_USER_ID,))
        count_depois = cur.fetchone()["n"]

        cur.execute("""
            SELECT
                MIN("Valor")::numeric(10,2) as min_val,
                MAX("Valor")::numeric(10,2) as max_val,
                AVG("Valor")::numeric(10,2) as avg_val,
                MIN("Ano") as ano_min,
                MAX("Ano") as ano_max
            FROM journal_entries WHERE user_id = %s
        """, (TARGET_USER_ID,))
        stats = cur.fetchone()

        print(f"\n{'='*60}")
        print(f"✅ CONCLUÍDO!")
        print(f"   Inseridos : {inseridos}")
        print(f"   Erros     : {erros}")
        print(f"   Total DB  : {count_depois}")
        print(f"   Período   : {stats['ano_min']}–{stats['ano_max']}")
        print(f"   Valores   : {stats['min_val']} a {stats['max_val']} (avg {stats['avg_val']})")
        print(f"{'='*60}")

        if erros > 0:
            print(f"\n⚠️  {erros} registros com erro — verifique IdTransacao duplicados")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERRO FATAL: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
