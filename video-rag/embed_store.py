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
    model = SentenceTransformer("intfloat/multilingual-e5-base")

    # ChromaDB client — disk pe persist hoga (data/chroma_db folder me)
    client = chromadb.PersistentClient(path="data/chroma_db")
    collection = client.get_or_create_collection(name="course_chunks")

    # embedding ke liye "passage: " prefix chahiye (e5 model requirement)
    texts_for_embedding = [f"passage: {c['text']}" for c in chunks]
    # storage/display/LLM ke liye clean text (bina prefix ke)
    texts_for_storage = [c["text"] for c in chunks]

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
    embeddings = model.encode(texts_for_embedding)