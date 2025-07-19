import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import HTTPException
from datetime import timedelta

# === Load transcription ===
def load_transcription(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

# === Format transcript text ===
def format_transcription_lines(data):
    return "\n".join(
        f"[{item['start_time']} - {item['end_time']}] {item['text']}" for item in data
    )

# === Remove trailing commas ===
def clean_trailing_commas(json_str):
    return re.sub(r",\s*(\]|\})", r"\1", json_str).strip()

# === Helper: Convert "HH:MM:SS" to seconds ===
def hms_to_seconds(hms):
    try:
        t = list(map(int, hms.split(":")))
        return timedelta(hours=t[0], minutes=t[1], seconds=t[2]).total_seconds()
    except:
        return 0

# === Build Gemini Prompt ===
def build_prompt(transcript_text):
    return f"""
You are given a 1-second chunked Tamil video transcript.

🎯 TASK:
Find potential **Shorts** (highlight segments) that are:
- Emotionally powerful
- Spiritually or philosophically deep
- Thematically strong

🧠 STRICT RULES:
1. ✅ Each segment must be at least **45 seconds** and at most **180 seconds** in duration.
2. ❌ Do NOT return any segment outside that time range.
3. ✅ Merge nearby transcript lines into meaningful segments.
4. ❌ Do NOT include any segment where the speaker is **repeating the same phrase or idea without meaningful variation**.
5. ❌ No timestamp quoting or markdown. Return **pure JSON only**.

📦 JSON Format (strict):
[
  {{
    "start_time": "HH:MM:SS",
    "end_time": "HH:MM:SS",
    "description": "Why this clip is powerful (in 1-2 lines)."
  }}
]

🎙️ Transcription:
{transcript_text}
"""

# === Main Gemini Logic ===
def run_gemini_analysis(api_key, transcript_json_path):
    transcription_data = load_transcription(transcript_json_path)
    transcript_text = format_transcription_lines(transcription_data)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-lite")

    print("🧠 Sending to Gemini...")
    response = model.generate_content(build_prompt(transcript_text))
    raw_text = response.text.strip()
    print("\n📄 Gemini Raw Output Preview:\n", raw_text[:1000], "\n--- END PREVIEW ---\n")

    # Remove any markdown formatting
    cleaned = re.sub(r"```json|```", "", raw_text, flags=re.IGNORECASE).strip()
    cleaned = clean_trailing_commas(cleaned)

    # Try parsing JSON
    try:
        shorts = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\[\s*{.*?}\s*]", cleaned, re.DOTALL)
        if not match:
            raise HTTPException(status_code=500, detail="Gemini returned no JSON array.")
        try:
            shorts = json.loads(clean_trailing_commas(match.group()))
        except:
            raise HTTPException(status_code=500, detail="Gemini JSON parsing failed.")

    # ✅ Post-filter segments: 30s to 180s only
    filtered_shorts = []
    for i, item in enumerate(shorts):
        try:
            start_sec = hms_to_seconds(item["start_time"])
            end_sec = hms_to_seconds(item["end_time"])
            duration = end_sec - start_sec
            if 10 <= duration <= 180:
                item["short_number"] = len(filtered_shorts) + 1
                filtered_shorts.append(item)
        except:
            continue  # Skip malformed entries

    if not filtered_shorts:
        raise HTTPException(status_code=500, detail="No valid shorts found (must be 30–180s).")

    # Save valid shorts
    with open("youtube_shorts.json", "w", encoding="utf-8") as f:
        json.dump(filtered_shorts, f, indent=2, ensure_ascii=False)

    print("✅ Filtered & saved valid shorts to `youtube_shorts.json`")
    return filtered_shorts
