from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastui import prebuilt_html

from .src.routes import api_routes, ui_routes

app = FastAPI()
app.include_router(api_routes.router)
app.include_router(ui_routes.router)

@app.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title="URL Shortener"))
