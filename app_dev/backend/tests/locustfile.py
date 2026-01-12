#!/usr/bin/env python3
"""
Load Test com Locust - Sistema de Finanças V4

Simula 100 usuários simultâneos realizando operações típicas:
- Login
- Consulta de transações
- Upload de CSV
- Dashboard

Métricas esperadas:
- Response time p95 < 500ms
- Error rate < 1%
- 100 usuários simultâneos

Para executar:
    locust -f locustfile.py --headless -u 100 -r 10 --run-time 2m --host=http://localhost:8000

Ou com UI:
    locust -f locustfile.py --host=http://localhost:8000
    # Acessar: http://localhost:8089
"""

from locust import HttpUser, task, between, events
import random
import json
from datetime import datetime, timedelta

# Credenciais de teste (usar demo user se existir)
TEST_USERS = [
    {"email": "admin@email.com", "password": "admin123"},
    {"email": "demo@financas.com", "password": "demo123"},
]


class FinancasUser(HttpUser):
    """
    Usuário simulado do sistema de finanças
    
    Comportamento:
    - Wait time: 1-5s entre requisições (simula pensamento humano)
    - Tasks: Login, consultas, dashboard
    - Sessão persistente com cookies
    """
    
    wait_time = between(1, 5)  # Aguardar 1-5s entre tasks
    
    def on_start(self):
        """
        Executado uma vez ao iniciar cada usuário simulado
        Faz login e guarda token
        """
        # Escolher usuário aleatório
        self.user_creds = random.choice(TEST_USERS)
        
        # Fazer login
        response = self.client.post(
            "/api/v1/auth/login",
            json=self.user_creds,
            name="/auth/login"
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.access_token}"}
        else:
            self.access_token = None
            self.headers = {}
    
    @task(3)  # Peso 3 (mais frequente)
    def list_transactions(self):
        """
        Listar transações do mês atual
        Task mais comum (peso 3)
        """
        if not self.access_token:
            return
        
        # Simular consulta do mês atual
        now = datetime.now()
        params = {
            "mes": now.month,
            "ano": now.year
        }
        
        self.client.get(
            "/api/v1/transactions/list",
            params=params,
            headers=self.headers,
            name="/transactions/list"
        )
    
    @task(2)  # Peso 2
    def get_budget_vs_actual(self):
        """
        Consultar budget vs actual
        """
        if not self.access_token:
            return
        
        now = datetime.now()
        params = {
            "mes": now.month,
            "ano": now.year
        }
        
        self.client.get(
            "/api/v1/dashboard/budget-vs-actual",
            params=params,
            headers=self.headers,
            name="/dashboard/budget-vs-actual"
        )
    
    @task(2)  # Peso 2
    def get_dashboard_categories(self):
        """
        Consultar categorias do dashboard
        """
        if not self.access_token:
            return
        
        now = datetime.now()
        params = {
            "mes": now.month,
            "ano": now.year
        }
        
        self.client.get(
            "/api/v1/dashboard/categories",
            params=params,
            headers=self.headers,
            name="/dashboard/categories"
        )
    
    @task(1)  # Peso 1 (menos frequente)
    def get_dashboard_metrics(self):
        """
        Buscar métricas gerais
        """
        if not self.access_token:
            return
        
        now = datetime.now()
        params = {
            "mes": now.month,
            "ano": now.year
        }
        
        self.client.get(
            "/api/v1/dashboard/metrics",
            params=params,
            headers=self.headers,
            name="/dashboard/metrics"
        )
    
    @task(1)  # Peso 1
    def filter_by_category(self):
        """
        Filtrar transações por filtros
        """
        if not self.access_token:
            return
        
        # Simular soma filtrada
        now = datetime.now()
        params = {
            "mes": now.month,
            "ano": now.year
        }
        
        self.client.get(
            "/api/v1/transactions/filtered-total",
            params=params,
            headers=self.headers,
            name="/transactions/filtered-total"
        )
    
    @task(1)  # Peso 1 (raro, operação pesada)
    def upload_history(self):
        """
        Consultar histórico de uploads
        """
        if not self.access_token:
            return
        
        self.client.get(
            "/api/v1/upload/history",
            headers=self.headers,
            name="/upload/history"
        )
    
    @task(1)  # Peso 1
    def get_user_profile(self):
        """
        Consultar perfil do usuário (/me)
        """
        if not self.access_token:
            return
        
        self.client.get(
            "/api/v1/auth/me",
            headers=self.headers,
            name="/auth/me"
        )


