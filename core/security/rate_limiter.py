import time
from typing import Dict, Optional
from fastapi import HTTPException, Request
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from core.cache.redis_manager import redis_cache

class RateLimiter:
    """
    Rate limiter haute performance pour API Vantablack
    Supporte différents algorithms: token bucket, fixed window, sliding window
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis = redis_cache
        
    async def limit_request(
        self,
        request: Request,
        key: str,
        max_requests: int = 100,
        window_seconds: int = 60,
        algorithm: str = "sliding_window"
    ) -> bool:
        """
        Vérifier et appliquer la limite de taux
        
        Args:
            request: Requête FastAPI
            key: Clé unique pour le rate limiting
            max_requests: Nombre maximum de requêtes
            window_seconds: Fenêtre de temps en secondes
            algorithm: Algorithme à utiliser
        
        Returns:
            bool: True si la requête est autorisée, False sinon
        """
        
        # Obtenir l'IP du client
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # Créer une clé unique
        limiter_key = f"rate_limit:{key}:{client_ip}:{user_agent}"
        
        if algorithm == "sliding_window":
            return await self._sliding_window(limiter_key, max_requests, window_seconds)
        elif algorithm == "fixed_window":
            return await self._fixed_window(limiter_key, max_requests, window_seconds)
        elif algorithm == "token_bucket":
            return await self._token_bucket(limiter_key, max_requests, window_seconds)
        else:
            raise ValueError(f"Algorithm {algorithm} not supported")
    
    async def _sliding_window(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Algorithme sliding window plus précis"""
        current_time = time.time()
        window_start = current_time - window_seconds
        
        # Récupérer les timestamps des requêtes
        timestamps = self.redis.get(key) or []
        
        # Filtrer les requêtes dans la fenêtre actuelle
        timestamps = [ts for ts in timestamps if ts > window_start]
        
        if len(timestamps) >= max_requests:
            return False
        
        # Ajouter la nouvelle requête
        timestamps.append(current_time)
        
        # Stocker avec expiration
        self.redis.set(key, timestamps, window_seconds)
        
        return True
    
    async def _fixed_window(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Algorithme fixed window simple"""
        current_window = int(time.time() // window_seconds)
        counter_key = f"{key}:{current_window}"
        
        # Incrémenter le compteur
        current_count = self.redis.increment(counter_key, 1)
        
        # Définir l'expiration
        if current_count == 1:
            self.redis.get_client().expire(counter_key, window_seconds)
        
        return current_count <= max_requests
    
    async def _token_bucket(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Algorithme token bucket pour burst traffic"""
        bucket_key = f"{key}:tokens"
        last_refill_key = f"{key}:last_refill"
        
        current_time = time.time()
        
        # Récupérer l'état actuel
        tokens = self.redis.get(bucket_key) or max_requests
        last_refill = self.redis.get(last_refill_key) or current_time
        
        # Calculer les tokens à ajouter
        time_passed = current_time - last_refill
        tokens_to_add = time_passed * (max_requests / window_seconds)
        
        if tokens_to_add > 0:
            tokens = min(max_requests, tokens + tokens_to_add)
            last_refill = current_time
        
        # Vérifier si on peut consommer un token
        if tokens < 1:
            return False
        
        # Consommer un token
        tokens -= 1
        
        # Mettre à jour
        self.redis.set(bucket_key, tokens, window_seconds * 2)
        self.redis.set(last_refill_key, last_refill, window_seconds * 2)
        
        return True
    
    def get_remaining_requests(self, key: str, client_ip: str) -> Dict:
        """Obtenir le nombre de requêtes restantes"""
        limiter_key = f"rate_limit:{key}:{client_ip}"
        
        # Pour sliding window
        timestamps = self.redis.get(limiter_key) or []
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window
        
        timestamps = [ts for ts in timestamps if ts > window_start]
        remaining = max(0, 100 - len(timestamps))
        
        return {
            "remaining": remaining,
            "reset_in": 60 - (current_time - window_start),
            "limit": 100
        }

# Instance globale
rate_limiter = RateLimiter()

# Middleware pour rate limiting
async def rate_limit_middleware(request: Request, call_next):
    """Middleware global de rate limiting"""
    
    # Exclure certains endpoints du rate limiting
    if request.url.path in ["/v5/health", "/v5/metrics"]:
        return await call_next(request)
    
    # Appliquer le rate limiting
    allowed = await rate_limiter.limit_request(
        request,
        key="api_global",
        max_requests=100,  # 100 req/min par IP
        window_seconds=60,
        algorithm="sliding_window"
    )
    
    if not allowed:
        raise HTTPException(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": "60"}
        )
    
    response = await call_next(request)
    
    # Ajouter les headers de rate limiting
    remaining = rate_limiter.get_remaining_requests("api_global", request.client.host)
    response.headers["X-RateLimit-Limit"] = str(remaining["limit"])
    response.headers["X-RateLimit-Remaining"] = str(remaining["remaining"])
    response.headers["X-RateLimit-Reset"] = str(int(remaining["reset_in"]))
    
    return response