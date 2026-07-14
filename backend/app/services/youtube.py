"""YouTube transcript fetch for video chat."""
import re
from youtube_transcript_api import YouTubeTranscriptApi


def video_id(url: str) -> str:
    m = re.search(r"(?:v=|youtu\.be/|shorts/)([\w-]{11})", url)
    if not m:
        raise ValueError("Could not parse YouTube video id")
    return m.group(1)


def get_transcript(url: str) -> str:
    vid = video_id(url)
    entries = YouTubeTranscriptApi.get_transcript(vid)
    return " ".join(e["text"] for e in entries)
