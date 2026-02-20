"""
Recalcula id_parcela incluindo user_id no hash
Necessário após mudança para isolar parcelas por usuário
"""
import sys
import hashlib
import re
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Path do banco
DB_PATH = Path(__file__).parent.parent.parent / "app_dev" / "backend" / "database" / "financas_dev.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Criar engine e session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Adicionar backend ao path
backend_path = Path(__file__).parent.parent.parent / "app_dev" / "backend"
sys.path.insert(0, str(backend_path))

from app.domains.transactions.models import BaseParcelas


def normalizar_estabelecimento(texto: str) -> str:
    """Normaliza estabelecimento (cópia da função em utils)"""
    if not texto:
        return ""
    # Uppercase
    texto = texto.upper().strip()
    # Remove espaços múltiplos
    texto = re.sub(r'\s+', ' ', texto)
    return texto


def recalcular_id_parcela(user_id: int = None):
    """
    Recalcula id_parcela para incluir user_id no hash
    
    Args:
        user_id: Se especificado, recalcula apenas para esse usuário
    """
    db = SessionLocal()
    
    try:
        # Buscar parcelas
        query = db.query(BaseParcelas)
        if user_id:
            query = query.filter(BaseParcelas.user_id == user_id)
        
        parcelas = query.all()
        
        print(f"📦 Encontradas {len(parcelas)} parcelas para recalcular")
        
        if not parcelas:
            print("⚠️  Nenhuma parcela encontrada")
            return
        
        # Recalcular cada parcela
        atualizadas = 0
        erros = 0
        
        for parcela in parcelas:
            try:
                # Calcular novo id_parcela com user_id
                estab_normalizado = normalizar_estabelecimento(parcela.estabelecimento_base)
                chave = f"{estab_normalizado}|{parcela.valor_parcela:.2f}|{parcela.qtd_parcelas}|{parcela.user_id}"
                novo_id = hashlib.md5(chave.encode()).hexdigest()[:16]
                
                # Atualizar se diferente
                if parcela.id_parcela != novo_id:
                    print(f"  🔄 {parcela.estabelecimento_base[:40]:40} | user={parcela.user_id} | {parcela.id_parcela} → {novo_id}")
                    parcela.id_parcela = novo_id
                    atualizadas += 1
                
            except Exception as e:
                print(f"  ❌ Erro ao recalcular {parcela.id}: {e}")
                erros += 1
        
        # Commit
        if atualizadas > 0:
            db.commit()
            print(f"\n✅ {atualizadas} parcelas atualizadas")
        else:
            print(f"\n✅ Todas as parcelas já estão corretas")
        
        if erros > 0:
            print(f"⚠️  {erros} erros encontrados")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 80)
    print("RECALCULAR ID_PARCELA COM USER_ID")
    print("=" * 80)
    
    # Recalcular para todos os usuários
    recalcular_id_parcela()
    
    print("\n" + "=" * 80)
    print("✅ CONCLUÍDO")
    print("=" * 80)
