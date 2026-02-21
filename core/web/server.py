from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional
import os
import shutil
from datetime import datetime
from core.qr_link_system import qr_link_system, QRConfig, QRCorrectionLevel

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
IMAGES_DIR = STATIC_DIR / "images"


def create_app() -> FastAPI:
    app = FastAPI(title="Vantablack UI")

    # Ensure directories exist
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    # Mount static files
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # Templates
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

    # UI pages
    @app.get("/ui", response_class=HTMLResponse)
    async def ui_dashboard(request: Request):
        return templates.TemplateResponse("dashboard.html", {"request": request})

    @app.get("/ui/guides", response_class=HTMLResponse)
    async def ui_guides(request: Request):
        return templates.TemplateResponse("guides.html", {"request": request})

    @app.get("/ui/status", response_class=HTMLResponse)
    async def ui_status(request: Request):
        return templates.TemplateResponse("status.html", {"request": request})

    @app.get("/ui/qr", response_class=HTMLResponse)
    async def ui_qr(request: Request):
        return templates.TemplateResponse("qr.html", {"request": request})

    @app.get("/ui/docs", response_class=HTMLResponse)
    async def ui_docs(request: Request):
        return templates.TemplateResponse("docs.html", {"request": request})

    # Minimal content API (optional, returns full page content for now)
    @app.get("/ui/api/content/{page}", response_class=HTMLResponse)
    async def ui_content(request: Request, page: str):
        mapping = {
            "dashboard": "dashboard.html",
            "guides": "guides.html",
            "status": "status.html",
            "qr": "qr.html",
            "docs": "docs.html",
        }
        template = mapping.get(page, "dashboard.html")
        return templates.TemplateResponse(template, {"request": request})

    # QR generation endpoint
    @app.post("/ui/api/generate-qr")
    async def generate_qr(
        request: Request,
        url: str = Form(...),
        validate: bool = Form(True),
        fill_color: str = Form("#000000"),
        back_color: str = Form("#FFFFFF"),
        logo: Optional[UploadFile] = File(None),
    ):
        try:
            logo_path = None
            if logo:
                # Save uploaded logo to images dir
                logo_filename = f"logo_{int(datetime.utcnow().timestamp())}_{logo.filename}"
                logo_path = IMAGES_DIR / logo_filename
                with logo_path.open("wb") as f:
                    shutil.copyfileobj(logo.file, f)

            config = QRConfig(
                error_correction=QRCorrectionLevel.HIGH,
                fill_color=fill_color,
                back_color=back_color,
                logo_path=str(logo_path) if logo_path else None,
            )

            out_name = f"qr_{int(datetime.utcnow().timestamp())}.png"
            out_path = IMAGES_DIR / out_name

            result = qr_link_system.generate_qr_with_link_validation(
                url=url,
                output_path=str(out_path),
                validate=validate,
                config=config,
            )

            if result.get("qr_generated"):
                return JSONResponse(
                    {
                        "ok": True,
                        "file": f"/static/images/{out_name}",
                        "metrics": qr_link_system.get_metrics(),
                        "validation": result.get("validation"),
                    }
                )
            else:
                return JSONResponse(
                    {"ok": False, "error": result.get("error", "unknown")}, status_code=400
                )
        except Exception as e:
            return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

    return app

