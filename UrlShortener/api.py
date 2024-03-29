from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import HTMLResponse
from fastui import prebuilt_html

from .src.routes import api_routes, base_routes, ui_routes

app = FastAPI()
app.include_router(base_routes.router)
app.include_router(api_routes.router)
app.include_router(ui_routes.router)


@app.get("/{rest_of_path:path}")
async def html_landing(rest_of_path: str, background_tasks: BackgroundTasks):
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    if not rest_of_path.startswith("q_"):
        # return HTMLResponse()
        return HTMLResponse(prebuilt_html(title="URL Shortener", api_root_url="/ui"))
    return await base_routes.redirect_url(rest_of_path, background_tasks)
