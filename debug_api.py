import youtube_transcript_api
from youtube_transcript_api import YouTubeTranscriptApi

print(f"Version: {youtube_transcript_api.__version__ if hasattr(youtube_transcript_api, '__version__') else 'Unknown'}")
print(f"File: {youtube_transcript_api.__file__}")

try:
    # Just check if method exists
    if hasattr(YouTubeTranscriptApi, 'get_transcript'):
        print("SUCCESS: get_transcript method exists.")
    else:
        print("FAILURE: get_transcript method MISSING.")
except Exception as e:
    print(f"Error: {e}")
