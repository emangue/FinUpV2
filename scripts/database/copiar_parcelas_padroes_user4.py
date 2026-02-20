"""
Copia base_parcelas e base_padroes do user 1 para user 4
Recalcula id_parcela com user_id=4 no hash
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
    texto = texto.upper().strip()
    texto = re.sub(r'\s+', ' ', texto)
    return texto


def copiar_parcelas():
    """Copia parcelas do user 1 para user 4 com id_parcela recalculado"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Buscar parcelas do user 1
        cursor.execute("""
            SELECT estabelecimento_base, valor_parcela, qtd_parcelas, 
                   grupo_sugerido, subgrupo_sugerido, tipo_gasto_sugerido,
                   qtd_pagas, valor_total_plano, data_inicio, status, categoria_geral_sugerida
            FROM base_parcelas
            WHERE user_id = 1
        """)
        
        parcelas = cursor.fetchall()
        print(f"📦 Copiando {len(parcelas)} parcelas do user 1 para user 4...")
        
        copiadas = 0
        for row in parcelas:
            (estabelecimento_base, valor_parcela, qtd_parcelas, grupo_sugerido, 
             subgrupo_sugerido, tipo_gasto_sugerido, qtd_pagas, valor_total_plano, 
             data_inicio, status, categoria_geral_sugerida) = row
            
            # Calcular id_parcela para user 4 COM user_id
            estab_normalizado = normalizar_estabelecimento(estabelecimento_base)
            chave = f"{estab_normalizado}|{valor_parcela:.2f}|{qtd_parcelas}|4"  # user_id = 4
            id_parcela = hashlib.md5(chave.encode()).hexdigest()[:16]
            
            # Inserir
            cursor.execute("""
                INSERT INTO base_parcelas (
                    id_parcela, estabelecimento_base, valor_parcela, qtd_parcelas,
                    grupo_sugerido, subgrupo_sugerido, tipo_gasto_sugerido,
                    qtd_pagas, valor_total_plano, data_inicio, status, user_id, categoria_geral_sugerida
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 4, ?)
            """, (id_parcela, estabelecimento_base, valor_parcela, qtd_parcelas,
                  grupo_sugerido, subgrupo_sugerido, tipo_gasto_sugerido,
                  qtd_pagas, valor_total_plano, data_inicio, status, categoria_geral_sugerida))
            
            copiadas += 1
        
        conn.commit()
        print(f"✅ {copiadas} parcelas copiadas para user 4")
        
    except Exception as e:
        print(f"❌ Erro ao copiar parcelas: {e}")
        conn.rollback()
    finally:
        conn.close()


def copiar_padroes():
    """Copia padrões do user 1 para user 4"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Buscar padrões do user 1
        cursor.execute("""
            SELECT padrao_estabelecimento, contagem, valor_medio, valor_min, valor_max,
                   desvio_padrao, coef_variacao, percentual_consistencia, confianca,
                   grupo_sugerido, subgrupo_sugerido, tipo_gasto_sugerido,
                   faixa_valor, segmentado, exemplos, status, categoria_geral_sugerida
            FROM base_padroes
            WHERE user_id = 1
        """)
        
        padroes = cursor.fetchall()
        print(f"📦 Copiando {len(padroes)} padrões do user 1 para user 4...")
        
        copiados = 0
        for i, row in enumerate(padroes, 1):
            (padrao_estabelecimento, contagem, valor_medio, valor_min, valor_max,
             desvio_padrao, coef_variacao, percentual_consistencia, confianca,
             grupo_sugerido, subgrupo_sugerido, tipo_gasto_sugerido,
             faixa_valor, segmentado, exemplos, status, categoria_geral_sugerida) = row
            
            # Gerar padrao_num único para user 4
            padrao_num = f"u4_{i:05d}"
            
            # Inserir
            cursor.execute("""
                INSERT INTO base_padroes (
                    user_id, padrao_estabelecimento, padrao_num, contagem,
                    valor_medio, valor_min, valor_max, desvio_padrao, coef_variacao,
                    percentual_consistencia, confianca, grupo_sugerido, subgrupo_sugerido,
                    tipo_gasto_sugerido, faixa_valor, segmentado, exemplos, status,
                    categoria_geral_sugerida
                )
                VALUES (4, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (padrao_estabelecimento, padrao_num, contagem, valor_medio, valor_min, valor_max,
                  desvio_padrao, coef_variacao, percentual_consistencia, confianca,
                  grupo_sugerido, subgrupo_sugerido, tipo_gasto_sugerido,
                  faixa_valor, segmentado, exemplos, status, categoria_geral_sugerida))
            
            copiados += 1
        
        conn.commit()
        print(f"✅ {copiados} padrões copiados para user 4")
        
    except Exception as e:
        print(f"❌ Erro ao copiar padrões: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 80)
    print("COPIAR PARCELAS E PADRÕES - USER 1 → USER 4")
    print("=" * 80)
    
    copiar_parcelas()
    print()
    copiar_padroes()
    
    print("\n" + "=" * 80)
    print("✅ CONCLUÍDO")
    print("=" * 80)
