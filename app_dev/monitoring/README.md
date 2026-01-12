# 📊 Sistema de Monitoring - Finanças V4

Sistema completo de monitoramento com Prometheus, Grafana e Alertmanager.

## 🎯 Arquitetura

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│   Backend   │────▶│  Prometheus  │────▶│  Grafana   │
│  (FastAPI)  │     │  (Metrics)   │     │(Dashboard) │
└─────────────┘     └──────────────┘     └────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Alertmanager │
                    │  (Alerts)    │
                    └──────────────┘
                           │
                           ▼
                    Email / Slack
```

## 🚀 Quick Start

### 1. Iniciar Stack de Monitoring

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev/monitoring
docker-compose -f docker-compose.monitoring.yml up -d
```

### 2. Acessos

- **Grafana:** http://localhost:3001
  - User: `admin`
  - Pass: `admin` (alterar no primeiro login)

- **Prometheus:** http://localhost:9090

- **Alertmanager:** http://localhost:9093

### 3. Verificar Saúde

```bash
# Ver status dos containers
docker-compose -f docker-compose.monitoring.yml ps

# Ver logs
docker-compose -f docker-compose.monitoring.yml logs -f
```

## 📦 Componentes

### Prometheus
**Porta:** 9090  
**Função:** Coleta e armazena métricas (time-series database)

**Métricas coletadas:**
- Request rate (req/s)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- CPU, Memory, Disk usage
- Database size
- Backup success/failure

**Retention:** 30 dias

### Grafana
**Porta:** 3001  
**Função:** Visualização de dashboards

**Dashboards disponíveis:**
- Sistema Overview (req/s, errors, latency)
- System Resources (CPU, RAM, Disk)
- Database Metrics
- Backup Status

### Alertmanager
**Porta:** 9093  
**Função:** Gerenciamento e roteamento de alertas

**Alertas configurados:**
- ServiceDown (critical)
- HighErrorRate (warning)
- CriticalErrorRate (critical)
- HighResponseTime (warning)
- LowDiskSpace (critical)
- BackupFailed (critical)

## 📊 Dashboards Grafana

### Dashboard Principal: "Financas Overview"

**Painéis:**
1. **Request Rate** - Requisições por segundo
2. **Error Rate** - Porcentagem de erros 4xx/5xx
3. **Response Time** - Latência (p50, p95, p99)
4. **Active Users** - Usuários ativos
5. **Database Size** - Tamanho do banco
6. **System Resources** - CPU, RAM, Disk

### Criar Dashboard Personalizado

