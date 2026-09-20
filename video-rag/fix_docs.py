import json
import chromadb

def fix_stored_documents():
    with open("data/chunks.json", encoding="utf-8") as f:
        chunks = json.load(f)

    client = chromadb.PersistentClient(path="data/chroma_db")
    collection = client.get_or_create_collection(name="course_chunks")

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    clean_texts = [c["text"] for c in chunks]  # bina "passage: " prefix ke

    batch_size = 500
    for i in range(0, len(ids), batch_size):
        collection.update(
            ids=ids[i:i+batch_size],
            documents=clean_texts[i:i+batch_size],
        )

    print("Documents updated, embeddings untouched.")

if __name__ == "__main__":
    fix_stored_documents()