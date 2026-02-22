import pytest
from core.proxy.aitm import AiTMProxy
from bs4 import BeautifulSoup

class TestAiTMProxy:
    
    @pytest.fixture
    def proxy(self):
        return AiTMProxy()
    
    def test_rewrite_url(self, proxy):
        base_url = "https://example.com/login"
        
        # Test lien absolu vers le même domaine
        url1 = "https://example.com/dashboard"
        rewritten1 = proxy._rewrite_url(url1, base_url)
        assert rewritten1 == "/dashboard"
        
        # Test lien relatif
        url2 = "/forgot-password"
        rewritten2 = proxy._rewrite_url(url2, base_url)
        assert rewritten2 == "/forgot-password"
        
        # Test lien avec query params
        url3 = "/search?q=test"
        rewritten3 = proxy._rewrite_url(url3, base_url)
        assert rewritten3 == "/search?q=test"
    
    def test_rewrite_html(self, proxy):
        base_url = "https://example.com/login"
        html = """
        <html>
            <body>
                <a href="https://example.com/dashboard">Dashboard</a>
                <form action="/auth/login" method="POST">
                    <input type="text" name="user">
                </form>
                <img src="https://example.com/logo.png">
            </body>
        </html>
        """
        
        rewritten_html = proxy.rewrite_html(html.encode('utf-8'), base_url)
        soup = BeautifulSoup(rewritten_html, "html.parser")
        
        # Vérification lien a href
        link = soup.find("a")
        assert link["href"] == "/dashboard"
        
        # Vérification form action
        form = soup.find("form")
        assert form["action"] == "/auth/login"
        
        # Vérification image src (non modifiée selon implémentation actuelle)
        img = soup.find("img")
        assert img["src"] == "https://example.com/logo.png"

@pytest.mark.asyncio
async def test_proxy_session_management():
    proxy = AiTMProxy()
    session = await proxy.get_session()
    assert session is not None
    assert not session.closed
    await proxy.close()
    assert session.closed
