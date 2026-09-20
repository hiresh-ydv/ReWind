import json

chunks = json.load(open("data/chunks.json", encoding="utf-8"))
video_chunks = [c for c in chunks if c["video_id"] == "aF0IK2sIQyY"]

print(f"Total chunks for this video: {len(video_chunks)}")
for c in video_chunks:
    print(f"[{c['start_time']}-{c['end_time']}s] {c['text'][:150]}")