# ==================================================
# Event Handlers (Relatórios)
# ==================================================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Executado ao iniciar o teste"""
    print("="*60)
    print("🚀 INICIANDO TESTE DE CARGA - Sistema Finanças V4")
    print("="*60)
    print(f"Target: {environment.host}")
    print(f"Usuários: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")
    print(f"Spawn rate: N/A")
    print("="*60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Executado ao finalizar o teste"""
    stats = environment.stats
    
    print("\n" + "="*60)
    print("📊 RESUMO DO TESTE DE CARGA")
    print("="*60)
    
    # Estatísticas gerais
    total_requests = stats.total.num_requests
    total_failures = stats.total.num_failures
    error_rate = (total_failures / total_requests * 100) if total_requests > 0 else 0
    
    print(f"Total de requisições: {total_requests}")
    print(f"Falhas: {total_failures}")
    print(f"Error rate: {error_rate:.2f}%")
    print(f"RPS médio: {stats.total.total_rps:.2f} req/s")
    print(f"Response time médio: {stats.total.avg_response_time:.2f}ms")
    print(f"Response time p50: {stats.total.get_response_time_percentile(0.5):.2f}ms")
    print(f"Response time p95: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"Response time p99: {stats.total.get_response_time_percentile(0.99):.2f}ms")
    
    print("\n📋 Detalhes por endpoint:")
    for name, entry in stats.entries.items():
        if entry.num_requests > 0:
            endpoint_error_rate = (entry.num_failures / entry.num_requests * 100)
            print(f"\n  {name}")
            print(f"    Requests: {entry.num_requests}")
            print(f"    Failures: {entry.num_failures} ({endpoint_error_rate:.2f}%)")
            print(f"    Avg: {entry.avg_response_time:.2f}ms")
            print(f"    p95: {entry.get_response_time_percentile(0.95):.2f}ms")
    
    # Validações
    print("\n" + "="*60)
    print("✅ VALIDAÇÕES")
    print("="*60)
    
    p95_time = stats.total.get_response_time_percentile(0.95)
    
    if p95_time < 500:
        print(f"✅ PASS: Response time p95 < 500ms ({p95_time:.2f}ms)")
    else:
        print(f"❌ FAIL: Response time p95 > 500ms ({p95_time:.2f}ms)")
    
    if error_rate < 1.0:
        print(f"✅ PASS: Error rate < 1% ({error_rate:.2f}%)")
    else:
        print(f"❌ FAIL: Error rate > 1% ({error_rate:.2f}%)")
    
    # Decisão final
    success = (p95_time < 500 and error_rate < 1.0)
    
    print("\n" + "="*60)
    if success:
        print("🎉 SUCESSO! Sistema aguenta carga de 100 usuários")
        print("   - Performance OK (p95 < 500ms)")
        print("   - Estabilidade OK (error rate < 1%)")
    else:
        print("🚨 FALHA! Sistema não aguenta carga esperada")
        if p95_time >= 500:
            print(f"   - Response time muito alto (p95: {p95_time:.2f}ms)")
        if error_rate >= 1.0:
            print(f"   - Taxa de erro muito alta ({error_rate:.2f}%)")
    print("="*60)


if __name__ == "__main__":
    """
    Executar standalone (sem locust CLI)
    """
    print("💡 Para executar este teste de carga:")
    print("")
    print("1. Instalar Locust:")
    print("   pip install locust")
    print("")
    print("2. Executar teste headless (2 min, 100 usuários):")
    print("   locust -f locustfile.py --headless -u 100 -r 10 --run-time 2m --host=http://localhost:8000")
    print("")
    print("3. Ou com interface web:")
    print("   locust -f locustfile.py --host=http://localhost:8000")
    print("   Acessar: http://localhost:8089")
    print("")
    print("4. Parâmetros:")
    print("   -u: Número de usuários simultâneos")
    print("   -r: Spawn rate (usuários/segundo)")
    print("   --run-time: Duração do teste")
    print("   --host: URL do backend")
