import redis
import json
import time
import asyncio
from typing import Any, Optional, Dict, List, Set
from functools import wraps
from core.common.config import get

class RedisCacheManager:
    """
    Gestionnaire de cache Redis haute performance pour Vantablack
    Supporte la réplication, sharding et expiration intelligente.
    Inclut un fallback en mémoire si Redis n'est pas disponible.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or get("REDIS_URL") or "redis://localhost:6379"
        self.connection_pool = None
        self._use_memory = False
        self._memory_cache = {}
        self._memory_sets = {}
        self._connect()
    
    def _connect(self):
        """Établir la connexion Redis avec pool de connexions"""
        try:
            self.connection_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                max_connections=100,
                socket_timeout=1,
                socket_connect_timeout=1,
                retry_on_timeout=False,
                health_check_interval=30
            )
            # Test connection
            with self.get_client() as client:
                client.ping()
            self._use_memory = False
            print("[Redis] Connected successfully")
        except Exception as e:
            print(f"[Redis] Connection failed, switching to Memory Cache: {e}")
            self.connection_pool = None
            self._use_memory = True

    def get_client(self):
        """Obtenir un client Redis thread-safe"""
        if self._use_memory:
            # Si mode mémoire, on retourne un objet qui lève une exception pour forcer le fallback
            # ou on gère le fallback dans chaque méthode.
            # Ici on retourne None pour signaler l'absence de client.
            return None
            
        if self.connection_pool is None:
             try:
                 self.connection_pool = redis.ConnectionPool.from_url(self.redis_url)
             except Exception as e:
                 print(f"Warning: Redis connection failed: {e}")
                 self._use_memory = True
                 return None
                 
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
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                cache_key = f"{prefix}{key}:{str(args)}:{str(kwargs)}"
                
                # Try to get from cache
                try:
                    cached_result = self.get(cache_key)
                    if cached_result is not None:
                        return cached_result
                except Exception:
                    pass
                
                # Execute async function
                result = await func(*args, **kwargs)
                
                # Check condition for caching
                if condition is None or condition(result):
                    try:
                        self.set(cache_key, result, expire)
                    except Exception:
                        pass
                
                return result
            
            # Return the appropriate wrapper based on function type
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return wrapper
        return decorator
    
    def set(self, key: str, value: Any, expire: int = 300) -> bool:
        """Stocker une valeur avec expiration"""
        if self._use_memory:
            self._memory_cache[key] = {
                "value": value,
                "expire_at": time.time() + expire
            }
            return True

        try:
            with self.get_client() as client:
                serialized = json.dumps(value)
                return client.setex(key, expire, serialized)
        except Exception as e:
            print(f"Redis Set Error (fallback to memory): {e}")
            self._use_memory = True
            return self.set(key, value, expire)
    
    def exists(self, key: str) -> bool:
        """Vérifie si une clé existe"""
        if self._use_memory:
            if key in self._memory_cache:
                item = self._memory_cache[key]
                if item["expire_at"] > time.time():
                    return True
                else:
                    del self._memory_cache[key]
            return False

        try:
            client = self.get_client()
            return bool(client.exists(key))
        except Exception as e:
            print(f"Redis Exists Error (fallback to memory): {e}")
            self._use_memory = True
            return self.exists(key)

    def get(self, key: str) -> Optional[Any]:
        """Récupérer une valeur"""
        if self._use_memory:
            if key in self._memory_cache:
                item = self._memory_cache[key]
                if item["expire_at"] > time.time():
                    return item["value"]
                else:
                    del self._memory_cache[key]
            return None

        try:
            with self.get_client() as client:
                result = client.get(key)
                if result:
                    return json.loads(result)
                return None
        except Exception as e:
            print(f"Redis Get Error (fallback to memory): {e}")
            self._use_memory = True
            return self.get(key)

    def delete(self, key: str) -> bool:
        """Supprimer une clé"""
        if self._use_memory:
            if key in self._memory_cache:
                del self._memory_cache[key]
                return True
            return False

        try:
            with self.get_client() as client:
                return client.delete(key)
        except Exception as e:
            print(f"Redis Delete Error (fallback to memory): {e}")
            self._use_memory = True
            return self.delete(key)
            
    def sadd(self, key: str, value: str) -> int:
        """Ajouter un membre à un set"""
        if self._use_memory:
            if key not in self._memory_sets:
                self._memory_sets[key] = set()
            if value not in self._memory_sets[key]:
                self._memory_sets[key].add(value)
                return 1
            return 0

        try:
            with self.get_client() as client:
                return client.sadd(key, value)
        except Exception as e:
            print(f"Redis SADD Error (fallback to memory): {e}")
            self._use_memory = True
            return self.sadd(key, value)

    def srem(self, key: str, value: str) -> int:
        """Retirer un membre d'un set"""
        if self._use_memory:
            if key in self._memory_sets and value in self._memory_sets[key]:
                self._memory_sets[key].remove(value)
                return 1
            return 0

        try:
            with self.get_client() as client:
                return client.srem(key, value)
        except Exception as e:
            print(f"Redis SREM Error (fallback to memory): {e}")
            self._use_memory = True
            return self.srem(key, value)

    def smembers(self, key: str) -> List[str]:
        """Récupérer tous les membres d'un set"""
        if self._use_memory:
            return list(self._memory_sets.get(key, []))

        try:
            with self.get_client() as client:
                members = client.smembers(key)
                return [m.decode('utf-8') if isinstance(m, bytes) else m for m in members]
        except Exception as e:
            print(f"Redis SMEMBERS Error (fallback to memory): {e}")
            self._use_memory = True
            return self.smembers(key)
            
    def scan_keys(self, pattern: str) -> List[str]:
        """Scanner les clés correspondant au pattern"""
        if self._use_memory:
            import fnmatch
            # Convert redis pattern to fnmatch pattern (very basic approximation)
            fn_pattern = pattern.replace("*", "*") 
            return fnmatch.filter(self._memory_cache.keys(), fn_pattern)

        keys = []
        cursor = '0'
        try:
            with self.get_client() as client:
                while cursor != 0:
                    cursor, data = client.scan(cursor=cursor, match=pattern, count=100)
                    keys.extend(data)
            return [k.decode('utf-8') if isinstance(k, bytes) else k for k in keys]
        except Exception as e:
            print(f"Redis Scan Error (fallback to memory): {e}")
            self._use_memory = True
            return self.scan_keys(pattern)
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Incrémenter une valeur numérique"""
        if self._use_memory:
            if key not in self._memory_cache:
                self._memory_cache[key] = {"value": 0, "expire_at": time.time() + 3600}
            
            try:
                val = int(self._memory_cache[key]["value"])
                val += amount
                self._memory_cache[key]["value"] = val
                return val
            except:
                return 0

        try:
            with self.get_client() as client:
                return client.incrby(key, amount)
        except Exception:
            self._use_memory = True
            return self.increment(key, amount)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques du cache"""
        if self._use_memory:
            return {
                "used_memory": "Memory Mode",
                "connected_clients": 0,
                "keyspace_hits": 0,
                "keyspace_misses": 0,
                "hit_rate": 0,
                "keys_count": len(self._memory_cache)
            }

        try:
            with self.get_client() as client:
                info = client.info()
                return {
                    "used_memory": info.get("used_memory_human", "0"),
                    "connected_clients": info.get("connected_clients", 0),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0),
                    "hit_rate": info.get("keyspace_hits", 0) / max(1, info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0))
                }
        except Exception:
            self._use_memory = True
            return self.get_stats()
    
    def clear_cache(self, pattern: str = "cache:*") -> int:
        """Vider le cache selon un motif"""
        if self._use_memory:
            keys = self.scan_keys(pattern)
            count = 0
            for k in keys:
                if k in self._memory_cache:
                    del self._memory_cache[k]
                    count += 1
            return count

        try:
            with self.get_client() as client:
                keys = client.keys(pattern)
                if keys:
                    return client.delete(*keys)
                return 0
        except Exception:
            self._use_memory = True
            return self.clear_cache(pattern)

    def acquire_lock(self, lock_name: str, acquire_timeout: int = 10, lock_timeout: int = 10) -> Any:
        """
        Acquérir un verrou distribué (Redis Lock).
        Retourne l'objet lock si succès, False sinon.
        """
        if self._use_memory:
            # Dummy lock implementation for memory mode
            class MemoryLock:
                def __init__(self, name):
                    self.name = name
                def acquire(self): return True
                def release(self): pass
            return MemoryLock(lock_name)

        try:
            client = self.get_client()
            lock = client.lock(f"lock:{lock_name}", timeout=lock_timeout, blocking_timeout=acquire_timeout)
            if lock.acquire():
                return lock
            return False
        except Exception as e:
            print(f"Redis Lock Error: {e}")
            self._use_memory = True
            return self.acquire_lock(lock_name, acquire_timeout, lock_timeout)

# Instance globale
redis_cache = RedisCacheManager()
