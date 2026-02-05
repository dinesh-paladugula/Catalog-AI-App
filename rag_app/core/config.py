import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION","chunks")

TESSERACT_CMD = os.getenv("TESSERACT_CMD") 

HUGGINGFACE_EMBED_MODEL = os.getenv("HUGGINGFACE_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

IMAGE_OUT_DIR = os.getenv("IMAGE_OUT_DIR", "storage/images")