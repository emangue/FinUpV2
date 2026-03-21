"""
Cliente Redis compartilhado — pool thread-safe para FastAPI (workers síncronos).

Uso:
    from app.core.redis_client import redis_get, redis_set, redis_delete

Fallback silencioso: se o Redis estiver indisponível (ex: container não subiu),
as funções retornam None/False sem lançar exceção — o app continua funcionando
em modo degradado (sem cache).
"""

import json
import logging
import os
from typing import Any, Optional

import redis

logger = logging.getLogger(__name__)

# Pool compartilhado (thread-safe). Reutilizado por todos os workers.
_pool: Optional[redis.ConnectionPool] = None


def _get_pool() -> redis.ConnectionPool:
    global _pool
    if _pool is None:
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        _pool = redis.ConnectionPool.from_url(
            redis_url,
            decode_responses=True,
            max_connections=10,
        )
    return _pool


def get_redis() -> redis.Redis:
    """Retorna cliente Redis com pool compartilhado."""
    return redis.Redis(connection_pool=_get_pool())


# ─── API pública ─────────────────────────────────────────────────────────────

def redis_get(key: str) -> Optional[Any]:
    """
    Lê e desserializa valor do Redis.
    Retorna None se chave não existir ou Redis indisponível.
    """
    try:
        raw = get_redis().get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as exc:
        logger.debug("redis_get(%s) falhou silenciosamente: %s", key, exc)
        return None


def redis_set(key: str, value: Any, ex: int = 300) -> bool:
    """
    Serializa e grava valor no Redis com TTL em segundos (padrão: 5 min).
    Retorna True em sucesso, False em falha silenciosa.
    """
    try:
        get_redis().set(key, json.dumps(value, default=str), ex=ex)
        return True
    except Exception as exc:
        logger.debug("redis_set(%s) falhou silenciosamente: %s", key, exc)
        return False


def redis_delete(key: str) -> None:
    """
    Remove chave do Redis (invalidação de cache).
    Falha silenciosa — não propaga exceção.
    """
    try:
        get_redis().delete(key)
    except Exception as exc:
        logger.debug("redis_delete(%s) falhou silenciosamente: %s", key, exc)
