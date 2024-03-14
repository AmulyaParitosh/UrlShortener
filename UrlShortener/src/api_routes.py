from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from .models import LongURL, ShortURL
from .shortener import fetch_redirect_url, generate_shorten_url

router = APIRouter()


@router.post("/shorten")
async def shorten_url(url: LongURL, request: Request) -> ShortURL:
    try:
        short_url: ShortURL = await generate_shorten_url(str(request.base_url), url)
    except ValidationError as exc:
        raise HTTPException(
            status_code=400, detail=f"{url} is not a valid url"
        ) from exc
    return short_url


@router.get("/{short_code}")
async def redirect_url(short_code: str):
    try:
        long_url: LongURL = await fetch_redirect_url(short_code)
        return RedirectResponse(url=str(long_url.url), status_code=302)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="URL does not exists") from exc
