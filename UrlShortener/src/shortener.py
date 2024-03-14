import random
import string

import firebase_admin
from firebase_admin import credentials, firestore

from .models import LongURL, ShortURL

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


async def generate_short_code() -> str:
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(6))


async def generate_shorten_url(base_url: str, long_url: LongURL) -> ShortURL:
    query = db.collection("urls").where("long_url", "==", long_url.url).limit(1).get()

    if len(query) == 0:
        short_code = await generate_short_code()
        db.collection("urls").document(short_code).set({"long_url": long_url.url})

    else:
        short_code = query[0].id

    return ShortURL(url=f"{base_url}{short_code}")


async def fetch_redirect_url(short_code: str) -> LongURL:
    doc = db.collection("urls").document(short_code).get()
    if doc.exists:
        long_url = doc.to_dict()["long_url"]
        return LongURL(url=long_url)

    raise KeyError("URL not found")
