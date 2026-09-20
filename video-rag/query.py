import os
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

print("Loading embedding model...")
model = SentenceTransformer("intfloat/multilingual-e5-base")

client = chromadb.PersistentClient(path="data/chroma_db")
collection = client.get_or_create_collection(name="course_chunks")

groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])


def translate_to_devanagari(query: str):
    """
    User ki Hinglish/English query ko Devanagari script me convert karta hai,
    taaki course transcripts (jo Devanagari me hain) ke saath better match ho.
    """
    prompt = f"""Convert the following text into Hindi written in Devanagari script. 
Keep English technical/tech words as they are commonly spoken in Hindi speech (transliterate them into Devanagari too, don't translate technical terms into pure Hindi).
Only output the converted text, nothing else, no explanation.

Text: {query}"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


def search(query: str, top_k=5):
    """
    User ki query ko Devanagari me translate karke, e5 prefix add karke,
    embed karke ChromaDB me similarity search karta hai.
    """
    devanagari_query = translate_to_devanagari(query)
    

    # e5 models ko query ke aage "query: " prefix chahiye hota hai
    query_embedding = model.encode([f"query: {devanagari_query}"]).tolist()

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
    context = "\n\n".join(
        f"[Video: {m['video_title']}, Timestamp: {int(m['start_time'])}s]\n{m['text']}"
        for m in matches
    )

    prompt = f"""Tumhe course transcripts ke chunks diye gaye hain neeche (yeh Devanagari script me ho sakte hain). 
SIRF inhi chunks ke base pe user ke sawal ka jawab do.

Zaroori rules:
- Apna jawab HINGLISH me do — matlab Roman/English alphabet me likho (jaise "temperature kya hota hai"), Devanagari script (हिंदी) BILKUL use mat karo, chahe context Devanagari me ho.
- Sirf diye gaye context se answer karo, apni bahar ki knowledge use mat karo.
- Agar context me answer nahi hai, saaf keh do: "Yeh topic diye gaye course videos me cover nahi mila."
- Jawab clear aur concise rakho, aur bata do kaunse video/timestamp se aaya.

Context:
{context}

Sawal: {query}

Jawab (Roman script/Hinglish me, no Devanagari):"""

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