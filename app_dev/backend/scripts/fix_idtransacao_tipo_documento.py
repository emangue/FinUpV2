"""
Script para corrigir IdTransacao considerando tipo_documento corretamente

PROBLEMA:
- Código antigo: if tipo_documento == 'extrato'
- Arquivos Itaú: tipo_documento = 'Cartão de Crédito' (não 'extrato')
- Resultado: Lógica de fatura aplicada erradamente a extratos

SOLUÇÃO:
- Código novo: if 'extrato' in tipo_documento.lower() or 'conta' in tipo_documento.lower()
- Regenerar TODOS os IdTransacao com a lógica correta

Uso:
    python scripts/fix_idtransacao_tipo_documento.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.core.database import get_db, engine
from app.domains.transactions.models import JournalEntry
from app.shared.utils import generate_id_transacao, arredondar_2_decimais
import re
from collections import defaultdict

def extrair_estabelecimento_base(estabelecimento: str) -> str:
    """Remove parcela do estabelecimento"""
    # Formato com parênteses: "LOJA (3/12)"
    match = re.search(r'^(.+?)\s*\((\d{1,2})/(\d{1,2})\)\s*$', estabelecimento)
    if match:
        return match.group(1).strip()
    
    # Formato sem parênteses: "LOJA 3/12"
    match = re.search(r'^(.+?)\s*(\d{1,2})/(\d{1,2})\s*$', estabelecimento)
    if match:
        return match.group(1).strip()
    
    return estabelecimento


def regenerar_idtransacao():
    """
    Regenera IdTransacao de TODAS as transações com lógica corrigida
    """
    db = next(get_db())
    
    try:
        print("🔄 REGENERAÇÃO DE IdTransacao - Correção tipo_documento")
        print("=" * 70)
        print()
        
        # Buscar TODAS as transações
        transacoes = db.query(JournalEntry).order_by(
            JournalEntry.user_id,
            JournalEntry.arquivo_origem,
            JournalEntry.Data
        ).all()
        
        total = len(transacoes)
        print(f"📊 Total de transações: {total}")
        print()
        
        # Agrupar por user_id + arquivo_origem para controle de sequência
        grupos = defaultdict(lambda: defaultdict(int))
        modificadas = []
        
        for i, trans in enumerate(transacoes, 1):
            # 1. Detectar tipo de documento
            tipo_doc_lower = trans.tipodocumento.lower() if trans.tipodocumento else ''
            
            # 2. Extrair estabelecimento base
            estabelecimento_base = extrair_estabelecimento_base(trans.Estabelecimento)
            
            # 3. Determinar estratégia baseado em tipo_documento
            if 'extrato' in tipo_doc_lower or 'conta' in tipo_doc_lower:
                # Extrato/Conta: usa lancamento COMPLETO
                estab_para_hash = trans.Estabelecimento
                estrategia = "EXTRATO"
            else:
                # Fatura/Cartão: usa estabelecimento_base (sem parcela)
                estab_para_hash = estabelecimento_base
                estrategia = "FATURA/CARTÃO"
            
            # 4. Controle de sequência para duplicados no mesmo arquivo
            valor_arredondado = arredondar_2_decimais(abs(trans.Valor))
            chave_hash = estab_para_hash.upper().strip()
            chave_unica = f"{trans.Data}|{chave_hash}|{valor_arredondado:.2f}"
            chave_arquivo = f"{trans.user_id}_{trans.arquivo_origem}"
            
            # Incrementar sequência
            grupos[chave_arquivo][chave_unica] += 1
            sequencia = grupos[chave_arquivo][chave_unica]
            
            # 5. Gerar novo IdTransacao
            novo_id = generate_id_transacao(
                data=trans.Data,
                estabelecimento=estab_para_hash,
                valor=valor_arredondado,
                sequencia=sequencia
            )
            
            # 6. Verificar se mudou
            if trans.IdTransacao != novo_id:
                modificadas.append({
                    'id': trans.id,
                    'data': trans.Data,
                    'estabelecimento': trans.Estabelecimento,
                    'tipo_documento': trans.tipodocumento,
                    'estrategia': estrategia,
                    'estab_para_hash': estab_para_hash,
                    'sequencia': sequencia,
                    'id_antigo': trans.IdTransacao,
                    'id_novo': novo_id,
                    'trans': trans
                })
            
            if i % 500 == 0:
                print(f"  Progresso: {i}/{total} ({i*100//total}%)")
        
        print()
        print(f"📊 Análise completa:")
        print(f"   Total: {total}")
        print(f"   Modificadas: {len(modificadas)}")
        print(f"   Sem alteração: {total - len(modificadas)}")
        print()
        
        if not modificadas:
            print("✅ Todos os IdTransacao já estão corretos!")
            return
        
        # Mostrar exemplos de mudanças
        print("📋 Exemplos de mudanças (primeiros 10):")
        print("-" * 70)
        for m in modificadas[:10]:
            print(f"ID {m['id']}: {m['data']} | {m['estabelecimento'][:40]}")
            print(f"  Tipo: {m['tipo_documento']} → {m['estrategia']}")
            print(f"  Hash base: {m['estab_para_hash'][:40]} (seq={m['sequencia']})")
            print(f"  IdTransacao: {m['id_antigo']} → {m['id_novo']}")
            print()
        
        # Confirmar
        resposta = input(f"\n⚠️  Atualizar {len(modificadas)} transações? (s/N): ")
        
        if resposta.lower() != 's':
            print("❌ Operação cancelada")
            return
        
        # Atualizar
        print()
        print("💾 Atualizando transações...")
        
        for i, m in enumerate(modificadas, 1):
            m['trans'].IdTransacao = m['id_novo']
            
            if i % 100 == 0:
                db.commit()
                print(f"  Salvando: {i}/{len(modificadas)}")
        
        db.commit()
        
        print()
        print("✅ Regeneração concluída com sucesso!")
        print(f"   {len(modificadas)} IdTransacao atualizados")
        print()
        print("🔍 Próximos passos:")
        print("   1. Reinicie os servidores: ./quick_stop.sh && ./quick_start.sh")
        print("   2. Teste o upload novamente")
        print("   3. Verifique se duplicatas são detectadas corretamente")
        
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    regenerar_idtransacao()
