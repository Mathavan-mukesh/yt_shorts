from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from app.transcriber import TamilTranscriber
from app.gemini_agent import run_gemini_analysis
from app.cutter import cut_shorts
from dotenv import load_dotenv
import os
import shutil
import traceback

# Load environment variables
load_dotenv()

app = FastAPI(title="YT Tamil Shorts Generator", description="Extracts meaningful Shorts from Tamil YouTube videos.")

# Request body schema
class YouTubeRequest(BaseModel):
    youtube_url: str

@app.get("/")
def root():
    return {"message": "YT Tamil Shorts App is Live ✅"}

# ▶️ Route 1: YouTube URL processing
@app.post("/process/")
def process_video(req: YouTubeRequest):
    youtube_url = req.youtube_url
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise HTTPException(status_code=500, detail="Missing GOOGLE_API_KEY in .env file.")

    try:
        clean_temp_files()

        # Step 1: Transcribe
        transcriber = TamilTranscriber(youtube_url, chunk_duration=1)
        transcriber.run_all()

        # Ensure video was downloaded
        if not os.path.exists("full_video.mp4"):
            raise Exception("full_video.mp4 not found after download.")

        # Step 2: Gemini Analysis
        run_gemini_analysis(api_key, "junk_transcript.json")

        # Step 3: Cut Shorts
        cut_shorts("full_video.mp4", "youtube_shorts.json", output_dir="shorts_output")

        return response_success()

    except Exception as e:
        traceback.print_exc()  # Print full error in terminal
        raise HTTPException(status_code=500, detail=f"❌ Error: {str(e)}")

# ▶️ Route 2: Local file upload processing
@app.post("/process_local/")
async def process_local_video(file: UploadFile = File(...)):
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise HTTPException(status_code=500, detail="Missing GOOGLE_API_KEY in .env file.")

    try:
        clean_temp_files()

        # Save uploaded video file
        local_path = "full_video.mp4"
        with open(local_path, "wb") as f:
            f.write(await file.read())

        if not os.path.exists(local_path):
            raise Exception("Uploaded video not saved correctly.")

        # Transcribe from local file
        transcriber = TamilTranscriber(local_path, chunk_duration=1)
        transcriber.run_local()
        transcriber.load_audio()
        transcriber.transcribe()
    

        # Gemini + Shorts
        run_gemini_analysis(api_key, "junk_transcript.json")
        cut_shorts("full_video.mp4", "youtube_shorts.json", output_dir="shorts_output")

        return response_success()

    except Exception as e:
        traceback.print_exc()  # Print full error in terminal
        raise HTTPException(status_code=500, detail=f"❌ Error: {str(e)}")

# ✅ Helper: Cleanup function
def clean_temp_files():
    for file in ["full_video.mp4", "downloaded_audio.mp3", "junk_transcript.json", "youtube_shorts.json"]:
        if os.path.exists(file):
            os.remove(file)
    if os.path.exists("shorts_output"):
        shutil.rmtree("shorts_output")

# ✅ Helper: Success response
def response_success():
    return {
        "status": "✅ Completed all steps successfully!",
        "transcript": "junk_transcript.json",
        "shorts_file": "youtube_shorts.json",
        "shorts_output_dir": "shorts_output/"
    }
