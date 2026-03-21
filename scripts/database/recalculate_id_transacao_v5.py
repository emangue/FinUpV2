#!/usr/bin/env python3
"""
Migração: IdTransacao v4.2.1 → v5

Recalcula IdTransacao de todos os registros em journal_entries usando o
novo algoritmo v5 (banco + tipo + data + valor, sem nome).

PRÉ-REQUISITOS:
  1. Backup do banco: ./scripts/deploy/backup_daily.sh
  2. Containers Docker rodando: ./scripts/deploy/quick_start_docker.sh
  3. Testes unitários passando: python3 scripts/testing/test_idtransacao_v5.py

EXECUÇÃO (dentro do container Docker):
  docker exec finup_backend_dev python3 \
    /app/scripts/database/recalculate_id_transacao_v5.py

  Flags:
    --dry-run    Calcula sem salvar (mostra preview)
    --user-id N  Migrar apenas um usuário específico

REVERSÃO:
  Não é possível reverter automaticamente.
  Restaurar backup criado antes da execução.
"""

import sys
import argparse
import logging
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# Mapa explícito: banco_origem sujo (filenames) → banco canônico
# Levantamento feito em 21/03/2026 — user_id=1, 29 registros afetados
# ──────────────────────────────────────────────────────────────────────────────
BANCO_ORIGEM_CLEANUP: dict = {
    'BTG202601.xls':                                      'BTG Pactual',
    'Extrato_2025-11-20_a_2026-01-18_11259347605.xls':    'BTG Pactual',
    # Adicionar aqui novos casos conforme encontrados:
    # 'NomeArquivo.xls': 'Banco Correto',
}


def _inferir_banco_de_filename(banco_origem: str) -> str:
    """
    Heurística para inferir banco a partir de filename não mapeado explicitamente.
    """
    nome = banco_origem.lower()
    if 'btg' in nome or '11259347605' in nome:
        return 'BTG Pactual'
    if 'mercado' in nome or '_mp_' in nome:
        return 'Mercado Pago'
    if 'itau' in nome or 'itaú' in nome:
        return 'Itaú'
    if 'xp' in nome:
        return 'XP'
    if 'nubank' in nome or 'nu_' in nome:
        return 'Nubank'
    if 'santander' in nome:
        return 'Santander'
    # Não reconhecido — retorna original (canonical fallback no hasher)
    return banco_origem


def limpar_banco_origem(banco_origem: str) -> str:
    """Retorna o banco canônico para o banco_origem fornecido."""
    if not banco_origem:
        return 'Desconhecido'
    # 1. Mapa explícito (casos conhecidos — mais confiável)
    if banco_origem in BANCO_ORIGEM_CLEANUP:
        return BANCO_ORIGEM_CLEANUP[banco_origem]
    # 2. Heurística: parece filename (tem extensão, sem barras de data DD/MM)
    nome_lower = banco_origem.lower()
    if any(nome_lower.endswith(ext) for ext in ('.xls', '.xlsx', '.csv', '.pdf', '.ofx')):
        return _inferir_banco_de_filename(banco_origem)
    # 3. Banco já está limpo
    return banco_origem


def main():
    parser = argparse.ArgumentParser(
        description='Migração IdTransacao v4.2.1 → v5',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Simula sem salvar nenhuma alteração no banco')
    parser.add_argument('--user-id', type=int, metavar='N',
                        help='Migrar apenas este user_id (default: todos)')
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Adicionar path do backend para imports
    backend_path = Path(__file__).parent.parent.parent / 'app_dev' / 'backend'
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))

    try:
        from app.core.database import SessionLocal
        from app.domains.transactions.models import JournalEntry
        from app.shared.utils.hasher import generate_id_transacao, get_canonical_banco
    except ImportError as e:
        logger.error(f"Erro de importação: {e}")
        logger.error("Execute dentro do container Docker:")
        logger.error("  docker exec finup_backend_dev python3 /app/scripts/database/recalculate_id_transacao_v5.py")
        sys.exit(1)

    db = SessionLocal()
    try:
        # ── Carregar registros ─────────────────────────────────────────────────
        query = db.query(JournalEntry)
        if args.user_id:
            query = query.filter(JournalEntry.user_id == args.user_id)
            logger.info(f"🎯 Filtrando apenas user_id={args.user_id}")
        entries = query.all()

        total = len(entries)
        logger.info(f"📊 Total de registros a migrar: {total}")

        if args.dry_run:
            logger.info("⚠️  DRY RUN ativo — nenhuma alteração será salva")

        # ── Estatísticas ───────────────────────────────────────────────────────
        bancos_corrigidos = 0
        bancos_ja_limpos  = 0
        erros             = 0
        atualizados       = 0

        for entry in entries:
            try:
                banco_original = entry.banco_origem or ''
                banco_limpo    = limpar_banco_origem(banco_original)

                if banco_limpo != banco_original:
                    bancos_corrigidos += 1
                    logger.debug(f"  banco corrigido: '{banco_original}' → '{banco_limpo}'")
                else:
                    bancos_ja_limpos += 1

                tipo = entry.tipodocumento or 'extrato'

                # sequencia: usar campo se disponível, fallback 1
                seq = getattr(entry, 'sequencia', None) or 1

                novo_id = generate_id_transacao(
                    data=entry.Data,
                    banco=banco_limpo,
                    tipo_documento=tipo,
                    valor=entry.Valor,
                    user_id=entry.user_id,
                    sequencia=seq
                )

                if not args.dry_run:
                    entry.IdTransacao  = novo_id
                    entry.banco_origem = banco_limpo  # persiste banco limpo
                    atualizados += 1

            except Exception as e:
                erros += 1
                entry_id = getattr(entry, 'id', getattr(entry, 'IdTransacao', '?'))
                logger.error(f"  ERRO entry={entry_id}: {e}")

        # ── Resumo ─────────────────────────────────────────────────────────────
        logger.info("=" * 60)
        logger.info(f"  Registros processados  : {total}")
        logger.info(f"  Bancos já limpos       : {bancos_ja_limpos}")
        logger.info(f"  Bancos corrigidos      : {bancos_corrigidos}")
        logger.info(f"  Erros                  : {erros}")

        if args.dry_run:
            logger.info("  ⚠️  DRY RUN — nenhuma alteração salva")
        elif erros == 0:
            db.commit()
            logger.info(f"  ✅ Atualizados         : {atualizados}")
            logger.info("✅ Commit realizado com sucesso")
        else:
            db.rollback()
            logger.error(f"❌ Rollback por {erros} erros — verifique os logs acima")
            sys.exit(1)

    finally:
        db.close()


if __name__ == '__main__':
    main()
