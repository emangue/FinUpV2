#!/usr/bin/env python3
"""
Migracao: IdTransacao v4.2.1 -> v5

Recalcula IdTransacao de todos os registros em journal_entries usando o
novo algoritmo v5 (banco + tipo + data + valor, sem nome).

EXECUCAO (dentro do container Docker):
  docker cp scripts/database/recalculate_id_transacao_v5.py finup_backend_dev:/tmp/migrate_v5.py
  docker exec finup_backend_dev python3 /tmp/migrate_v5.py

  Flags:
    --dry-run    Calcula sem salvar (valida unicidade dos novos IDs)
    --user-id N  Migrar apenas um usuario especifico

REVERSAO:
  docker exec -i finup_postgres_dev psql -U finup_user -d finup_db \\
    < temp/backups/backup_before_migration_v5_*.sql
"""

import sys
import argparse
import logging
from pathlib import Path

BANCO_ORIGEM_CLEANUP = {
    "BTG202601.xls": "BTG Pactual",
    "Extrato_2025-11-20_a_2026-01-18_11259347605.xls": "BTG Pactual",
    "BTG": "BTG Pactual",
}


def _inferir_banco_de_filename(banco_origem):
    nome = banco_origem.lower()
    if "btg" in nome or "11259347605" in nome:
        return "BTG Pactual"
    if "mercado" in nome or "_mp_" in nome:
        return "Mercado Pago"
    if "itau" in nome:
        return "Itau"
    if "xp" in nome:
        return "XP"
    if "nubank" in nome:
        return "Nubank"
    if "santander" in nome:
        return "Santander"
    return banco_origem


def limpar_banco_origem(banco_origem):
    if not banco_origem:
        return "Desconhecido"
    if banco_origem in BANCO_ORIGEM_CLEANUP:
        return BANCO_ORIGEM_CLEANUP[banco_origem]
    nome_lower = banco_origem.lower()
    if any(nome_lower.endswith(ext) for ext in (".xls", ".xlsx", ".csv", ".pdf", ".ofx")):
        return _inferir_banco_de_filename(banco_origem)
    return banco_origem


