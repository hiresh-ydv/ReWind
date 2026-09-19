import yt_dlp
import json

def get_playlist_video_ids(playlist_url: str):
    """
    Playlist URL se saare video_id + title ki list nikalta hai.
    extract_flat=True matlab: sirf metadata chahiye, actual video download nahi karna.
    """
    ydl_opts = {
        'extract_flat': True,   # download nahi, sirf list chahiye
        'quiet': True,          # console pe extra logs mat dikhao
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)

        if 'entries' in info:  # playlist
            videos = [{"video_id": e['id'], "title": e['title']} for e in info['entries']]
        else:  # single video
            videos = [{"video_id": info['id'], "title": info['title']}]

    return videos


if __name__ == "__main__":
    playlist_url = "https://youtube.com/playlist?list=PLW4OpyGE0RdY&si=29cafdQzShDRZB57"
    videos = get_playlist_video_ids(playlist_url)

    print(f"Found {len(videos)} videos")

    # Save to disk — next steps isko reuse karenge, dobara playlist scan nahi karna padega
    with open("data/videos.json", "w") as f:
        json.dump(videos, f, indent=2)