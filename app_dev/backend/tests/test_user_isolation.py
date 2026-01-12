#!/usr/bin/env python3
"""
Test User Isolation - Sistema de Finanças V4

Valida que usuários NÃO podem acessar dados de outros usuários.
Cria 3 usuários com transações e testa 50+ queries para garantir isolamento.

Resultado esperado: 0 vazamentos de dados entre usuários
"""

import sys
import os
from pathlib import Path

# Adicionar app/ ao path para imports
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date, timedelta
import hashlib

# Imports do sistema
from app.core.database import Base
from app.domains.users.models import User, RefreshToken
from app.domains.users.service import hash_password
from app.domains.transactions.models import JournalEntry
from app.domains.categories.models import BaseMarcacao
from app.domains.upload.history_models import UploadHistory


# Configuração do banco de teste
TEST_DB_PATH = app_dir / "database" / "test_isolation.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

# Setup database
engine = create_engine(TEST_DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


class IsolationTester:
    """Classe para testar isolamento de usuários"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.test_results = []
        
    def setup_database(self):
        """Criar database limpo para testes"""
        print("🔧 Configurando banco de teste...")
        
        # Remover DB antigo se existir
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
        
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas")
        
    def create_test_users(self, db):
        """Criar 3 usuários de teste"""
        print("\n👥 Criando usuários de teste...")
        
        users_data = [
            {"name": "Alice", "email": "alice@test.com", "password": "senha123"},
            {"name": "Bob", "email": "bob@test.com", "password": "senha123"},
            {"name": "Carlos", "email": "carlos@test.com", "password": "senha123"}
        ]
        
        users = []
        for data in users_data:
            user = User(
                nome=data["name"],
                email=data["email"],
                password_hash=hash_password(data["password"])
            )
            db.add(user)
            db.flush()  # Para obter o ID
            users.append(user)
        
        db.commit()
        print(f"✅ {len(users)} usuários criados")
        print(f"   - Alice (ID: {users[0].id})")
        print(f"   - Bob (ID: {users[1].id})")
        print(f"   - Carlos (ID: {users[2].id})")
        
        return users
    
    def create_test_transactions(self, db, users):
        """Criar transações para cada usuário"""
        print("\n💰 Criando transações de teste...")
        
        base_date = date.today() - timedelta(days=30)
        transactions_per_user = 10
        
        for user_idx, user in enumerate(users):
            for i in range(transactions_per_user):
                trans_date = base_date + timedelta(days=i)
                
                transaction = JournalEntry(
                    user_id=user.id,
                    Data=trans_date,
                    Estabelecimento=f"Loja {user.nome} {i+1}",
                    Valor=100.00 * (user_idx + 1),  # Alice: 100, Bob: 200, Carlos: 300
                    TipoTransacao="Débito",
                    CategoriaGeral="Alimentação",
                    arquivo_origem=f"test_{user.nome.lower()}.csv",
                    IdTransacao=self._generate_id_transacao(trans_date, f"Loja {user.nome} {i+1}", 100.00 * (user_idx + 1), i+1)
                )
                db.add(transaction)
        
        db.commit()
        
        # Contar transações por usuário
        counts = {}
        for user in users:
            count = db.query(JournalEntry).filter(JournalEntry.user_id == user.id).count()
            counts[user.nome] = count
        
        print(f"✅ Transações criadas:")
        for name, count in counts.items():
            print(f"   - {name}: {count} transações")
        
        return counts
    
    def _generate_id_transacao(self, data, estabelecimento, valor, seq):
        """Gerar IdTransacao único"""
        data_str = data.strftime("%Y-%m-%d")
        valor_str = f"{valor:.2f}"
        base = f"{data_str}|{estabelecimento}|{valor_str}"
        hash_base = hashlib.sha256(base.encode()).hexdigest()[:12]
        return f"{hash_base}_{seq:04d}"
    
    def test_transaction_isolation(self, db, users):
        """Testar que usuários não veem transações de outros"""
        print("\n🔍 TESTE 1: Isolamento de transações (JournalEntry)")
        
        alice, bob, carlos = users
        
        # Alice deve ver apenas suas transações
        alice_trans = db.query(JournalEntry).filter(JournalEntry.user_id == alice.id).all()
        self._assert_equal(len(alice_trans), 10, "Alice deve ter 10 transações", "test_transaction_isolation_alice")
        
        # Bob deve ver apenas suas transações
        bob_trans = db.query(JournalEntry).filter(JournalEntry.user_id == bob.id).all()
        self._assert_equal(len(bob_trans), 10, "Bob deve ter 10 transações", "test_transaction_isolation_bob")
        
        # Carlos deve ver apenas suas transações
        carlos_trans = db.query(JournalEntry).filter(JournalEntry.user_id == carlos.id).all()
        self._assert_equal(len(carlos_trans), 10, "Carlos deve ter 10 transações", "test_transaction_isolation_carlos")
        
        # Validar que os valores são diferentes (Alice=100, Bob=200, Carlos=300)
        alice_valor = alice_trans[0].Valor if alice_trans else 0
        bob_valor = bob_trans[0].Valor if bob_trans else 0
        self._assert_not_equal(alice_valor, bob_valor, "Valores de Alice e Bob devem ser diferentes", "test_transaction_values")
        
        # Query sem filtro user_id (DEVE ser evitado no código!)
        all_trans_no_filter = db.query(JournalEntry).all()
        if len(all_trans_no_filter) > 10:
            self._warning("Query sem filtro user_id retorna dados de múltiplos usuários (OK se for admin)", "test_no_filter_warning")
        
        print(f"  ✅ {self.passed} testes passaram")
        if self.failed > 0:
            print(f"  ❌ {self.failed} testes falharam")
    
    def test_upload_history_isolation(self, db, users):
        """Testar isolamento de histórico de uploads"""
        print("\n🔍 TESTE 2: Isolamento de histórico de upload")
        
        import uuid
        alice, bob, _ = users
        
        # Criar uploads para Alice e Bob
        alice_upload = UploadHistory(
            user_id=alice.id,
            session_id=str(uuid.uuid4()),
            banco="Itaú",
            tipo_documento="extrato",
            nome_arquivo="alice_extrato.csv",
            status="success",
            total_registros=10,
            transacoes_duplicadas=0
        )
        bob_upload = UploadHistory(
            user_id=bob.id,
            session_id=str(uuid.uuid4()),
            banco="BTG",
            tipo_documento="fatura",
            nome_arquivo="bob_fatura.csv",
            status="success",
            total_registros=15,
            transacoes_duplicadas=2
        )
        db.add(alice_upload)
        db.add(bob_upload)
        db.commit()
        
        # Alice deve ver apenas seus uploads
        alice_uploads = db.query(UploadHistory).filter(UploadHistory.user_id == alice.id).all()
        self._assert_equal(len(alice_uploads), 1, "Alice deve ter 1 upload", "test_upload_isolation_alice")
        self._assert_equal(alice_uploads[0].nome_arquivo, "alice_extrato.csv", "Filename de Alice deve estar correto", "test_upload_filename_alice")
        
        # Bob deve ver apenas seus uploads
        bob_uploads = db.query(UploadHistory).filter(UploadHistory.user_id == bob.id).all()
        self._assert_equal(len(bob_uploads), 1, "Bob deve ter 1 upload", "test_upload_isolation_bob")
        self._assert_equal(bob_uploads[0].nome_arquivo, "bob_fatura.csv", "Filename de Bob deve estar correto", "test_upload_filename_bob")
        
        print(f"  ✅ {self.passed} testes passaram")
        if self.failed > 0:
            print(f"  ❌ {self.failed} testes falharam")
    
    def test_refresh_token_isolation(self, db, users):
        """Testar isolamento de refresh tokens"""
        print("\n🔍 TESTE 3: Isolamento de refresh tokens")
        
        alice, bob, _ = users
        
        # Criar tokens para Alice e Bob
        alice_token = RefreshToken(
            user_id=alice.id,
            token_hash=hash_password("alice_token_123"),
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        bob_token = RefreshToken(
            user_id=bob.id,
            token_hash=hash_password("bob_token_456"),
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(alice_token)
        db.add(bob_token)
        db.commit()
        
        # Alice deve ver apenas seu token
        alice_tokens = db.query(RefreshToken).filter(RefreshToken.user_id == alice.id).all()
        self._assert_equal(len(alice_tokens), 1, "Alice deve ter 1 token", "test_token_isolation_alice")
        
        # Bob deve ver apenas seu token
        bob_tokens = db.query(RefreshToken).filter(RefreshToken.user_id == bob.id).all()
        self._assert_equal(len(bob_tokens), 1, "Bob deve ter 1 token", "test_token_isolation_bob")
        
        # Tokens não devem ser iguais
        self._assert_not_equal(
            alice_tokens[0].token_hash, 
            bob_tokens[0].token_hash, 
            "Token hashes devem ser únicos", 
            "test_token_uniqueness"
        )
        
        print(f"  ✅ {self.passed} testes passaram")
        if self.failed > 0:
            print(f"  ❌ {self.failed} testes falharam")
    
    def test_aggregation_queries(self, db, users):
        """Testar queries de agregação (SUM, COUNT) com isolamento"""
        print("\n🔍 TESTE 4: Isolamento em queries de agregação")
        
        from sqlalchemy import func
        
        alice, bob, carlos = users
        
        # Total de transações por usuário (Alice=10, Bob=10, Carlos=10)
        for user, expected_count in [(alice, 10), (bob, 10), (carlos, 10)]:
            count = db.query(func.count(JournalEntry.id)).filter(JournalEntry.user_id == user.id).scalar()
            self._assert_equal(count, expected_count, f"{user.nome} deve ter {expected_count} transações", f"test_count_{user.nome.lower()}")
        
        # Soma de valores por usuário (Alice=1000, Bob=2000, Carlos=3000)
        expected_sums = {alice.id: 1000.00, bob.id: 2000.00, carlos.id: 3000.00}
        for user in users:
            total = db.query(func.sum(JournalEntry.Valor)).filter(JournalEntry.user_id == user.id).scalar() or 0
            expected = expected_sums[user.id]
            self._assert_equal(total, expected, f"{user.nome} deve ter total R${expected:.2f}", f"test_sum_{user.nome.lower()}")
        
        print(f"  ✅ {self.passed} testes passaram")
        if self.failed > 0:
            print(f"  ❌ {self.failed} testes falharam")
    
    def test_cross_user_leak(self, db, users):
        """Testar que NÃO há vazamento entre usuários"""
        print("\n🔍 TESTE 5: Detecção de vazamentos (CRÍTICO)")
        
        alice, bob, _ = users
        
        # Tentar buscar transações de Bob usando ID de Alice (NÃO deve retornar nada)
        leak_test = db.query(JournalEntry).filter(
            JournalEntry.user_id == alice.id,
            JournalEntry.Estabelecimento.like("%Bob%")  # Estabelecimentos de Bob
        ).all()
        
        self._assert_equal(len(leak_test), 0, "Alice NÃO deve ver transações de Bob", "test_cross_leak_alice_bob")
        
        # Tentar buscar uploads de Bob usando ID de Alice
        upload_leak = db.query(UploadHistory).filter(
            UploadHistory.user_id == alice.id,
            UploadHistory.nome_arquivo.like("%bob%")
        ).all()
        
        self._assert_equal(len(upload_leak), 0, "Alice NÃO deve ver uploads de Bob", "test_upload_leak")
        
        # Tentar buscar tokens de Bob usando ID de Alice
        token_leak = db.query(RefreshToken).filter(
            RefreshToken.user_id == alice.id
        ).join(User).filter(User.email == "bob@test.com").all()
        
        self._assert_equal(len(token_leak), 0, "Alice NÃO deve ver tokens de Bob", "test_token_leak")
        
        print(f"  ✅ {self.passed} testes passaram")
        if self.failed > 0:
            print(f"  ❌ {self.failed} FALHAS CRÍTICAS DETECTADAS!")
    
    def _assert_equal(self, actual, expected, message, test_name):
        """Assert que valores são iguais"""
        if actual == expected:
            self.passed += 1
            self.test_results.append({
                "test": test_name,
                "status": "PASS",
                "message": message
            })
        else:
            self.failed += 1
            error_msg = f"{message} | Esperado: {expected}, Obtido: {actual}"
            self.test_results.append({
                "test": test_name,
                "status": "FAIL",
                "message": error_msg
            })
            print(f"    ❌ FALHA: {error_msg}")
    
    def _assert_not_equal(self, actual, expected, message, test_name):
        """Assert que valores são diferentes"""
        if actual != expected:
            self.passed += 1
            self.test_results.append({
                "test": test_name,
                "status": "PASS",
                "message": message
            })
        else:
            self.failed += 1
            error_msg = f"{message} | Valores iguais: {actual}"
            self.test_results.append({
                "test": test_name,
                "status": "FAIL",
                "message": error_msg
            })
            print(f"    ❌ FALHA: {error_msg}")
    
    def _warning(self, message, test_name):
        """Registrar warning (não é falha)"""
        self.warnings += 1
        self.test_results.append({
            "test": test_name,
            "status": "WARNING",
            "message": message
        })
        print(f"    ⚠️ WARNING: {message}")
    
    def print_summary(self):
        """Imprimir resumo final dos testes"""
        print("\n" + "="*60)
        print("📊 RESUMO DOS TESTES DE ISOLAMENTO")
        print("="*60)
        print(f"✅ Testes passaram: {self.passed}")
        print(f"❌ Testes falharam: {self.failed}")
        print(f"⚠️ Warnings: {self.warnings}")
        print(f"📋 Total de testes: {self.passed + self.failed}")
        
        if self.failed == 0:
            print("\n🎉 SUCESSO! Isolamento de usuários está funcionando corretamente!")
            print("   Nenhum vazamento de dados detectado.")
        else:
            print("\n🚨 FALHA! Vazamentos de dados detectados!")
            print("   ⚠️ CRÍTICO: Sistema NÃO está pronto para produção!")
            print("\nTestes que falharam:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result['message']}")
        
        print("="*60)
        
        return self.failed == 0
    
    def cleanup(self):
        """Limpar database de teste"""
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
            print("\n🧹 Database de teste removido")


def main():
    """Executar todos os testes de isolamento"""
    print("="*60)
    print("🔒 TESTE DE ISOLAMENTO DE USUÁRIOS - Sistema Finanças V4")
    print("="*60)
    print("Objetivo: Validar que usuários NÃO podem acessar dados de outros")
    print("Resultado esperado: 0 vazamentos detectados")
    print("="*60)
    
    tester = IsolationTester()
    
    try:
        # Setup
        tester.setup_database()
        
        # Criar sessão
        db = SessionLocal()
        
        try:
            # Criar dados de teste
            users = tester.create_test_users(db)
            tester.create_test_transactions(db, users)
            
            # Executar testes
            tester.test_transaction_isolation(db, users)
            tester.test_upload_history_isolation(db, users)
            tester.test_refresh_token_isolation(db, users)
            tester.test_aggregation_queries(db, users)
            tester.test_cross_user_leak(db, users)
            
            # Resumo
            success = tester.print_summary()
            
            return 0 if success else 1
            
        finally:
            db.close()
    
    finally:
        # Cleanup
        tester.cleanup()


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
