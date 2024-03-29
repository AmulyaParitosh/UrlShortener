from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from ..db import (
    remove_expired_urls,
    save_doc,
    search_doc_by_code,
    search_doc_by_long_url,
)
from ..models import LongURLForm, ShortURL, URLMapSchema

router = APIRouter(prefix="/api")


@router.post("/shorten")
async def shorten_url(
    long_url: LongURLForm, request: Request, background_tasks: BackgroundTasks
) -> ShortURL:
    try:
        url_map = (
            await handle_custom_code(long_url)
            if long_url.code
            else await handle_standard_code(long_url)
        )

        background_tasks.add_task(url_map.extend_expiration, 12)
        return ShortURL(url=f"{request.base_url}{url_map.code}")

    except ValidationError as exc:
        raise HTTPException(
            status_code=400, detail=f"{long_url} is not a valid url"
        ) from exc

    finally:
        background_tasks.add_task(remove_expired_urls)


async def handle_custom_code(long_url: LongURLForm) -> URLMapSchema:
    try:
        search_doc_by_code(long_url.code)
        raise HTTPException(
            status_code=400, detail=f"{long_url.code} already exists in the database"
        )
    except KeyError:
        url_map = URLMapSchema(long_url=long_url.url, code=long_url.code)
        save_doc(url_map.code, url_map.model_dump())
    return url_map


async def handle_standard_code(long_url: LongURLForm) -> URLMapSchema:
    try:
        doc = search_doc_by_long_url(long_url.url)
        url_map = URLMapSchema(**doc.to_dict())
    except KeyError:
        url_map = URLMapSchema(long_url=long_url.url)
        save_doc(url_map.code, url_map.model_dump())
    return url_map
