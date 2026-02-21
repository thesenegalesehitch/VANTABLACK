import json
import os

class I18n:
    def __init__(self, default_lang="en"):
        self.lang = default_lang
        self.translations = {}
        self.load_translations()

    def load_translations(self):
        locales_dir = os.path.join(os.path.dirname(__file__), "../locales")
        for filename in os.listdir(locales_dir):
            if filename.endswith(".json"):
                lang_code = filename.split(".")[0]
                with open(os.path.join(locales_dir, filename), "r", encoding="utf-8") as f:
                    self.translations[lang_code] = json.load(f)

    def set_language(self, lang):
        if lang in self.translations:
            self.lang = lang
            return True
        return False

    def t(self, key, **kwargs):
        """Translate a key to the current language."""
        text = self.translations.get(self.lang, {}).get(key, key)
        try:
            return text.format(**kwargs)
        except KeyError:
            return text

# Global instance
i18n = I18n()

def set_lang(lang):
    i18n.set_language(lang)

def t(key, **kwargs):
    return i18n.t(key, **kwargs)
