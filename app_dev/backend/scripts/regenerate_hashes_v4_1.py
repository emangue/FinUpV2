#!/usr/bin/env python3
"""
Script para regenerar TODOS os IdTransacao com hash recursivo v4.1.0

ESTRATÉGIA:
1. Agrupa transações por (Data, Estabelecimento, Valor)
2. Ordena cada grupo por id (ordem de inserção)
3. Aplica sequência: 1ª = seq=1, 2ª = seq=2, etc
4. Gera hash recursivo v4.1.0
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.domains.transactions.models import JournalEntry
from app.domains.upload.history_models import UploadHistory  # Import necessário para relationship
from collections import defaultdict

# Hash FNV-1a
def fnv1a_64_hash(text: str) -> str:
    FNV_OFFSET_64 = 0xcbf29ce484222325
    FNV_PRIME_64 = 0x100000001b3
    MASK64 = (1 << 64) - 1
    h = FNV_OFFSET_64
    for char in text:
        h ^= ord(char)
        h = (h * FNV_PRIME_64) & MASK64
    return str(h)

# Hash recursivo v4.1.0
def generate_hash_v4_1(data: str, estabelecimento: str, valor: float, sequencia: int) -> str:
    """
    Gera hash v4.1.0 com recursão para duplicados
    
    seq=1: hash(data|estab|valor)
    seq=2: hash(hash_seq1)
    seq=N: hash aplicado N-1 vezes
    """
    estab_upper = estabelecimento.upper().strip()
    valor_abs = abs(valor)
    chave = f"{data}|{estab_upper}|{valor_abs:.2f}"
    
    # Hash base
    hash_atual = fnv1a_64_hash(chave)
    
    # Aplicar hash recursivo (seq-1) vezes
    for _ in range(sequencia - 1):
        hash_atual = fnv1a_64_hash(hash_atual)
    
    return hash_atual

def main():
    # Conectar ao banco
    engine = create_engine(f"sqlite:///{settings.DATABASE_PATH}")
    Session = sessionmaker(bind=engine)
    db = Session()
    
    print("=" * 80)
    print("REGENERAÇÃO DE HASHES v4.1.0 (Hash Recursivo)")
    print("=" * 80)
    print()
    
    # 1. Buscar TODAS as transações
    print("📊 Carregando transações...")
    transactions = db.query(JournalEntry).order_by(JournalEntry.id).all()
    total = len(transactions)
    print(f"   Total: {total} transações")
    print()
    
    # 2. Agrupar por (Data, Estabelecimento, Valor)
    print("🔍 Agrupando duplicados...")
    grupos = defaultdict(list)
    
    for t in transactions:
        # Chave única: data|estabelecimento_upper|valor
        estab_upper = t.Estabelecimento.upper().strip()
        valor_abs = abs(t.Valor)
        chave = f"{t.Data}|{estab_upper}|{valor_abs:.2f}"
        grupos[chave].append(t)
    
    print(f"   {len(grupos)} chaves únicas")
    print(f"   {sum(1 for g in grupos.values() if len(g) > 1)} grupos com duplicados")
    print()
    
    # 3. Calcular novos hashes
    print("🔄 Calculando novos hashes...")
    mudancas = []
    
    for chave, grupo in grupos.items():
        # Ordenar por id (ordem de inserção original)
        grupo_ordenado = sorted(grupo, key=lambda x: x.id)
        
        for seq, transacao in enumerate(grupo_ordenado, start=1):
            # Gerar novo hash v4.1.0
            novo_hash = generate_hash_v4_1(
                data=transacao.Data,
                estabelecimento=transacao.Estabelecimento,
                valor=transacao.Valor,
                sequencia=seq
            )
            
            # Verificar se mudou
            if transacao.IdTransacao != novo_hash:
                mudancas.append({
                    'id': transacao.id,
                    'data': transacao.Data,
                    'estabelecimento': transacao.Estabelecimento,
                    'valor': transacao.Valor,
                    'seq': seq,
                    'hash_antigo': transacao.IdTransacao,
                    'hash_novo': novo_hash,
                    'transacao': transacao
                })
    
    print(f"   {len(mudancas)} transações precisam ser atualizadas ({len(mudancas)/total*100:.1f}%)")
    print()
    
    # 4. Mostrar exemplos
    if mudancas:
        print("📋 Exemplos de mudanças:")
        for m in mudancas[:5]:
            print(f"   ID {m['id']}: {m['data']} | {m['estabelecimento'][:40]} | {m['valor']:.2f}")
            print(f"      Antigo: {m['hash_antigo']}")
            print(f"      Novo:   {m['hash_novo']} (seq={m['seq']})")
            print()
    
    # 5. Confirmar
    if not mudancas:
        print("✅ Todos os hashes já estão corretos!")
        return
    
    print("⚠️  ATENÇÃO: Esta operação irá MODIFICAR o banco de dados!")
    resposta = input("Deseja continuar? (SIM para confirmar): ")
    
    if resposta != "SIM":
        print("❌ Operação cancelada")
        return
    
    # 6. Aplicar mudanças
    print()
    print("💾 Aplicando mudanças...")
    
    try:
        for i, m in enumerate(mudancas, 1):
            m['transacao'].IdTransacao = m['hash_novo']
            
            if i % 100 == 0:
                print(f"   Processando {i}/{len(mudancas)}...")
        
        db.commit()
        print()
        print(f"✅ {len(mudancas)} transações atualizadas com sucesso!")
        print()
        print("🎯 Sistema agora usa hash recursivo v4.1.0")
        print("   - Preview e Journal usam a MESMA lógica")
        print("   - Duplicados serão detectados corretamente")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao aplicar mudanças: {e}")
        raise
    
    finally:
        db.close()

if __name__ == "__main__":
    main()
