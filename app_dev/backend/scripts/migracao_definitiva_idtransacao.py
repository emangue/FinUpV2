#!/usr/bin/env python3
"""
MIGRAÇÃO DEFINITIVA - IdTransacao v3.0.0

Estratégia Final:
1. Usa apenas UPPERCASE (preserva /, *, -, etc)
2. Sequência obrigatória para transações idênticas
3. Ordena por (Data, Estabelecimento, Valor, id) para determinismo
4. Backup automático antes de modificar

Autor: Sistema de Finanças V4
Data: 10/01/2026
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import shutil

# Adiciona o diretório raiz do backend ao path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.domains.transactions.models import JournalEntry
from app.shared.utils.hasher import generate_id_transacao


def criar_backup(db_path: Path) -> Path:
    """Cria backup do banco de dados"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = db_path.parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    backup_path = backup_dir / f"{db_path.stem}_backup_v3_{timestamp}{db_path.suffix}"
    shutil.copy2(db_path, backup_path)
    
    print(f"✅ Backup criado: {backup_path}")
    return backup_path


def recalcular_idtransacao_definitivo(dry_run: bool = True):
    """
    Recalcula TODOS os IdTransacao com a estratégia definitiva v3.0.0
    
    Args:
        dry_run: Se True, apenas simula (não commita)
    """
    # Conecta ao banco
    db_path = backend_dir / "database" / "financas_dev.db"
    
    if not db_path.exists():
        print(f"❌ Banco não encontrado: {db_path}")
        return
    
    print(f"📂 Banco de dados: {db_path}")
    print(f"🔍 Modo: {'DRY RUN (simulação)' if dry_run else 'EXECUÇÃO REAL'}")
    print()
    
    # Criar backup antes de modificar
    if not dry_run:
        criar_backup(db_path)
        print()
    
    # Conectar ao banco
    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Buscar todas as transações ordenadas para determinismo
        print("📥 Carregando transações do banco...")
        transacoes = session.query(JournalEntry).order_by(
            JournalEntry.Data,
            JournalEntry.Estabelecimento,
            JournalEntry.Valor,
            JournalEntry.id
        ).all()
        
        print(f"   Total: {len(transacoes)} transações\n")
        
        # Rastrear duplicatas: {chave: contador}
        duplicatas_map = {}
        modificadas = 0
        mantidas = 0
        duplicatas_numeradas = 0
        erros = 0
        mudancas_preview = []
        
        print("🔄 Processando transações...")
        print("=" * 80)
        
        for i, transacao in enumerate(transacoes, 1):
            try:
                # Normalizar valores para chave
                data = transacao.Data
                estabelecimento = transacao.Estabelecimento
                valor = transacao.Valor
                
                # Criar chave única para detectar duplicatas
                # Usa uppercase para comparação (mesma lógica do hash)
                estab_upper = str(estabelecimento).upper().strip()
                chave_unica = f"{data}|{estab_upper}|{valor:.2f}"
                
                # Incrementar contador de ocorrências
                if chave_unica not in duplicatas_map:
                    duplicatas_map[chave_unica] = 1
                else:
                    duplicatas_map[chave_unica] += 1
                
                sequencia = duplicatas_map[chave_unica]
                
                # Gerar novo IdTransacao
                novo_id = generate_id_transacao(
                    data=data,
                    estabelecimento=estabelecimento,
                    valor=valor,
                    sequencia=sequencia
                )
                
                # Comparar com IdTransacao atual
                id_atual = transacao.IdTransacao
                
                if novo_id != id_atual:
                    modificadas += 1
                    
                    # Mostrar primeiras 20 mudanças
                    if modificadas <= 20:
                        seq_info = f" [Seq: {sequencia}]" if sequencia > 1 else ""
                        mudancas_preview.append({
                            'id': transacao.id,
                            'data': data,
                            'estabelecimento': estabelecimento[:40],
                            'valor': valor,
                            'id_antigo': id_atual,
                            'id_novo': novo_id,
                            'sequencia': sequencia
                        })
                    
                    if sequencia > 1:
                        duplicatas_numeradas += 1
                    
                    # Atualizar no banco (se não for dry run)
                    if not dry_run:
                        transacao.IdTransacao = novo_id
                else:
                    mantidas += 1
                
                # Progress a cada 500 transações
                if i % 500 == 0:
                    print(f"   Processadas: {i}/{len(transacoes)} | "
                          f"Modificadas: {modificadas} | Mantidas: {mantidas}")
            
            except Exception as e:
                erros += 1
                print(f"❌ Erro na transação {transacao.id}: {str(e)}")
        
        print("=" * 80)
        print()
        
        # Mostrar preview das mudanças
        if mudancas_preview:
            print("📋 PREVIEW DAS MUDANÇAS (primeiras 20):")
            print("-" * 80)
            for mudanca in mudancas_preview[:20]:
                seq_label = f" [Seq {mudanca['sequencia']}]" if mudanca['sequencia'] > 1 else ""
                print(f"ID {mudanca['id']}: {mudanca['data']} | {mudanca['estabelecimento']}")
                print(f"   Valor: {mudanca['valor']:.2f}{seq_label}")
                print(f"   ❌ Antigo: {mudanca['id_antigo']}")
                print(f"   ✅ Novo:   {mudanca['id_novo']}")
                print()
        
        # Resumo
        print("📊 RESUMO:")
        print(f"   Total processadas: {len(transacoes)}")
        print(f"   ✅ Modificadas: {modificadas}")
        print(f"   ➡️  Mantidas: {mantidas}")
        print(f"   🔢 Duplicatas numeradas (seq > 1): {duplicatas_numeradas}")
        print(f"   ❌ Erros: {erros}")
        print()
        
        # Commit ou rollback
        if not dry_run:
            print("💾 Commitando mudanças no banco...")
            session.commit()
            print("✅ Migração concluída com sucesso!")
            print()
            
            # Verificar se há duplicatas após migração
            print("🔍 Verificando duplicatas após recálculo...")
            duplicatas = session.query(
                JournalEntry.IdTransacao,
                func.count(JournalEntry.id).label('count')
            ).group_by(
                JournalEntry.IdTransacao
            ).having(
                func.count(JournalEntry.id) > 1
            ).all()
            
            if duplicatas:
                print(f"⚠️  ATENÇÃO: Encontradas {len(duplicatas)} duplicatas:")
                for id_trans, count in duplicatas[:10]:
                    print(f"   IdTransacao {id_trans}: {count} ocorrências")
            else:
                print("   ✅ Nenhuma duplicata encontrada!")
        else:
            print("ℹ️  DRY RUN - Nenhuma mudança foi salva no banco")
            session.rollback()
    
    except Exception as e:
        print(f"❌ Erro fatal: {str(e)}")
        session.rollback()
        raise
    
    finally:
        session.close()


