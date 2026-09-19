import json
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


def get_transcript(video_id: str):
    try:
        ytt_api = YouTubeTranscriptApi()
        # Pehle Hindi try karo, nahi mili toh English try karo
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
        print(f"⚠️  Error on {video_id}: {e}")
        return None


if __name__ == "__main__":
    # Step 1 ka output load karo
    with open("data/videos.json") as f:
        videos = json.load(f)

    all_transcripts = {}

    for v in videos:
        video_id = v["video_id"]
        print(f"Fetching: {v['title']} ({video_id})")
        segments = get_transcript(video_id)
        if segments:
            all_transcripts[video_id] = {
                "title": v["title"],
                "segments": segments
            }

    # Sabka result ek hi file me save karo
    with open("data/transcripts.json", "w") as f:
        json.dump(all_transcripts, f, indent=2)

    print(f"\nDone. Got transcripts for {len(all_transcripts)}/{len(videos)} videos.")