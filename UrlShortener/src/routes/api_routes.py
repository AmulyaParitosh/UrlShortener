from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import AnyUrl, ValidationError

from ..db import (
    remove_expired_urls,
    save_doc,
    search_doc_by_code,
    search_doc_by_long_url,
)
from ..models import LongURL, ShortURL, URLMapSchema

router = APIRouter()


@router.post("/shorten")
async def shorten_url(
    long_url: LongURL, request: Request, background_tasks: BackgroundTasks
) -> ShortURL:
    try:
        try:
            doc = search_doc_by_long_url(long_url.url)
            url_map = URLMapSchema(**doc.to_dict())
            background_tasks.add_task(url_map.extend_expiration, 12)
        except KeyError:
            url_map = URLMapSchema(long_url=long_url.url)
            save_doc(url_map.code, url_map.model_dump())
        finally:
            background_tasks.add_task(remove_expired_urls)

        return ShortURL(url=AnyUrl(f"{request.base_url}q/{url_map.code}"))

    except ValidationError as exc:
        raise HTTPException(
            status_code=400, detail=f"{long_url} is not a valid url"
        ) from exc


@router.get("/q/{short_code}")
async def redirect_url(
    short_code: str, background_tasks: BackgroundTasks
) -> RedirectResponse:
    try:
        doc = search_doc_by_code(short_code)
    except KeyError:
        raise HTTPException(status_code=404, detail="URL does not exists")

    url_map = URLMapSchema(**doc.to_dict())
    background_tasks.add_task(url_map.extend_expiration, 12)

    return RedirectResponse(url=str(url_map.long_url), status_code=302)
