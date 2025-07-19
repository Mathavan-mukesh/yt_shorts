# 🎬 Tamil Shorts Generator

This project helps users automatically extract **emotionally resonant**, **meaningful**, and **thematically powerful** short video clips (YouTube Shorts) from Tamil videos.

Users can either upload a local `.mp4` file or provide a YouTube link. The system processes the video, analyzes its content using a Large Language Model (Gemini), and produces short clips based on deep understanding of the spoken content.

---

## ✨ Features

- 📥 **Input Source**:
  - Upload local MP4 files
  - Enter YouTube video URL

- 🔊 **Audio Chunking**:
  - Splits video audio into **1-second chunks**

- 🧠 **LLM-powered Meaning Detection**:
  - Uses **Google Gemini** to analyze Tamil transcriptions
  - Identifies segments that are:
    - Emotionally powerful
    - Spiritually or philosophically deep
    - Thematically strong or expressive

- ✂️ **Auto Shorts Cutter**:
  - Converts selected segments into short videos (MP4)
  - Cropped and resized to **1080x1920** (vertical)

- 💾 **Output**:
  - Generates `youtube_shorts.json` with descriptions and timestamps
  - Saves each short clip to `shorts_output/` folder

---

## ⚙️ How It Works

1. **User Uploads Video / Enters YouTube Link**
2. **Whisper Model** transcribes Tamil speech into text (chunked by 1s)
3. **Gemini LLM** analyzes each chunk to identify meaningful segments
4. Filtered segments (30–180 seconds) are saved to a JSON
5. **MoviePy** extracts each video segment as a high-resolution Short

---


