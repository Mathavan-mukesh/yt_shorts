import os
import json
from moviepy.editor import VideoFileClip
from app.utils import time_to_seconds

def cut_shorts(video_path="full_video.mp4", json_path="youtube_shorts.json", output_dir="shorts_output"):
    with open(json_path, "r", encoding="utf-8") as f:
        shorts = json.load(f)

    os.makedirs(output_dir, exist_ok=True)
    video = VideoFileClip(video_path)
    duration = video.duration

    for s in shorts:
        start = time_to_seconds(s["start_time"])
        end = time_to_seconds(s["end_time"])
        if start >= duration:
            continue
        if end > duration:
            end = duration

        filename = os.path.join(output_dir, f"short_{s['short_number']}.mp4")

        # ▶️ Extract subclip
        clip = video.subclip(start, end)

        # 📐 Resize to height 1920
        clip = clip.resize(height=1920)

        # 📌 Center crop width to 1080
        if clip.w > 1080:
            x_center = clip.w // 2
            clip = clip.crop(x_center=x_center, width=1080)
        elif clip.w < 1080:
            # Optionally: pad if width is less (you can skip this to leave black borders)
            clip = clip.resize(width=1080)

        # 💾 Save the clip
        clip.write_videofile(filename, codec="libx264", audio_codec="aac", fps=30, verbose=False, logger=None)

    video.close()
