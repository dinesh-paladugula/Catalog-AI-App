from rag_app.core.storage.mongo import get_collection

col = get_collection()
print(col.database.name, col.name)
print(col.count_documents({}))
