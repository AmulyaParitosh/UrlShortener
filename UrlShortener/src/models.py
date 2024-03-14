from typing import Annotated

from pydantic import AnyUrl, BaseModel
from pydantic.functional_validators import AfterValidator


class LongURL(BaseModel):
    url: Annotated[AnyUrl, AfterValidator(str), AfterValidator(lambda url: url.strip())]


class ShortURL(BaseModel):
    url: Annotated[AnyUrl, AfterValidator(str), AfterValidator(lambda url: url.strip())]
