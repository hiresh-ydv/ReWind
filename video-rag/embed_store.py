import json
import chromadb
from sentence_transformers import SentenceTransformer


def load_chunks():
    with open("data/chunks.json", encoding="utf-8") as f:
        return json.load(f)


def build_vector_store():
    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks")

    # Multilingual model — Hindi + English dono handle karega
    print("Loading embedding model...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    # ChromaDB client — disk pe persist hoga (data/chroma_db folder me)
    client = chromadb.PersistentClient(path="data/chroma_db")
    collection = client.get_or_create_collection(name="course_chunks")

    texts = [c["text"] for c in chunks]
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "video_id": c["video_id"],
            "video_title": c["video_title"],
            "start_time": c["start_time"],
            "end_time": c["end_time"],
        }
        for c in chunks
    ]

    print("Generating embeddings (batch)...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32).tolist()

    print("Storing in ChromaDB...")
    # Chroma ek limit rakhta hai per-batch insert pe, isliye chunks me daalte hain
    batch_size = 500
    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i:i+batch_size],
            embeddings=embeddings[i:i+batch_size],
            documents=texts[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
        )

    print(f"\nDone. {collection.count()} chunks stored in ChromaDB.")


if __name__ == "__main__":
    build_vector_store()