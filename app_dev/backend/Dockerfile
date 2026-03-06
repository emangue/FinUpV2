# ============================================
# Stage 1: Builder - Instalar dependências
# ============================================
FROM python:3.11-slim AS builder

# Evitar bytecode desnecessário e forçar output imediato (logs limpos)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instalar deps do sistema para compilar
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar apenas requirements primeiro (cache layer — não invalida se código mudou)
COPY requirements.txt .

# Instalar deps em venv isolado
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 2: Runtime - Imagem final otimizada
# ============================================
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Instalar apenas runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar venv do builder (sem compiladores no runtime)
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

# Criar user não-root ANTES de copiar o código
RUN useradd -m -u 1000 appuser

# Copiar código e ajustar permissões
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
