import os
import shutil

def time_to_seconds(t):
    h, m, s = map(int, t.strip().split(":"))
    return h * 3600 + m * 60 + s

def cleanup(paths=["full_video.mp4", "downloaded_audio.mp3", "junk_transcript.json", "youtube_shorts.json"], folders=["shorts_output"]):
    for path in paths:
        if os.path.exists(path):
            os.remove(path)
    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    os.makedirs("shorts_output", exist_ok=True)


