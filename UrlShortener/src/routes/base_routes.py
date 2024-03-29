from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import RedirectResponse

from ..db import search_doc_by_code
from ..models import URLMapSchema

router = APIRouter(prefix="/api")


@router.get("/{code}")
async def redirect_url(
    code: str, background_tasks: BackgroundTasks
) -> RedirectResponse:
    print("hello there")
    try:
        doc = search_doc_by_code(code)
        print(doc.to_dict())
    except KeyError as ke:
        raise HTTPException(status_code=404, detail="URL does not exists") from ke

    url_map = URLMapSchema(**doc.to_dict())
    background_tasks.add_task(url_map.extend_expiration, 12)

    return RedirectResponse(url=url_map.long_url, status_code=301)
