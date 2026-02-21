from fastapi.testclient import TestClient
from core.web.server import create_app
from core.api.routes import router


def build_app():
    app = create_app()
    app.include_router(router)
    return app


def test_ui_pages_load():
    client = TestClient(build_app())
    for path in ["/ui", "/ui/guides", "/ui/status", "/ui/qr", "/ui/docs"]:
        r = client.get(path)
        assert r.status_code == 200
        assert "text/html" in r.headers.get("content-type", "")


def test_static_assets_available():
    client = TestClient(build_app())
    r = client.get("/static/js/main.js")
    assert r.status_code == 200
    assert "javascript" in r.headers.get("content-type", "")

