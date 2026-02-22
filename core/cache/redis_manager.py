import redis
import json
import time
from typing import Any, Optional, Dict, List
from functools import wraps
from core.common.config import get

class RedisCacheManager:
    """
    Gestionnaire de cache Redis haute performance pour Vantablack
    Supporte la réplication, sharding et expiration intelligente
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or get("REDIS_URL") or "redis://localhost:6379"
        self.connection_pool = None
        self._connect()
    
    def _connect(self):
        """Établir la connexion Redis avec pool de connexions"""
        try:
            self.connection_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                max_connections=100,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Test connection
            with self.get_client() as client:
                client.ping()
        except redis.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")
    
    def get_client(self):
        """Obtenir un client Redis thread-safe"""
        return redis.Redis(connection_pool=self.connection_pool)
    
    def cached(
        self,
        key: str,
        expire: int = 300,
        prefix: str = "cache:",
        condition: Optional[callable] = None
    ):
        """
        Decorator pour mettre en cache le résultat d'une fonction
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = f"{prefix}{key}:{str(args)}:{str(kwargs)}"
                
                # Try to get from cache
                try:
                    cached_result = self.get(cache_key)
                    if cached_result is not None:
                        return cached_result
                except Exception:
                    pass
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Check condition for caching
                if condition is None or condition(result):
                    try:
                        self.set(cache_key, result, expire)
                    except Exception:
                        pass
                
                return result
            return wrapper
        return decorator
    
    def set(self, key: str, value: Any, expire: int = 300) -> bool:
        """Stocker une valeur avec expiration"""
        with self.get_client() as client:
            serialized = json.dumps(value)
            return client.setex(key, expire, serialized)
    
    def get(self, key: str) -> Optional[Any]:
        """Récupérer une valeur"""
        with self.get_client() as client:
            result = client.get(key)
            if result:
                return json.loads(result)
            return None
    
    def delete(self, key: str) -> bool:
        """Supprimer une clé"""
        with self.get_client() as client:
            return client.delete(key) > 0
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Incrémenter une valeur numérique"""
        with self.get_client() as client:
            return client.incrby(key, amount)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques du cache"""
        with self.get_client() as client:
            info = client.info()
            return {
                "used_memory": info.get("used_memory_human", "0"),
                "connected_clients": info.get("connected_clients", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": info.get("keyspace_hits", 0) / max(1, info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0))
            }
    
    def clear_cache(self, pattern: str = "cache:*") -> int:
        """Vider le cache selon un motif"""
        with self.get_client() as client:
            keys = client.keys(pattern)
            if keys:
                return client.delete(*keys)
            return 0

# Instance globale
redis_cache = RedisCacheManager()

# Exemple d'utilisation:
# @redis_cache.cached("user_data", expire=600)
# def get_user_data(user_id):
#     # Logique coûteuse ici
#     return expensive_operation()