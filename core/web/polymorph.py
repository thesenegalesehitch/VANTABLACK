
import random
import string
import re
from pathlib import Path

class PolymorphicEngine:
    """
    Moteur de polymorphisme JavaScript pour Vantablack v5.
    Génère du code JS unique à chaque requête pour éviter la détection par signature.
    """
    
    def __init__(self, js_path: Path):
        self.js_path = js_path
        self.base_code = ""
        self._load_base_code()

    def _load_base_code(self):
        if self.js_path.exists():
            with open(self.js_path, "r") as f:
                self.base_code = f.read()
        else:
            self.base_code = "// Error: Base JS not found"

    def _generate_random_name(self, length=8):
        return ''.join(random.choices(string.ascii_letters, k=length))

    def _generate_junk_code(self):
        """Génère du code mort (junk code) pour modifier la signature du fichier"""
        junk_type = random.choice(['var', 'function', 'comment'])
        name = self._generate_random_name()
        
        if junk_type == 'var':
            val = random.randint(0, 1000)
            return f"var {name} = {val} + {random.randint(1,10)};"
        elif junk_type == 'function':
            return f"function {name}(){{ return '{self._generate_random_name()}'; }}"
        else:
            return f"/* {self._generate_random_name()} {random.randint(0,9999)} */"

    def obfuscate(self, global_var_name: str = "VantaFP") -> str:
        """
        Obfusque le code de base :
        1. Renomme les variables internes
        2. Renomme l'objet principal
        3. Ajoute du junk code complexe
        4. Expose l'objet sous le nom global demandé
        """
        code = self.base_code
        
        # 1. Rename internal variables (Scope-safe heuristics)
        # We rename 'components' and 'signals' which are local to functions
        vars_map = {
            "components": self._generate_random_name(10),
            "signals": self._generate_random_name(10),
            "mouseMoves": self._generate_random_name(8),
            "scrollEvents": self._generate_random_name(8),
            "keyPresses": self._generate_random_name(8),
            "startTime": self._generate_random_name(8)
        }
        
        for old, new in vars_map.items():
            # Use word boundaries to avoid replacing substrings
            code = re.sub(r'\b' + old + r'\b', new, code)

        # 2. Rename internal object
        internal_name = self._generate_random_name(12)
        code = code.replace("FingerprintCollector", internal_name)
        
        # 3. Expose to global scope with the desired name
        # The original code ends with: root.FingerprintCollector = FingerprintCollector;
        # We replaced FingerprintCollector with internal_name, so it is: root.internal_name = internal_name;
        pattern = f"root\\.{internal_name}\\s*=\\s*{internal_name};"
        replacement = f"root.{global_var_name} = {internal_name};"
        code = re.sub(pattern, replacement, code)
        
        # 4. Inject junk code at random lines
        lines = code.split('\n')
        new_lines = []
        
        # Helper to generate logic junk
        def get_logic_junk():
            v1 = random.randint(1, 100)
            v2 = random.randint(1, 100)
            return f"if ({v1} > {v2}) {{ var {self._generate_random_name(4)} = {v1*v2}; }}"

        for line in lines:
            # Randomly insert junk before the line
            if random.random() < 0.15: 
                junk_choice = random.choice(['var', 'func', 'logic', 'comment'])
                if junk_choice == 'logic':
                    new_lines.append(get_logic_junk())
                elif junk_choice == 'func':
                    fname = self._generate_random_name(6)
                    new_lines.append(f"function {fname}(a){{return a?{random.randint(0,9)}:0;}}")
                elif junk_choice == 'comment':
                    new_lines.append(f"/* {self._generate_random_name(15)} */")
                else:
                    new_lines.append(self._generate_junk_code())
            
            new_lines.append(line)
        
        return '\n'.join(new_lines)

# Singleton instance setup in server.py or similar
