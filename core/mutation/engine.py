"""
Vantablack Core v5 - Mutation Engine
====================================

Handles:
- Polymorphic obfuscation of Javascript (AST based)
- HTML structure mutation (tag randomization, class renaming)
- CSS selector rewriting
"""

import re
import random
import string
import logging
from typing import Dict, List
from bs4 import BeautifulSoup
import jsbeautifier

class MutationEngine:
    def __init__(self):
        self.logger = logging.getLogger("vantablack.mutation.engine")
        self._class_map: Dict[str, str] = {}
        self._id_map: Dict[str, str] = {}

    def generate_random_name(self, length: int = 8) -> str:
        """Generate a random variable/class name"""
        chars = string.ascii_letters
        return ''.join(random.choice(chars) for _ in range(length))

    def mutate_html(self, html_content: str) -> str:
        """
        Mutate HTML structure:
        - Rename classes and IDs
        - Inject dummy comments/tags
        - Shuffle attributes
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 1. Rename Classes
        for tag in soup.find_all(class_=True):
            new_classes = []
            for cls in tag['class']:
                if cls not in self._class_map:
                    self._class_map[cls] = self.generate_random_name()
                new_classes.append(self._class_map[cls])
            tag['class'] = new_classes
            
        # 2. Rename IDs
        for tag in soup.find_all(id=True):
            old_id = tag['id']
            if old_id not in self._id_map:
                self._id_map[old_id] = self.generate_random_name()
            tag['id'] = self._id_map[old_id]

        # 3. Inject Noise (Invisible elements)
        body = soup.find('body')
        if body:
            noise = soup.new_tag('div', style="display:none")
            noise.string = self.generate_random_name(32)
            body.insert(0, noise)
            
        return str(soup)

    def mutate_js(self, js_content: str) -> str:
        """
        Simple JS obfuscation (variable renaming, string splitting).
        For V5, we simulate AST transformation with regex/string ops for now.
        Real AST requires `esprima` or `slimit` which are heavy deps.
        """
        # 1. Split Strings
        def split_string(match):
            s = match.group(1)
            if len(s) > 4:
                mid = len(s) // 2
                return f"'{s[:mid]}' + '{s[mid:]}'"
            return f"'{s}'"
            
        obfuscated = re.sub(r"'([^']*)'", split_string, js_content)
        
        # 2. Remove comments
        obfuscated = re.sub(r"//.*", "", obfuscated)
        
        # 3. Minify/Beautify to change structure
        opts = jsbeautifier.default_options()
        opts.indent_size = 2
        return jsbeautifier.beautify(obfuscated, opts)

    def get_maps(self) -> Dict:
        """Return the mapping used for current mutation context"""
        return {"classes": self._class_map, "ids": self._id_map}
