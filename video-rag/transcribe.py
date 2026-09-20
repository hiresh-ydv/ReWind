import json
import os
import time
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


def get_transcript(video_id: str, retries=2):
    """
    Ek video_id se transcript (text + start + duration) nikalta hai.
    Hindi pehle try karta hai, nahi mili toh English.
    Rate-limit/block error pe retry karta hai with backoff.
    """
    for attempt in range(retries + 1):
        try:
            ytt_api = YouTubeTranscriptApi()
            transcript = ytt_api.fetch(video_id, languages=['hi', 'en'])
            segments = [
                {"text": s.text, "start": s.start, "duration": s.duration}
                for s in transcript
            ]
            return segments
        except (TranscriptsDisabled, NoTranscriptFound):
            print(f"⚠️  No captions for {video_id}, skipping")
            return None
        except Exception as e:
            if attempt < retries:
                wait = 20 * (attempt + 1)
                print(f"⚠️  Error on {video_id}, retrying in {wait}s...")
                time.sleep(wait)
            else:
                print(f"⚠️  Failed on {video_id} after retries: {e}")
                return None


if __name__ == "__main__":
    with open("data/videos.json") as f:
        videos = json.load(f)

    # Pehle se maujood transcripts load karo (resume support — dobara se sab fetch nahi karna)
    all_transcripts = {}
    if os.path.exists("data/transcripts.json"):
        with open("data/transcripts.json", encoding="utf-8") as f:
            all_transcripts = json.load(f)

    for v in videos:
        video_id = v["video_id"]

        if video_id in all_transcripts:
            print(f"Already have: {v['title']}, skipping")
            continue

        print(f"Fetching: {v['title']} ({video_id})")
        segments = get_transcript(video_id)
        if segments:
            all_transcripts[video_id] = {
                "title": v["title"],
                "segments": segments,
            }

        time.sleep(3)  # har request ke beech thoda ruko, rate-limit se bacho

        # progress ko turant save karo — beech me crash/block ho toh sab dobara na karna pade
        with open("data/transcripts.json", "w", encoding="utf-8") as f:
            json.dump(all_transcripts, f, indent=2, ensure_ascii=False)

    print(f"\nDone. Got transcripts for {len(all_transcripts)}/{len(videos)} videos.")