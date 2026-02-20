"""
Recalcula id_parcela incluindo user_id no hash
Usa SQL direto para evitar dependências
"""
import sqlite3
import hashlib
import re
from pathlib import Path

# Path do banco
DB_PATH = Path(__file__).parent.parent.parent / "app_dev" / "backend" / "database" / "financas_dev.db"


def normalizar_estabelecimento(texto: str) -> str:
    """Normaliza estabelecimento"""
    if not texto:
        return ""
    # Uppercase
    texto = texto.upper().strip()
    # Remove espaços múltiplos
    texto = re.sub(r'\s+', ' ', texto)
    return texto


def recalcular_id_parcela():
    """Recalcula id_parcela para incluir user_id no hash"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Buscar todas as parcelas
        cursor.execute("""
            SELECT id, estabelecimento_base, valor_parcela, qtd_parcelas, user_id, id_parcela
            FROM base_parcelas
            ORDER BY user_id, id
        """)
        
        parcelas = cursor.fetchall()
        
        print(f"📦 Encontradas {len(parcelas)} parcelas para recalcular")
        
        if not parcelas:
            print("⚠️  Nenhuma parcela encontrada")
            return
        
        # Recalcular cada parcela
        atualizadas = 0
        erros = 0
        
        for row in parcelas:
            id_row, estabelecimento_base, valor_parcela, qtd_parcelas, user_id, id_parcela_atual = row
            
            try:
                # Calcular novo id_parcela COM user_id
                estab_normalizado = normalizar_estabelecimento(estabelecimento_base)
                chave = f"{estab_normalizado}|{valor_parcela:.2f}|{qtd_parcelas}|{user_id}"
                novo_id = hashlib.md5(chave.encode()).hexdigest()[:16]
                
                # Atualizar se diferente
                if id_parcela_atual != novo_id:
                    print(f"  🔄 {estabelecimento_base[:40]:40} | user={user_id} | {id_parcela_atual} → {novo_id}")
                    
                    cursor.execute("""
                        UPDATE base_parcelas
                        SET id_parcela = ?
                        WHERE id = ?
                    """, (novo_id, id_row))
                    
                    atualizadas += 1
                
            except Exception as e:
                print(f"  ❌ Erro ao recalcular {id_row}: {e}")
                erros += 1
        
        # Commit
        if atualizadas > 0:
            conn.commit()
            print(f"\n✅ {atualizadas} parcelas atualizadas")
        else:
            print(f"\n✅ Todas as parcelas já estão corretas")
        
        if erros > 0:
            print(f"⚠️  {erros} erros encontrados")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 80)
    print("RECALCULAR ID_PARCELA COM USER_ID")
    print("=" * 80)
    
    recalcular_id_parcela()
    
    print("\n" + "=" * 80)
    print("✅ CONCLUÍDO")
    print("=" * 80)
