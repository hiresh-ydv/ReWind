import json
import os


def merge_into_chunks(segments, window=40):
    """
    Chhote caption segments ko merge karke ~window seconds ke bade chunks banata hai.
    start_time preserve rehta hai — taaki timestamp-jump ke liye use ho sake.
    """
    chunks = []
    current_text = ""
    chunk_start = None
    chunk_end = None

    for seg in segments:
        if chunk_start is None:
            chunk_start = seg["start"]  # naya chunk shuru — starting time note karo

        current_text += " " + seg["text"]
        chunk_end = seg["start"] + seg.get("duration", 0)

        # agar chunk itna bada ho gaya jitna window chahiye, toh save karke reset karo
        if chunk_end - chunk_start >= window:
            chunks.append({
                "text": current_text.strip(),
                "start_time": round(chunk_start, 2),
                "end_time": round(chunk_end, 2),
            })
            current_text = ""
            chunk_start = None

    # loop khatam hone ke baad agar kuch bacha hai (last partial chunk), usko bhi add karo
    if current_text.strip():
        chunks.append({
            "text": current_text.strip(),
            "start_time": round(chunk_start, 2),
            "end_time": round(chunk_end, 2),
        })

    return chunks


if __name__ == "__main__":
    with open("data/transcripts.json") as f:
        all_transcripts = json.load(f)

    all_chunks = []

    for video_id, data in all_transcripts.items():
        segments = data["segments"]
        title = data["title"]

        video_chunks = merge_into_chunks(segments, window=40)

        # har chunk me video_id aur title bhi daal do — baad me pata chalna chahiye kaunsa video hai
        for c in video_chunks:
            c["video_id"] = video_id
            c["video_title"] = title

        all_chunks.extend(video_chunks)
        print(f"{title}: {len(segments)} segments → {len(video_chunks)} chunks")

    os.makedirs("data", exist_ok=True)
    with open("data/chunks.json", "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"\nTotal chunks across all videos: {len(all_chunks)}")