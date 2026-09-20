import os
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Ek hi baar load karo — baar baar model load karna slow hota
print("Loading embedding model...")
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

client = chromadb.PersistentClient(path="data/chroma_db")
collection = client.get_or_create_collection(name="course_chunks")

groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])


def search(query: str, top_k=5):
    """
    User ki query embed karke ChromaDB me similarity search karta hai.
    Top-k matching chunks (text + metadata) return karta hai.
    """
    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
    )

    matches = []
    for i in range(len(results["ids"][0])):
        matches.append({
            "text": results["documents"][0][i],
            "video_id": results["metadatas"][0][i]["video_id"],
            "video_title": results["metadatas"][0][i]["video_title"],
            "start_time": results["metadatas"][0][i]["start_time"],
        })
    return matches


def ask_llm(query: str, matches: list):
    """
    Retrieved chunks ko context banakar Groq LLM se answer generate karwata hai.
    """
    context = "\n\n".join(
        f"[Video: {m['video_title']}, Timestamp: {int(m['start_time'])}s]\n{m['text']}"
        for m in matches
    )

    prompt = f"""Tumhe course transcripts ke chunks diye gaye hain neeche. Inhi ke base pe user ke sawal ka jawab do.
Jawab clear aur concise rakhna, aur bata dena kaunse video/timestamp se yeh info aayi hai.

Context:
{context}

Sawal: {query}

Jawab:"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    while True:
        query = input("\nApna sawal poocho (ya 'exit' likho): ")
        if query.lower() == "exit":
            break

        matches = search(query)

        print("\n--- Matching video segments ---")
        for m in matches:
            minutes = int(m["start_time"]) // 60
            seconds = int(m["start_time"]) % 60
            print(f"📹 {m['video_title']} — {minutes}:{seconds:02d} → https://youtu.be/{m['video_id']}?t={int(m['start_time'])}")

        print("\n--- LLM Answer ---")
        answer = ask_llm(query, matches)
        print(answer)