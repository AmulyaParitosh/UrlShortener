from typing import Annotated

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui import prebuilt_html
from fastui.events import BackEvent, GoToEvent
from fastui.forms import fastui_form
from pydantic import ValidationError

from .src.url_shortener import LongURL, fetch_redirect_url, generate_shorten_url

app = FastAPI()


@app.get("/api/", response_model=FastUI, response_model_exclude_none=True)
def root() -> list[AnyComponent]:
    return [
        c.Page(
            components=[
                c.Heading(text="Url Shortener", level=1),
                c.ModelForm(
                    model=LongURL, display_mode="page", submit_url="/api/shorten/"
                ),
            ]
        )
    ]


@app.post("/api/shorten/", response_model=FastUI, response_model_exclude_none=True)
async def test_shorten_url(
    form: Annotated[LongURL, fastui_form(LongURL)], request: Request
) -> list[AnyComponent]:
    short_url: str = await generate_shorten_url(str(request.base_url), form)
    return [
        c.Page(
            components=[
                c.Heading(text="Shortened Url is", level=2),
                c.Link(
                    components=[c.Heading(text=short_url, level=4)],
                    on_click=GoToEvent(url=short_url),
                ),
                c.Button(text="Back", on_click=BackEvent()),
            ]
        )
    ]


@app.post("/shorten")
async def shorten_url(url: LongURL, request: Request):
    try:
        short_url: str = await generate_shorten_url(str(request.base_url), url)
    except ValidationError as exc:
        raise HTTPException(
            status_code=400, detail=f"{url} is not a valid url"
        ) from exc
    return {"shortened_url": short_url}


@app.get("/{short_code}")
async def redirect_url(short_code: str):
    try:
        long_url = await fetch_redirect_url(short_code)
        return long_url
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="URL does not exists") from exc


@app.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title="URL Shortener"))
