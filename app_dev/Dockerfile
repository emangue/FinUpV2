# ==========================================
# DOCKERFILE MULTI-STAGE - Sistema de Finanças v4
# ==========================================
# 
# Estrutura:
# - Stage 1: Build Frontend (Next.js → static files)
# - Stage 2: Setup Backend (Python dependencies)
# - Stage 3: Runtime Final (Backend + Frontend servidos)
#
# Uso:
#   docker build -t financas-app:latest .
#   docker run -p 8000:8000 -p 3000:3000 financas-app:latest
# ==========================================

# ==========================================
# STAGE 1: Build Frontend (Next.js)
# ==========================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copiar package.json e instalar dependências
COPY frontend/package*.json ./
RUN npm ci

# Copiar código fonte do frontend
COPY frontend/ ./

# Build Next.js para produção
# Gera pasta .next/ com arquivos otimizados
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
RUN npm run build

# ==========================================
# STAGE 2: Setup Backend Python
# ==========================================
FROM python:3.11-slim AS backend-builder

WORKDIR /app/backend

# Instalar dependências do sistema necessárias para compilar pacotes Python
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==========================================
# STAGE 3: Runtime Final
# ==========================================
FROM python:3.11-slim

# Metadados
LABEL maintainer="Emanuel Guerra <emangue@financas.com>"
LABEL version="4.0.0"
LABEL description="Sistema de Controle Financeiro Pessoal - Multi-tenant"

# Variáveis de ambiente de produção
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=production
ENV DEBUG=False

# Criar usuário não-root para segurança
RUN groupadd -r financas && useradd -r -g financas financas

# Diretórios da aplicação
WORKDIR /app

# Copiar dependências Python do stage 2
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copiar código backend
COPY backend/ ./backend/

# Copiar frontend buildado do stage 1
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/public ./frontend/public
COPY --from=frontend-builder /app/frontend/package*.json ./frontend/
COPY --from=frontend-builder /app/frontend/node_modules ./frontend/node_modules

# Criar diretórios necessários com permissões corretas
RUN mkdir -p /var/lib/financas/db /var/lib/financas/uploads /var/lib/financas/backups && \
    chown -R financas:financas /app /var/lib/financas

# Copiar script de entrada
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Instalar Node.js para rodar Next.js (apenas runtime)
RUN apt-get update && apt-get install -y nodejs npm && \
    rm -rf /var/lib/apt/lists/*

# Trocar para usuário não-root
USER financas

# Expor portas
EXPOSE 8000 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Volume para dados persistentes
VOLUME ["/var/lib/financas/db", "/var/lib/financas/uploads", "/var/lib/financas/backups"]

# Entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]

# Comando padrão: iniciar backend e frontend
CMD ["start"]
