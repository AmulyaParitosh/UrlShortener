import random
import string

import firebase_admin
from firebase_admin import credentials, firestore
from pydantic import BaseModel

DOMAIN = "http://localhost:8000/"

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


class URL(BaseModel):
    long_url: str


async def generate_short_code():
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(6))


async def generate_shorten_url(url: str):
    short_code = await generate_short_code()
    db.collection("urls").document(short_code).set({"long_url": url})
    return f"{DOMAIN}{short_code}"


async def fetch_redirect_url(short_code: str):
    doc_ref = db.collection("urls").document(short_code)
    doc = doc_ref.get()
    if doc.exists:
        long_url = doc.to_dict()["long_url"]
        return long_url
    else:
        raise KeyError("URL not found")
