#!/usr/bin/env python3
"""
Migration: Criar tabela error_codes e popular com códigos padrão

Cria sistema de códigos de erro estruturados para melhor debugging e UX

Run: python scripts/migrate_create_error_codes.py
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# Caminho do banco de dados
DB_PATH = Path(__file__).parent.parent / "app_dev" / "backend" / "database" / "financas_dev.db"

def criar_tabela_e_popular():
    """Cria tabela error_codes e popula com códigos iniciais"""
    
    print(f"🔍 Conectando ao banco: {DB_PATH}")
    
    if not DB_PATH.exists():
        print(f"❌ Erro: Banco de dados não encontrado em {DB_PATH}")
        sys.exit(1)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se tabela já existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='error_codes'
        """)
        
        if cursor.fetchone():
            print("⚠️  Tabela 'error_codes' já existe")
            resposta = input("Deseja recriar a tabela? (s/N): ").lower()
            if resposta != 's':
                print("❌ Operação cancelada")
                conn.close()
                return
            
            # Drop tabela existente
            cursor.execute("DROP TABLE error_codes")
            print("🗑️  Tabela existente removida")
        
        # Criar tabela
        cursor.execute("""
            CREATE TABLE error_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                message_pt TEXT NOT NULL,
                technical_details TEXT,
                suggested_action TEXT,
                severity TEXT DEFAULT 'error',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        print("✅ Tabela 'error_codes' criada com sucesso")
        
        # Popular com códigos iniciais
        error_codes = [
            # PREVIEW ERRORS (PREV_*)
            ('PREV_001', 'preview', 'Sessão de preview não encontrada', 
             'O session_id fornecido não existe na tabela preview_transacoes', 
             'Verifique se o arquivo foi processado corretamente ou faça novo upload', 'error'),
            
            ('PREV_002', 'preview', 'Erro ao acessar banco de dados do preview', 
             'Falha ao conectar ou consultar preview_transacoes no banco backend', 
             'Verifique se o banco de dados está acessível e a tabela existe', 'error'),
            
            ('PREV_003', 'preview', 'Nenhuma transação encontrada para esta sessão', 
             'Query retornou zero registros para o session_id fornecido', 
             'Verifique se o upload foi concluído corretamente', 'warning'),
            
            ('PREV_004', 'preview', 'Erro ao processar transações', 
             'Falha no processamento via universal_processor', 
             'Verifique o formato dos dados ou contate o suporte', 'error'),
            
            ('PREV_005', 'preview', 'Erro ao classificar transações', 
             'Falha na classificação via cascade_classifier', 
             'Verifique se as tabelas de classificação estão populadas', 'error'),
            
            # UPLOAD ERRORS (UPL_*)
            ('UPL_001', 'upload', 'Arquivo não fornecido', 
             'Campo "file" está ausente ou vazio no FormData', 
             'Selecione um arquivo antes de fazer upload', 'error'),
            
            ('UPL_002', 'upload', 'Banco não especificado', 
             'Campo "banco" é obrigatório mas não foi fornecido', 
             'Selecione o banco na interface de upload', 'error'),
            
            ('UPL_003', 'upload', 'Mês fatura não especificado', 
             'Campo "mesFatura" é obrigatório mas não foi fornecido', 
             'Selecione o mês da fatura na interface de upload', 'error'),
            
            ('UPL_004', 'upload', 'Processador não encontrado', 
             'Não existe processador para a combinação banco+tipo+formato fornecida', 
             'Verifique se o banco e formato são suportados', 'error'),
            
            ('UPL_005', 'upload', 'Erro ao salvar arquivo temporário', 
             'Falha ao salvar arquivo no diretório uploads_temp', 
             'Verifique permissões do diretório ou espaço em disco', 'error'),
            
            ('UPL_006', 'upload', 'Erro ao processar arquivo', 
             'Falha ao parsear o arquivo CSV/XLS', 
             'Verifique se o arquivo está no formato correto', 'error'),
            
            # DATABASE ERRORS (DB_*)
            ('DB_001', 'database', 'Banco de dados não encontrado', 
             'Arquivo SQLite não existe no caminho esperado', 
             'Execute as migrations ou verifique o caminho do banco', 'critical'),
            
            ('DB_002', 'database', 'Erro ao conectar ao banco de dados', 
             'Falha ao abrir conexão SQLite', 
             'Verifique permissões do arquivo ou se está corrompido', 'critical'),
            
            ('DB_003', 'database', 'Tabela não encontrada', 
             'Tabela referenciada não existe no schema', 
             'Execute as migrations pendentes', 'error'),
            
            ('DB_004', 'database', 'Erro ao executar query', 
             'Query SQL falhou durante execução', 
             'Verifique sintaxe SQL e parâmetros fornecidos', 'error'),
            
            # CLASSIFICATION ERRORS (CLS_*)
            ('CLS_001', 'classification', 'Erro ao carregar classificador', 
             'Falha ao inicializar CascadeClassifier', 
             'Verifique se módulos Python estão instalados corretamente', 'error'),
            
            ('CLS_002', 'classification', 'Usuário não encontrado', 
             'user_id fornecido não existe na tabela users', 
             'Verifique autenticação ou cadastre o usuário', 'error'),
            
            ('CLS_003', 'classification', 'Erro ao buscar regras de exclusão', 
             'Falha ao consultar transacoes_exclusao', 
             'Verifique se a tabela existe e está acessível', 'error'),
            
            ('CLS_004', 'classification', 'Erro ao buscar padrões', 
             'Falha ao consultar base_padroes ou base_marcacoes', 
             'Verifique se as tabelas de classificação existem', 'error'),
            
            # VALIDATION ERRORS (VAL_*)
            ('VAL_001', 'validation', 'Formato de arquivo inválido', 
             'Extensão do arquivo não é suportada', 
             'Use apenas arquivos CSV, XLS ou XLSX', 'error'),
            
            ('VAL_002', 'validation', 'Arquivo muito grande', 
             'Tamanho do arquivo excede o limite permitido', 
             'Reduza o tamanho do arquivo ou divida em múltiplos uploads', 'error'),
            
            ('VAL_003', 'validation', 'Dados inválidos', 
             'Formato dos dados não corresponde ao esperado', 
             'Verifique se o arquivo está formatado corretamente', 'error'),
        ]
        
        cursor.executemany("""
            INSERT INTO error_codes (code, category, message_pt, technical_details, suggested_action, severity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, error_codes)
        
        conn.commit()
        print(f"✅ {len(error_codes)} códigos de erro inseridos")
        
        # Verificar estrutura
        cursor.execute("SELECT code, category, severity FROM error_codes ORDER BY code")
        codes = cursor.fetchall()
        
        print("\n📋 Códigos cadastrados:")
        for code, category, severity in codes:
            print(f"  - {code} ({category}) [{severity}]")
        
    except sqlite3.Error as e:
        print(f"❌ Erro ao criar tabela: {e}")
        conn.rollback()
        sys.exit(1)
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRATION: Criar tabela error_codes")
    print("=" * 60)
    print()
    
    criar_tabela_e_popular()
    
    print()
    print("=" * 60)
    print("✅ Migration concluída")
    print("=" * 60)
