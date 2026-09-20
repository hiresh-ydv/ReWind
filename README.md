# Rewind — Course Video RAG

Ask a question, get pointed to the exact moment in your course videos where it's covered — no more scrubbing through hours of lecture recordings to find that one explanation.

Built to revise a YouTube AI Engineer course without notes: type a topic, get an answer generated from what the instructor actually said, plus a jump-to-timestamp link into the source video.

## How it works

```
Playlist URL
   │
   ▼
[1] Ingest ──────────  yt-dlp lists all video IDs + titles
   │
   ▼
[2] Transcribe ──────  youtube-transcript-api pulls auto-generated
   │                    captions (Hindi + English) with timestamps
   ▼
[3] Chunk ───────────  merge small caption segments into ~40s
   │                    chunks, keeping each chunk's start_time
   ▼
[4] Embed + Store ───  multilingual-e5-base embeddings → ChromaDB
   │
   ▼
[5] Query ───────────  user question → translated to Devanagari
   │                    for better retrieval → top-k chunks →
   │                    Groq LLM answers using only that context
   ▼
[6] Serve ───────────  FastAPI backend + web UI with an embedded
                        YouTube player that jumps to the timestamp
```

## Why these choices

- **Captions over Whisper** — the course videos already have YouTube auto-captions, so pulling those directly is free and instant; no audio download or transcription compute needed.
- **Multilingual e5 embeddings** — the course is spoken Hindi with English technical terms transliterated into Devanagari (e.g. "टेंपरेचर" for *temperature*). A general-purpose multilingual model under-performed on this code-mixed content; `intfloat/multilingual-e5-base` (a retrieval-tuned model) handles it noticeably better.
- **Query translation step** — user questions typed in Hinglish/English are translated to Devanagari before embedding, since that matches the script the transcripts are actually stored in, which improved retrieval accuracy further.
- **ChromaDB** — zero-setup, file-based persistence, no separate server to run. Right fit for this scale (~1,000 chunks); a production version could swap in Qdrant with minimal code changes.
- **Groq (Llama / gpt-oss-120b)** — fast inference, and the prompt constrains answers strictly to retrieved context so the tool doesn't fill gaps with outside knowledge.

## Tech stack

| Layer | Tool |
|---|---|
| Playlist / caption fetch | `yt-dlp`, `youtube-transcript-api` |
| Embeddings | `sentence-transformers` (`intfloat/multilingual-e5-base`) |
| Vector store | `ChromaDB` |
| LLM | Groq API |
| Backend | FastAPI |
| Frontend | Vanilla HTML/CSS/JS |
| Env/package management | `uv` |

## Project structure

```
video-rag/
├── ingest.py          # playlist → video IDs
├── transcribe.py       # captions with timestamps (resumable)
├── chunk.py            # merge segments into timestamped chunks
├── embed_store.py       # embed chunks, store in ChromaDB
├── query.py            # search + LLM answer generation
├── app.py               # FastAPI server
├── static/
│   └── index.html        # search UI + video player
└── data/                 # transcripts, chunks, chroma_db (gitignored)
```

## Setup

```bash
uv sync
```

Add a `.env` file:
```
GROQ_API_KEY=your_key_here
```

Run the pipeline once (each step's output feeds the next):
```bash
uv run ingest.py
uv run transcribe.py
uv run chunk.py
uv run embed_store.py
```

Start the app:
```bash
uv run uvicorn app:app --reload
```

Open `http://127.0.0.1:8000`.

## Known limitations

- 21/30 videos are indexed for the current course (a few hit YouTube's rate-limiting mid-fetch); `transcribe.py` resumes automatically and skips already-fetched videos on re-run.
- Retrieval quality depends on caption accuracy — auto-generated captions occasionally misrecognize spoken words.
