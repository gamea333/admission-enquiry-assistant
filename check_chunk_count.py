# check_chunk_count.py
from app.rag.ingest import get_vectorstore

vectorstore = get_vectorstore()
print("Total chunks in vector store:", vectorstore._collection.count())