def main():
    parser = argparse.ArgumentParser(description="Migracao IdTransacao v4.2.1 -> v5")
    parser.add_argument("--dry-run", action="store_true",
                        help="Calcula sem salvar (valida unicidade)")
    parser.add_argument("--user-id", type=int, metavar="N",
                        help="Migrar apenas este user_id")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger = logging.getLogger(__name__)

    # Detectar se estamos dentro do container Docker ou rodando localmente
    docker_app_path = Path("/app")
    if docker_app_path.exists() and (docker_app_path / "app" / "core" / "database.py").exists():
        if str(docker_app_path) not in sys.path:
            sys.path.insert(0, str(docker_app_path))
    else:
        backend_path = Path(__file__).parent.parent.parent / "app_dev" / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))

    try:
        from app.core.database import SessionLocal
        from app.domains.transactions.models import JournalEntry
        from app.domains.upload.history_models import UploadHistory  # noqa: F401
        from app.shared.utils.hasher import generate_id_transacao, get_canonical_banco, _normalize_str
        from sqlalchemy import text
    except ImportError as e:
        logger.error(f"Erro de importacao: {e}")
        logger.error("Execute dentro do container: docker exec finup_backend_dev python3 /tmp/migrate_v5.py")
        sys.exit(1)

    db = SessionLocal()
    try:
        # Carregar registros
        query = db.query(JournalEntry)
        if args.user_id:
            query = query.filter(JournalEntry.user_id == args.user_id)
            logger.info(f"Filtrando user_id={args.user_id}")
        entries = query.all()
        total = len(entries)
        logger.info(f"Total de registros: {total}")
        if args.dry_run:
            logger.info("DRY RUN ativo - nenhuma alteracao sera salva")

        # 1. Agrupar por chave v5 para detectar colisoes reais
        #    (mesmo banco + tipo + data + valor para o mesmo usuario)
        #
        #    IMPORTANTE: o base_key DEVE usar os mesmos valores canônicos que
        #    generate_id_transacao usa internamente (get_canonical_banco +
        #    _normalize_str), caso contrário registros que produziriam o mesmo
        #    hash ficam em grupos separados e ambos recebem seq=1 → colisão.
        #
        #    Exemplo do bug: tipodocumento="extrato" e tipodocumento="Extrato"
        #    → base_keys diferentes → grupos separados → seq=1 nos dois
        #    → generate_id_transacao normaliza ambos para "EXTRATO"
        #    → mesmo hash → colisão detectada ao validar unicidade.
        key_to_records = {}
        for entry in entries:
            banco_limpo = limpar_banco_origem(entry.banco_origem or "")
            tipo_raw = entry.tipodocumento or "extrato"

            # Normalizar com as MESMAS funções que o hasher usa internamente
            banco_canonical = get_canonical_banco(banco_limpo)   # "BTG Pactual" → "BTG"
            tipo_canonical  = _normalize_str(tipo_raw)           # "Extrato" → "EXTRATO"

            base_key = f"{entry.user_id}|{banco_canonical}|{tipo_canonical}|{entry.Data}|{float(entry.Valor):.2f}"
            if base_key not in key_to_records:
                key_to_records[base_key] = []
            key_to_records[base_key].append({
                "db_id": entry.id,
                "banco": banco_limpo,           # valor limpo para gravar no DB
                "tipo": tipo_raw,               # valor raw para passar ao hasher (que normaliza internamente)
                "data": entry.Data,
                "valor": entry.Valor,
                "user_id": entry.user_id,
                "banco_original": entry.banco_origem or "",
            })

        # 2. Calcular novos IDs; colisoes reais recebem sequencia 1, 2, 3...
        final_updates = {}
        bancos_corrigidos = 0
        colisoes_reais = 0
        for records in key_to_records.values():
            for seq, record in enumerate(records, 1):
                if seq > 1:
                    colisoes_reais += 1
                    logger.warning(
                        f"  Colisao seq={seq}: user={record['user_id']} "
                        f"banco={record['banco']} data={record['data']} "
                        f"valor={record['valor']:.2f}"
                    )
                novo_id = generate_id_transacao(
                    data=record["data"],
                    banco=record["banco"],
                    tipo_documento=record["tipo"],
                    valor=record["valor"],
                    user_id=record["user_id"],
                    sequencia=seq,
                )
                final_updates[record["db_id"]] = (novo_id, record["banco"])
                if record["banco"] != record["banco_original"]:
                    bancos_corrigidos += 1

        # 3. Validar unicidade antes de tocar no banco
        all_ids = [v[0] for v in final_updates.values()]
        if len(all_ids) != len(set(all_ids)):
            logger.error("IDs DUPLICADOS apos calculo! Abortando.")
            sys.exit(1)
        logger.info(f"Unicidade OK: {len(set(all_ids))} IDs unicos")
        logger.info(f"Bancos corrigidos : {bancos_corrigidos}")
        logger.info(f"Colisoes reais    : {colisoes_reais}")

        if args.dry_run:
            logger.info("DRY RUN: nenhuma alteracao salva.")
            return

        # 4. Aplicar via raw SQL (estrategia segura):
        #    DROP INDEX -> INSERT em temp table -> UPDATE bulk -> RECREATE INDEX
        #    Evita UniqueViolation do ORM flush:
        #    novo hash(A) == hash_antigo(B) antes de B ser atualizado
        logger.info("Aplicando via raw SQL (DROP INDEX + bulk UPDATE + RECREATE INDEX)...")

        db.execute(text('DROP INDEX IF EXISTS "ix_journal_entries_IdTransacao"'))

        db.execute(text("""
            CREATE TEMP TABLE _id_migration (
                db_id       INTEGER PRIMARY KEY,
                new_id      TEXT NOT NULL,
                banco_limpo TEXT NOT NULL
            ) ON COMMIT DROP
        """))

        # Inserir novos IDs em lotes de 200 (evita queries gigantes)
        items = list(final_updates.items())
        BATCH = 200
        for i in range(0, len(items), BATCH):
            lote = items[i:i + BATCH]
            rows_sql = ", ".join(f"(:{j}a, :{j}b, :{j}c)" for j in range(len(lote)))
            params = {}
            for j, (db_id, (new_id, banco_limpo)) in enumerate(lote):
                params[f"{j}a"] = db_id
                params[f"{j}b"] = new_id
                params[f"{j}c"] = banco_limpo
            db.execute(text(f"INSERT INTO _id_migration VALUES {rows_sql}"), params)
            logger.info(f"  Lote {i // BATCH + 1}/{-(-len(items) // BATCH)}: {len(lote)} registros")

        # UPDATE em um unico statement (sem constraint ativa = sem conflito)
        result = db.execute(text("""
            UPDATE journal_entries je
               SET "IdTransacao" = m.new_id,
                   banco_origem  = m.banco_limpo
              FROM _id_migration m
             WHERE je.id = m.db_id
        """))
        atualizados = result.rowcount

        # Recriar index unico
        db.execute(text(
            'CREATE UNIQUE INDEX "ix_journal_entries_IdTransacao" '
            'ON journal_entries ("IdTransacao")'
        ))
        db.commit()

        logger.info("=" * 50)
        logger.info(f"  Total registros   : {total}")
        logger.info(f"  Rows atualizados  : {atualizados}")
        logger.info(f"  Bancos corrigidos : {bancos_corrigidos}")
        logger.info(f"  Colisoes tratadas : {colisoes_reais}")
        logger.info("MIGRACAO CONCLUIDA COM SUCESSO!")

    except Exception as e:
        db.rollback()
        logger.error(f"ROLLBACK executado: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
