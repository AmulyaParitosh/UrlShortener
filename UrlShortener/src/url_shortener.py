import random
import string
from typing import Annotated

import firebase_admin
from firebase_admin import credentials, firestore
from pydantic import AnyUrl, BaseModel
from pydantic.functional_validators import AfterValidator

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


class LongURL(BaseModel):
    url: Annotated[AnyUrl, AfterValidator(str), AfterValidator(lambda url: url.strip())]


async def generate_short_code() -> str:
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(6))


async def generate_shorten_url(base_url: str, long_url: LongURL) -> str:
    short_code = await generate_short_code()
    db.collection("urls").document(short_code).set({"long_url": long_url.url})
    print(f"11111111111111111111111111111111111{base_url}{short_code}")
    return f"{base_url}{short_code}"


async def fetch_redirect_url(short_code: str) -> LongURL:
    doc_ref = db.collection("urls").document(short_code)
    doc = doc_ref.get()
    if doc.exists:
        long_url = doc.to_dict()["long_url"]
        return LongURL(url=long_url)

    raise KeyError("URL not found")