1. Acessar Grafana (http://localhost:3001)
2. Dashboard → New → Add Visualization
3. Selecionar datasource: Prometheus
4. Exemplos de queries:

```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))

# P95 latency
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# CPU usage
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100
```

## 🔔 Configurar Alertas

### Email (Gmail)

1. Editar `alertmanager.yml`:
```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'seu-email@gmail.com'
  smtp_auth_username: 'seu-email@gmail.com'
  smtp_auth_password: 'senha-app-google'  # App password!
```

2. Criar App Password no Google:
   - https://myaccount.google.com/apppasswords
   - Selecionar "Mail" e "Other"
   - Copiar senha gerada

3. Reiniciar Alertmanager:
```bash
docker-compose -f docker-compose.monitoring.yml restart alertmanager
```

### Slack (Opcional)

1. Criar Incoming Webhook no Slack:
   - https://api.slack.com/messaging/webhooks

2. Descomentar seção Slack no `alertmanager.yml`:
```yaml
slack_configs:
  - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
    channel: '#alerts-critical'
```

## 📈 Métricas Customizadas (Backend)

Para expor métricas no backend FastAPI, adicionar Prometheus client:

```bash
pip install prometheus-client
```

```python
# backend/app/main.py
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Response

# Métricas
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Endpoint de métricas
@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

## 🔧 Troubleshooting

### Prometheus não está coletando métricas

```bash
# Verificar targets
curl http://localhost:9090/api/v1/targets

# Verificar config
docker exec financas-prometheus promtool check config /etc/prometheus/prometheus.yml

# Ver logs
docker-compose -f docker-compose.monitoring.yml logs prometheus
```

### Grafana não conecta no Prometheus

```bash
# Verificar se Prometheus está respondendo
curl http://prometheus:9090/api/v1/query?query=up

# Verificar network
docker network inspect monitoring
```

### Alertas não estão sendo enviados

```bash
# Verificar config do Alertmanager
docker exec financas-alertmanager amtool check-config /etc/alertmanager/alertmanager.yml

# Ver alertas ativos
curl http://localhost:9093/api/v2/alerts

# Testar email
docker exec financas-alertmanager amtool alert add test
```

## 📊 Queries Úteis

### Request Rate por Endpoint
```promql
sum(rate(http_requests_total[5m])) by (endpoint)
```

### Top 5 Endpoints Mais Lentos
```promql
topk(5, histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint)))
```

### Erro Rate por Status Code
```promql
sum(rate(http_requests_total{status=~"4.."}[5m])) by (status)
sum(rate(http_requests_total{status=~"5.."}[5m])) by (status)
```

### Database Growth Rate
```promql
rate(node_filesystem_size_bytes{mountpoint="/var/lib/financas/db"}[1h])
```

### Backup Success Rate
```promql
rate(backup_success_total[24h]) / rate(backup_attempts_total[24h])
```

## 🔐 Segurança

### Expor métricas apenas internamente

No nginx.conf, bloquear /metrics externamente:

```nginx
location /metrics {
    deny all;
    return 403;
}
```

### Autenticação no Grafana

1. Alterar senha padrão no primeiro login
2. Desabilitar signup: `GF_USERS_ALLOW_SIGN_UP=false`
3. Usar OAuth (Google, GitHub) em produção

### Proteger Prometheus e Alertmanager

Adicionar auth básica no nginx:

```nginx
location /prometheus/ {
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://prometheus:9090/;
}
```

## 📦 Backup de Configurações

```bash
# Backup de dashboards Grafana
docker exec financas-grafana grafana-cli admin export-dashboard > dashboards-backup.json

# Backup de configs Prometheus
cp monitoring/prometheus.yml monitoring/prometheus.yml.backup
cp monitoring/alerts.yml monitoring/alerts.yml.backup
```

## 🚀 Deploy em Produção

### 1. Atualizar docker-compose.yml principal

Adicionar depends_on para garantir monitoring:

```yaml
services:
  app:
    depends_on:
      - prometheus
      - grafana
```

### 2. Configurar Reverse Proxy

Adicionar no nginx.conf:

```nginx
# Grafana
location /grafana/ {
    proxy_pass http://grafana:3000/;
}

# Prometheus (apenas admin)
location /prometheus/ {
    auth_basic "Admin Only";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://prometheus:9090/;
}
```

### 3. Persistent Volumes

Volumes já configurados no docker-compose.monitoring.yml:
- `prometheus-data` - 30 dias de métricas
- `grafana-data` - Dashboards e configurações
- `alertmanager-data` - Histórico de alertas

## 📝 Checklist de Setup

- [ ] ✅ Iniciar stack de monitoring
- [ ] ✅ Acessar Grafana e alterar senha
- [ ] ✅ Verificar datasource Prometheus conectado
- [ ] ✅ Configurar email no Alertmanager
- [ ] ✅ Testar alerta manual
- [ ] ✅ Criar dashboard customizado
- [ ] ✅ Configurar retention de métricas
- [ ] ✅ Backup de configurações

## 📚 Referências

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)

## 🆘 Suporte

**Logs em tempo real:**
```bash
docker-compose -f docker-compose.monitoring.yml logs -f
```

**Restart completo:**
```bash
docker-compose -f docker-compose.monitoring.yml down
docker-compose -f docker-compose.monitoring.yml up -d
```

**Remover volumes (CUIDADO: perde dados):**
```bash
docker-compose -f docker-compose.monitoring.yml down -v
```
