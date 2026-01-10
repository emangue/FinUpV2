#!/usr/bin/env python3
"""
MIGRAÇÃO DEFINITIVA - IdTransacao v3.0.0 (SQL Direto)

Evita problemas de imports usando SQL direto
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime
import shutil

# Adiciona o diretório raiz do backend ao path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.shared.utils.hasher import generate_id_transacao


def criar_backup(db_path: Path) -> Path:
    """Cria backup do banco de dados"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = db_path.parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    backup_path = backup_dir / f"{db_path.stem}_backup_v3_{timestamp}{db_path.suffix}"
    shutil.copy2(db_path, backup_path)
    
    print(f"✅ Backup criado: {backup_path.name}")
    return backup_path


def recalcular_idtransacao(dry_run: bool = True):
    """Recalcula TODOS os IdTransacao"""
    
    db_path = backend_dir / "database" / "financas_dev.db"
    
    if not db_path.exists():
        print(f"❌ Banco não encontrado: {db_path}")
        return
    
    print(f"📂 Banco: {db_path.name}")
    print(f"🔍 Modo: {'DRY RUN' if dry_run else 'EXECUÇÃO REAL'}")
    print()
    
    # Backup
    if not dry_run:
        criar_backup(db_path)
        print()
    
    # Conectar
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Buscar transações ordenadas
        print("📥 Carregando transações...")
        cursor.execute("""
            SELECT id, Data, Estabelecimento, Valor, IdTransacao
            FROM journal_entries
            ORDER BY Data, Estabelecimento, Valor, id
        """)
        
        transacoes = cursor.fetchall()
        print(f"   Total: {len(transacoes)} transações\n")
        
        # Processar
        duplicatas_map = {}
        modificadas = 0
        mantidas = 0
        duplicatas_numeradas = 0
        updates = []
        
        print("🔄 Processando...")
        print("=" * 80)
        
        for i, (tid, data, estabelecimento, valor, id_atual) in enumerate(transacoes, 1):
            # Chave única
            estab_upper = str(estabelecimento).upper().strip()
            chave = f"{data}|{estab_upper}|{valor:.2f}"
            
            # Sequência
            if chave not in duplicatas_map:
                duplicatas_map[chave] = 1
            else:
                duplicatas_map[chave] += 1
            
            seq = duplicatas_map[chave]
            
            # Gerar novo ID
            novo_id = generate_id_transacao(data, estabelecimento, valor, seq)
            
            # Comparar
            if novo_id != id_atual:
                modificadas += 1
                
                if modificadas <= 15:
                    seq_label = f" [Seq {seq}]" if seq > 1 else ""
                    print(f"ID {tid}: {data} | {estabelecimento[:35]}{seq_label}")
                    print(f"   ❌ {id_atual}")
                    print(f"   ✅ {novo_id}")
                    print()
                
                if seq > 1:
                    duplicatas_numeradas += 1
                
                updates.append((novo_id, tid))
            else:
                mantidas += 1
            
            if i % 500 == 0:
                print(f"   {i}/{len(transacoes)} processadas...")
        
        print("=" * 80)
        print()
        print("📊 RESUMO:")
        print(f"   Total: {len(transacoes)}")
        print(f"   ✅ Modificadas: {modificadas}")
        print(f"   ➡️  Mantidas: {mantidas}")
        print(f"   🔢 Duplicatas numeradas: {duplicatas_numeradas}")
        print()
        
        # Aplicar updates
        if not dry_run and updates:
            print(f"💾 Atualizando {len(updates)} registros...")
            cursor.executemany(
                "UPDATE journal_entries SET IdTransacao = ? WHERE id = ?",
                updates
            )
            conn.commit()
            print("✅ Migração concluída!")
            
            # Verificar duplicatas
            print()
            print("🔍 Verificando duplicatas...")
            cursor.execute("""
                SELECT IdTransacao, COUNT(*) as count
                FROM journal_entries
                GROUP BY IdTransacao
                HAVING COUNT(*) > 1
            """)
            
            duplicatas = cursor.fetchall()
            if duplicatas:
                print(f"⚠️  {len(duplicatas)} duplicatas encontradas:")
                for id_trans, count in duplicatas[:5]:
                    print(f"   {id_trans}: {count}x")
            else:
                print("   ✅ Nenhuma duplicata!")
        else:
            print("ℹ️  DRY RUN - nada foi salvo")
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 80)
    print("MIGRAÇÃO DEFINITIVA - IdTransacao v3.0.0")
    print("=" * 80)
    print()
    
    resposta = input("Executar migração? [sim/nao]: ").strip().lower()
    if resposta not in ['sim', 's']:
        print("❌ Cancelado")
        sys.exit(0)
    
    print("\n🔍 DRY RUN...\n")
    recalcular_idtransacao(dry_run=True)
    
    print("\n" + "=" * 80)
    resposta2 = input("APLICAR mudanças? [sim/nao]: ").strip().lower()
    if resposta2 not in ['sim', 's']:
        print("❌ Cancelado")
        sys.exit(0)
    
    print("\n💾 APLICANDO...\n")
    recalcular_idtransacao(dry_run=False)
    
    print("\n✅ CONCLUÍDO!")
    print("   Reinicie: ./quick_stop.sh && ./quick_start.sh")
