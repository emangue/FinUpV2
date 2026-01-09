"""
Script de Migração: bank_format_compatibility
De: 4 linhas por banco (1 por formato)
Para: 1 linha por banco (colunas por formato)

SEGURANÇA:
- Cria backup automático antes de migrar
- Valida dados após migração
- Rollback automático se falhar
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_compatibility():
    """
    Migra estrutura da tabela bank_format_compatibility
    
    ANTES (28 linhas - 4 por banco):
    id | bank_name | file_format | status
    1  | Itaú      | CSV         | OK
    2  | Itaú      | Excel       | OK
    3  | Itaú      | PDF         | TBD
    4  | Itaú      | OFX         | TBD
    
    DEPOIS (7 linhas - 1 por banco):
    id | bank_name | csv_status | excel_status | pdf_status | ofx_status
    1  | Itaú      | OK         | OK           | TBD        | TBD
    """
    
    engine = create_engine(str(settings.DATABASE_URL))
    
    with engine.begin() as conn:
        logger.info("🔍 Verificando estrutura atual...")
        
        # Verificar se já está migrado
        check_columns = text("""
            SELECT COUNT(*) as count 
            FROM pragma_table_info('bank_format_compatibility') 
            WHERE name IN ('csv_status', 'excel_status', 'pdf_status', 'ofx_status')
        """)
        result = conn.execute(check_columns).fetchone()
        
        if result.count == 4:
            logger.warning("⚠️  Tabela já está no formato matricial. Nada a fazer.")
            return
        
        logger.info("📦 Criando backup da tabela antiga...")
        
        # Criar backup com timestamp
        backup_name = f"bank_format_compatibility_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        conn.execute(text(f"""
            CREATE TABLE {backup_name} AS 
            SELECT * FROM bank_format_compatibility
        """))
        
        backup_count = conn.execute(text(f"SELECT COUNT(*) as count FROM {backup_name}")).fetchone()
        logger.info(f"✅ Backup criado: {backup_name} ({backup_count.count} registros)")
        
        logger.info("🔄 Coletando dados antigos...")
        
        # Buscar todos os dados agrupados por banco
        old_data = conn.execute(text("""
            SELECT 
                bank_name,
                MAX(CASE WHEN file_format = 'CSV' THEN status ELSE 'TBD' END) as csv_status,
                MAX(CASE WHEN file_format = 'Excel' THEN status ELSE 'TBD' END) as excel_status,
                MAX(CASE WHEN file_format = 'PDF' THEN status ELSE 'TBD' END) as pdf_status,
                MAX(CASE WHEN file_format = 'OFX' THEN status ELSE 'TBD' END) as ofx_status,
                MIN(created_at) as created_at,
                MAX(updated_at) as updated_at
            FROM bank_format_compatibility
            GROUP BY bank_name
            ORDER BY bank_name
        """)).fetchall()
        
        logger.info(f"📊 {len(old_data)} bancos encontrados")
        
        logger.info("🗑️  Removendo tabela antiga...")
        conn.execute(text("DROP TABLE bank_format_compatibility"))
        
        logger.info("🏗️  Criando nova estrutura...")
        conn.execute(text("""
            CREATE TABLE bank_format_compatibility (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bank_name VARCHAR NOT NULL UNIQUE,
                csv_status VARCHAR NOT NULL DEFAULT 'TBD',
                excel_status VARCHAR NOT NULL DEFAULT 'TBD',
                pdf_status VARCHAR NOT NULL DEFAULT 'TBD',
                ofx_status VARCHAR NOT NULL DEFAULT 'TBD',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        logger.info("📥 Migrando dados...")
        
        for row in old_data:
            conn.execute(text("""
                INSERT INTO bank_format_compatibility 
                (bank_name, csv_status, excel_status, pdf_status, ofx_status, created_at, updated_at)
                VALUES (:bank_name, :csv_status, :excel_status, :pdf_status, :ofx_status, :created_at, :updated_at)
            """), {
                'bank_name': row.bank_name,
                'csv_status': row.csv_status,
                'excel_status': row.excel_status,
                'pdf_status': row.pdf_status,
                'ofx_status': row.ofx_status,
                'created_at': row.created_at,
                'updated_at': row.updated_at
            })
        
        logger.info("✅ Validando migração...")
        
        new_count = conn.execute(text("SELECT COUNT(*) as count FROM bank_format_compatibility")).fetchone()
        logger.info(f"📊 {new_count.count} bancos migrados (esperado: {len(old_data)})")
        
        if new_count.count != len(old_data):
            logger.error("❌ Contagem não bate! Fazendo rollback...")
            raise Exception("Migração falhou - contagem incorreta")
        
        # Validar alguns dados
        sample = conn.execute(text("""
            SELECT bank_name, csv_status, excel_status, pdf_status, ofx_status 
            FROM bank_format_compatibility 
            LIMIT 3
        """)).fetchall()
        
        logger.info("📋 Amostra dos dados migrados:")
        for row in sample:
            logger.info(f"  {row.bank_name}: CSV={row.csv_status}, Excel={row.excel_status}, PDF={row.pdf_status}, OFX={row.ofx_status}")
        
        logger.info(f"✅ Migração concluída com sucesso!")
        logger.info(f"💾 Backup mantido em: {backup_name}")

if __name__ == "__main__":
    try:
        migrate_compatibility()
    except Exception as e:
        logger.error(f"❌ Erro na migração: {e}")
        logger.error("🔄 Rollback automático foi executado pela transação")
        sys.exit(1)
