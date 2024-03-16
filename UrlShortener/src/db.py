from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.base_query import FieldFilter

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
url_collection = db.collection("urls_map")


def remove_expired_urls() -> None:
    query = url_collection.where(
        filter=FieldFilter("expiration", "<", datetime.now())
    ).get()
    for doc in query:
        doc.reference.delete()


def search_doc_by_code(short_code: str) -> DocumentSnapshot:
    doc = url_collection.document(short_code).get()
    if not doc.exists:
        raise KeyError(f"{short_code} not found in urls_map collection")
    return doc


def search_doc_by_long_url(long_url: str) -> DocumentSnapshot:
    query = (
        url_collection.where(filter=FieldFilter("long_url", "==", long_url))
        .limit(1)
        .get()
    )
    if len(query) == 0:
        raise KeyError(f"{long_url} not found in urls_map collection")
    return query[0]


def update_doc_by_code(doc_id: str, data: dict) -> None:
    url_collection.document(doc_id).update(data)


def save_doc(doc_id: str, data: dict) -> None:
    url_collection.document(doc_id).set(data)
