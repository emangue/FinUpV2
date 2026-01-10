#!/usr/bin/env python3
"""
Regenera TODOS os IdTransacao do journal_entries com nova lógica v4.0.0

MUDANÇA CRÍTICA:
- Antes: Hash usava estabelecimento_base (sem parcela) + sequência
- Agora: Hash usa lancamento ORIGINAL (com parcela, datas, tudo)
- Elimina conceito de sequência completamente
- Transações diferentes = hashes diferentes

IMPORTANTE: Faz backup automático antes de modificar!
"""

import sys
import os
from pathlib import Path

# Adiciona app ao path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.core.database import engine, Base
from app.domains.transactions.models import JournalEntry
from app.shared.utils.hasher import generate_id_transacao
from app.shared.utils import arredondar_2_decimais
import shutil
from datetime import datetime

def fazer_backup_database():
    """Faz backup do database antes de modificar"""
    db_path = backend_dir / "database" / "financas_dev.db"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backend_dir / "database" / f"financas_dev_backup_{timestamp}.db"
    
    print(f"📦 Fazendo backup: {backup_path.name}")
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup criado com sucesso!")
    
    return backup_path

def regenerar_id_transacao():
    """Regenera IdTransacao para TODAS as transações"""
    
    print("="*60)
    print("🔄 REGENERAÇÃO DE IdTransacao - v4.0.0")
    print("="*60)
    print()
    
    # 1. Backup
    backup_path = fazer_backup_database()
    print()
    
    # 2. Conectar ao banco
    session = Session(engine)
    
    try:
        # 3. Buscar TODAS as transações
        print("📊 Carregando transações do journal_entries...")
        transacoes = session.query(JournalEntry).all()
        total = len(transacoes)
        
        print(f"✅ {total} transações encontradas")
        print()
        
        # 4. Confirmar ação
        print("⚠️  ATENÇÃO: Esta operação irá MODIFICAR todos os IdTransacao!")
        print(f"   Backup salvo em: {backup_path.name}")
        resposta = input("\n🔹 Continuar? (digite 'SIM' para confirmar): ")
        
        if resposta.strip().upper() != "SIM":
            print("❌ Operação cancelada pelo usuário")
            return
        
        print()
        print("🔄 Regenerando IdTransacao...")
        print("-" * 60)
        
        # 5. Regenerar cada IdTransacao
        modificados = 0
        erros = 0
        amostras = []  # Guardar primeiras 5 mudanças
        
        for i, trans in enumerate(transacoes, 1):
            try:
                # ID antigo
                id_antigo = trans.IdTransacao
                
                # Valor arredondado (mesmo que marker.py)
                valor_arredondado = arredondar_2_decimais(abs(trans.Valor))
                
                # NOVO ID - usa Estabelecimento ORIGINAL (não normalizado)
                # v4.0.0: Hash direto sem sequência
                id_novo = generate_id_transacao(
                    data=trans.Data,
                    estabelecimento=trans.Estabelecimento,  # ORIGINAL
                    valor=valor_arredondado
                )
                
                # Atualizar se diferente
                if id_antigo != id_novo:
                    trans.IdTransacao = id_novo
                    modificados += 1
                    
                    # Guardar amostra das primeiras 5 mudanças
                    if len(amostras) < 5:
                        amostras.append({
                            'data': trans.Data,
                            'estab': trans.Estabelecimento[:40],
                            'valor': trans.Valor,
                            'antigo': id_antigo,
                            'novo': id_novo
                        })
                
                # Progress
                if i % 500 == 0 or i == total:
                    print(f"  Processadas: {i}/{total} ({(i/total)*100:.1f}%)")
            
            except Exception as e:
                erros += 1
                print(f"❌ Erro na transação {trans.id}: {e}")
        
        print()
        print("="*60)
        print("📊 RESUMO DA REGENERAÇÃO")
        print("="*60)
        print(f"Total processadas: {total}")
        print(f"Modificadas:       {modificados}")
        print(f"Sem mudança:       {total - modificados}")
        print(f"Erros:             {erros}")
        print()
        
        # Mostrar amostras
        if amostras:
            print("🔍 AMOSTRAS DE MUDANÇAS:")
            print("-" * 60)
            for amostra in amostras:
                print(f"\n📍 {amostra['data']} | {amostra['estab']} | R$ {amostra['valor']:.2f}")
                print(f"   Antigo: {amostra['antigo']}")
                print(f"   Novo:   {amostra['novo']}")
        
        print()
        print("-" * 60)
        
        # 6. Confirmar commit
        if modificados > 0:
            resposta = input(f"\n🔹 Confirmar alteração de {modificados} transações? (SIM/não): ")
            
            if resposta.strip().upper() == "SIM":
                session.commit()
                print()
                print("✅ Alterações commitadas com sucesso!")
                print(f"   {modificados} IdTransacao atualizados")
                print()
                print("📋 Próximos passos:")
                print("   1. Reiniciar servidores: ./quick_stop.sh && ./quick_start.sh")
                print("   2. Fazer novo upload para testar")
                print("   3. Validar com: ./validar_upload.sh")
            else:
                session.rollback()
                print("❌ Alterações descartadas (rollback)")
        else:
            print("ℹ️  Nenhuma modificação necessária")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ ERRO: {e}")
        print(f"   Banco não foi modificado")
        print(f"   Backup disponível em: {backup_path.name}")
    
    finally:
        session.close()
        print()
        print("🏁 Script finalizado")


if __name__ == "__main__":
    regenerar_id_transacao()
