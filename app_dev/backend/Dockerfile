# ============================================
# Stage 1: Builder - Instalar dependências
# ============================================
FROM python:3.9-slim as builder

# Instalar deps do sistema para compilar
RUN apt-get update && apt-get install -y \
    gcc g++ make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar apenas requirements primeiro (cache layer)
COPY requirements.txt .

# Instalar deps em venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 2: Runtime - Imagem final otimizada
# ============================================
FROM python:3.9-slim

# Instalar apenas runtime deps
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar venv do builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copiar código
COPY . .

# Criar user não-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# Comando
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
