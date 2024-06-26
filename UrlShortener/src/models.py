from datetime import datetime, timedelta
from typing import Annotated, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator
from pydantic.functional_validators import AfterValidator

from .db import search_doc_by_code, update_doc_by_code


class ShortURL(BaseModel):
    url: Annotated[str, AfterValidator(lambda url: url.strip())]


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
        max_length=32,
        min_length=1,
        pattern=r"^[a-zA-Z0-9_-]+$",
        default=None,
    )

    @field_validator("code")
    @classmethod
    def validate_unique_code(cls, code: str) -> str:
        try:
            search_doc_by_code(f"q_{code}")
            raise ValueError(f"{code} already exists in the database")
        except KeyError:
            return code


class URLMapSchema(BaseModel):
    long_url: Annotated[str, AfterValidator(lambda url: url.strip())]
    code: str = Field(default_factory=lambda: uuid4().hex, validate_default=True)
    expiration: datetime = Field(
        default_factory=lambda: datetime.now() + timedelta(hours=12)
    )

    def extend_expiration(self, hours: int = 12) -> None:
        if hours < 1:
            raise ValueError("Expiration time should be greater than 1 hour")
        self.expiration = datetime.now() + timedelta(hours=hours)
        update_doc_by_code(self.code, self.model_dump())

    @field_validator("code")
    @classmethod
    def add_prefix(cls, code: str) -> str:
        return code if code.startswith("q_") else f"q_{code}"