if __name__ == "__main__":
    print("=" * 80)
    print("MIGRAÇÃO DEFINITIVA - IdTransacao v3.0.0")
    print("=" * 80)
    print()
    print("ESTRATÉGIA:")
    print("  • UPPERCASE apenas (preserva /, *, -, etc)")
    print("  • Sequência para diferenciar transações idênticas")
    print("  • Ordenação determinística (Data, Estabelecimento, Valor, id)")
    print()
    
    # Perguntar se quer executar
    resposta = input("Deseja executar a migração? (DRY RUN primeiro) [sim/nao]: ").strip().lower()
    
    if resposta not in ['sim', 's', 'yes', 'y']:
        print("❌ Migração cancelada")
        sys.exit(0)
    
    # Executar DRY RUN primeiro
    print("\n🔍 EXECUTANDO DRY RUN...")
    print("=" * 80)
    recalcular_idtransacao_definitivo(dry_run=True)
    
    # Perguntar se quer aplicar de verdade
    print("\n" + "=" * 80)
    resposta2 = input("Deseja APLICAR as mudanças no banco? [sim/nao]: ").strip().lower()
    
    if resposta2 not in ['sim', 's', 'yes', 'y']:
        print("❌ Aplicação cancelada")
        sys.exit(0)
    
    # Executar migração real
    print("\n💾 EXECUTANDO MIGRAÇÃO REAL...")
    print("=" * 80)
    recalcular_idtransacao_definitivo(dry_run=False)
    
    print("\n✅ PROCESSO CONCLUÍDO!")
    print("   Reinicie os servidores para carregar o código atualizado:")
    print("   cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4")
    print("   ./quick_stop.sh && ./quick_start.sh")
