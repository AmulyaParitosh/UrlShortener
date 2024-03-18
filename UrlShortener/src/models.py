from datetime import datetime, timedelta
from typing import Annotated, Optional
from uuid import uuid4

from pydantic import BaseModel, Field
from pydantic.functional_validators import AfterValidator

from .db import update_doc_by_code


class LongURL(BaseModel):
    url: Annotated[str, AfterValidator(lambda url: url.strip())]


class LongURLForm(BaseModel):

    url: Annotated[str, AfterValidator(lambda url: url.strip())] = Field(
        title="Long URL",
        description="URL to be shortened",
        max_length=2048,
        min_length=1,
        pattern=r"^(http|https)://.*$",
    )
    code: Optional[str] = Field(
        title="Short code",
        description="Custom short code for the URL",
        max_length=10,
        min_length=1,
        pattern=r"^[a-zA-Z0-9_-]+$",
        default=None,
    )


class ShortURL(BaseModel):
    url: Annotated[str, AfterValidator(lambda url: url.strip())]


class URLMapSchema(BaseModel):
    long_url: Annotated[str, AfterValidator(lambda url: url.strip())]
    code: str = Field(default_factory=lambda: uuid4().hex)
    expiration: datetime = Field(
        default_factory=lambda: datetime.now() + timedelta(hours=12)
    )

    def extend_expiration(self, hours: int = 12) -> None:
        if hours < 1:
            raise ValueError("Expiration time should be greater than 1 hour")
        self.expiration = datetime.now() + timedelta(hours=hours)
        update_doc_by_code(self.code, self.model_dump())
