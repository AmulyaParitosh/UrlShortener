from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Request
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.events import GoToEvent
from fastui.forms import fastui_form

from ..models import LongURL, ShortURL
from .api_routes import shorten_url as generate_shorten_url

router = APIRouter(prefix="/api")


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def root() -> list[AnyComponent]:
    return [
        c.Page(
            components=[
                c.Heading(text="Url Shortener", level=1),
                c.ModelForm(
                    model=LongURL, display_mode="page", submit_url="/api/shorten2/"
                ),
            ]
        )
    ]


@router.post("/shorten2/", response_model=FastUI, response_model_exclude_none=True)
async def test_shorten_url(
    form: Annotated[LongURL, fastui_form(LongURL)],
    request: Request,
    background_tasks: BackgroundTasks,
) -> list[AnyComponent]:
    _short_url: ShortURL = await generate_shorten_url(form, request, background_tasks)
    short_url: str = str(_short_url.url)
    return [
        c.Page(
            components=[
                c.Heading(text="Shortened Url is", level=2),
                c.Link(
                    components=[c.Heading(text=short_url, level=4)],
                    on_click=GoToEvent(url=short_url),
                ),
                c.Button(text="Back", on_click=GoToEvent(url=str(request.base_url))),
            ]
        )
    ]