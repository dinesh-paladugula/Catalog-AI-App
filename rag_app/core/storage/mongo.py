from pymongo import MongoClient
import certifi

from rag_app.core.config import MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION

def get_collection():
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI is not set")

    client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
    return client[MONGODB_DB][MONGODB_COLLECTION]
