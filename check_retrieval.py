# check_retrieval.py
from app.rag.ingest import get_vectorstore

vectorstore = get_vectorstore()
results = vectorstore.similarity_search("What documents are required for admission?", k=3)

for i, doc in enumerate(results, 1):
    print(f"\n--- Result {i} ---")
    print(f"Source: {doc.metadata.get('source_file')}")
    print(f"Page: {doc.metadata.get('page_number')}")
    print(f"Text: {doc.page_content[:300]}")