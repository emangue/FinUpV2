#!/usr/bin/env python3
"""
Script de Migração: Recalcula IdTransacao de todas as transações
usando o algoritmo atual de hash (FNV-1a 64-bit)

Objetivo: Garantir consistência entre dados históricos e novos uploads
para que a deduplicação funcione corretamente.

IMPORTANTE: Faz backup automático antes de modificar
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import shutil

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.shared.utils import generate_id_transacao, normalizar
from app.core.config import settings


def backup_database():
    """Cria backup do banco antes de modificar"""
    db_path = Path(settings.DATABASE_PATH)
    backup_dir = db_path.parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"financas_dev_backup_{timestamp}.db"
    
    print(f"📦 Criando backup: {backup_path}")
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup criado com sucesso!\n")
    
    return backup_path


def recalcular_idtransacao(dry_run=True):
    """
    Recalcula IdTransacao de todas as transações em journal_entries
    Detecta duplicatas (mesma data + estabelecimento + valor) e adiciona sequência
    
    Args:
        dry_run: Se True, apenas simula sem modificar banco
    """
    # Criar engine e session
    engine = create_engine(f"sqlite:///{settings.DATABASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Buscar todas as transações usando SQL direto, ordenadas para consistência
        result = session.execute(text("""
            SELECT id, Data, Estabelecimento, Valor, IdTransacao 
            FROM journal_entries
            ORDER BY Data, Estabelecimento, Valor, id
        """))
        
        transacoes = result.fetchall()
        
        print(f"📊 Total de transações: {len(transacoes)}")
        print(f"🔧 Modo: {'DRY RUN (simulação)' if dry_run else 'PRODUÇÃO (vai modificar banco)'}\n")
        
        modificadas = 0
        mantidas = 0
        erros = 0
        duplicatas_numeradas = 0
        
        # Contador de ocorrências: (data, estabelecimento_norm, valor) -> sequência
        ocorrencias = {}
        hash_map = {}
        updates = []
        
        for i, row in enumerate(transacoes, 1):
            trans_id, data, estabelecimento, valor, antigo_id = row
            
            try:
                # Normalizar estabelecimento para chave
                estab_norm = normalizar(estabelecimento)
                chave_duplicata = (data, estab_norm, f"{float(valor):.2f}")
                
                # Incrementar contador para esta combinação
                if chave_duplicata not in ocorrencias:
                    ocorrencias[chave_duplicata] = 1
                else:
                    ocorrencias[chave_duplicata] += 1
                
                sequencia = ocorrencias[chave_duplicata]
                
                # Calcular novo IdTransacao com sequência
                novo_id = generate_id_transacao(data, estabelecimento, valor, sequencia=sequencia)
                
                if novo_id != antigo_id:
                    modificadas += 1
                    
                    if sequencia > 1:
                        duplicatas_numeradas += 1
                    
                    if modificadas <= 15:  # Mostrar apenas primeiras 15
                        seq_label = f" [seq={sequencia}]" if sequencia > 1 else ""
                        print(f"  [{i}/{len(transacoes)}] {data} - {estabelecimento}{seq_label}")
                        print(f"    Antigo: {antigo_id}")
                        print(f"    Novo:   {novo_id}")
                    
                    # Verificar conflito (novo hash já existe em outro registro)
                    if novo_id in hash_map and hash_map[novo_id] != trans_id:
                        print(f"    ⚠️ CONFLITO: Novo hash já existe em transação ID {hash_map[novo_id]}")
                    
                    hash_map[novo_id] = trans_id
                    updates.append((novo_id, trans_id))
                else:
                    mantidas += 1
                    hash_map[novo_id] = trans_id
                
            except Exception as e:
                erros += 1
                print(f"  ❌ Erro ao processar transação ID {trans_id}: {e}")
        
        # Executar updates se não for dry_run
        if not dry_run and updates:
            print(f"\n💾 Salvando {len(updates)} alterações no banco...")
            
            for novo_id, trans_id in updates:
                session.execute(
                    text("UPDATE journal_entries SET IdTransacao = :novo_id WHERE id = :trans_id"),
                    {"novo_id": novo_id, "trans_id": trans_id}
                )
            
            session.commit()
            print(f"✅ Commit realizado com sucesso!")
        else:
            print(f"\n⚠️ DRY RUN - Nenhuma alteração foi salva no banco")
        
        # Resumo
        print(f"\n📊 RESUMO:")
        print(f"   Total processadas: {len(transacoes)}")
        print(f"   ✅ Modificadas: {modificadas}")
        print(f"   ➡️  Mantidas: {mantidas}")
        print(f"   🔢 Duplicatas numeradas: {duplicatas_numeradas}")
        print(f"   ❌ Erros: {erros}")
        
        # Verificar duplicatas após recálculo
        print(f"\n🔍 Verificando duplicatas após recálculo...")
        duplicatas = {}
        for id_trans, trans_id in hash_map.items():
            if id_trans in duplicatas:
                duplicatas[id_trans].append(trans_id)
            else:
                duplicatas[id_trans] = [trans_id]
        
        conflitos = {k: v for k, v in duplicatas.items() if len(v) > 1}
        
        if conflitos:
            print(f"   ⚠️ {len(conflitos)} IdTransacao duplicados encontrados:")
            for hash_id, trans_ids in list(conflitos.items())[:5]:  # Mostrar apenas 5
                print(f"      {hash_id}: transações {trans_ids}")
        else:
            print(f"   ✅ Nenhuma duplicata encontrada!")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ ERRO FATAL: {e}")
        raise
    finally:
        session.close()


def main():
    print("=" * 70)
    print("🔧 SCRIPT DE MIGRAÇÃO: Recalcular IdTransacao")
    print("=" * 70)
    print()
    
    # Verificar se banco existe
    if not Path(settings.DATABASE_PATH).exists():
        print(f"❌ Banco não encontrado: {settings.DATABASE_PATH}")
        return
    
    # Criar backup
    backup_path = backup_database()
    
    # DRY RUN primeiro
    print("=" * 70)
    print("🧪 PASSO 1: DRY RUN (Simulação)")
    print("=" * 70)
    print()
    
    recalcular_idtransacao(dry_run=True)
    
    # Perguntar confirmação
    print("\n" + "=" * 70)
    resposta = input("\n⚠️  Deseja executar a migração REAL? (sim/não): ").strip().lower()
    
    if resposta in ['sim', 's', 'yes', 'y']:
        print("\n" + "=" * 70)
        print("🚀 PASSO 2: EXECUÇÃO REAL")
        print("=" * 70)
        print()
        
        recalcular_idtransacao(dry_run=False)
        
        print("\n" + "=" * 70)
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"📦 Backup salvo em: {backup_path}")
        print("=" * 70)
    else:
        print("\n❌ Migração cancelada pelo usuário")
        print(f"📦 Backup mantido em: {backup_path}")


if __name__ == "__main__":
    main()
