from pymongo import MongoClient
from rag_app.core.config import MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION

def get_collection():
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI is not set")
    client = MongoClient(MONGODB_URI)
    return client[MONGODB_DB][MONGODB_COLLECTION]