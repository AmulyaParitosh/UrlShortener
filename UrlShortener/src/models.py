import uuid
from datetime import datetime, timedelta
from typing import Annotated

from pydantic import AnyUrl, BaseModel
from pydantic.functional_validators import AfterValidator

from .db import update_doc_by_code


class LongURL(BaseModel):
    url: Annotated[AnyUrl, AfterValidator(str), AfterValidator(lambda url: url.strip())]


class ShortURL(BaseModel):
    url: Annotated[AnyUrl, AfterValidator(str), AfterValidator(lambda url: url.strip())]


class URLMapSchema(BaseModel):
    long_url: Annotated[
        AnyUrl, AfterValidator(str), AfterValidator(lambda url: url.strip())
    ]
    code: str = str(uuid.uuid1())
    expiration: datetime = datetime.now() + timedelta(hours=12)

    def extend_expiration(self, hours: int = 12) -> None:
        if hours < 1:
            raise ValueError("Expiration time should be greater than 1 hour")
        self.expiration = datetime.now() + timedelta(hours=hours)
        update_doc_by_code(self.code, self.model_dump())
