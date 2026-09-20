from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from query import search, ask_llm

app = FastAPI(title="Video RAG API")

# Frontend alag origin se chal sakta hai (ya same server se bhi) — CORS allow kar rahe hain safety ke liye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str


@app.post("/search")
def search_endpoint(req: QueryRequest):
    """
    User ki query leta hai, matching video segments + LLM answer return karta hai.
    """
    matches = search(req.query, top_k=5)
    answer = ask_llm(req.query, matches)

    return {
        "answer": answer,
        "matches": matches,
    }


# Frontend static files serve karne ke liye (index.html waghera)
app.mount("/", StaticFiles(directory="static", html=True), name="static")