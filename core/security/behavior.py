
import math
import time
from typing import Dict, List, Any
from core.cache.redis_manager import redis_cache

class BehaviorEngine:
    """
    Moteur d'analyse comportementale Vantablack V5 (Behavioral Analysis).
    Détecte les bots via l'analyse dynamique des interactions (souris, clavier, timing).
    Score 0-100: 0 = Bot certain, 100 = Humain certain.
    """
    
    def __init__(self):
        self.redis = redis_cache
        
    def analyze_session(self, session_id: str, interaction_data: Dict[str, Any]) -> int:
        """
        Analyse les données d'interaction et retourne un score de confiance (0-100).
        """
        score = 50 # Start neutral
        
        # 1. Timing Analysis
        time_on_page = interaction_data.get("timeOnPage", 0)
        if time_on_page < 500: # < 0.5s
            score -= 40 # Inhumainement rapide
        elif time_on_page < 2000: # < 2s
            score -= 10 # Suspect
        else:
            score += 10 # Normal
            
        # 2. Mouse Dynamics
        mouse_moves = interaction_data.get("mouseMoves", 0)
        if mouse_moves == 0:
            # Could be mobile, check touch
            if not interaction_data.get("touchSupport", False):
                score -= 30 # Desktop sans souris = Bot
        elif mouse_moves < 5:
            score -= 10 # Très peu de mouvement
        else:
            score += 10
            
        # 3. Typing Speed (if available)
        key_presses = interaction_data.get("keyPresses", 0)
        if key_presses > 0:
            cpm = (key_presses / (time_on_page / 60000)) if time_on_page > 0 else 9999
            if cpm > 1500: # > 1500 chars/min
                score -= 40 # Bot paste
            elif cpm > 800:
                score -= 10 # Fast typer or paste
            else:
                score += 10
                
        # 4. Consistency Check (Entropy - simplified)
        # Si on avait les coordonnées brutes, on calculerait l'entropie de Shannon.
        # Ici on se base sur des heuristiques simples.
        
        # 5. Browser/Environment Consistency
        if interaction_data.get("is_webdriver", False):
            score = 0 # Game over
            
        # Cap score
        return max(0, min(100, score))

    def update_score(self, session_id: str, delta: int):
        """Mise à jour incrémentale du score de session."""
        key = f"behavior:{session_id}"
        current = self.redis.get(key) or 50
        new_score = max(0, min(100, current + delta))
        self.redis.set(key, new_score, expire=3600)
        return new_score

# Global Instance
behavior_engine = BehaviorEngine()
