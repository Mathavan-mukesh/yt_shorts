import os
import json
import datetime
import torch
import librosa
import yt_dlp
from moviepy.editor import VideoFileClip
from transformers import WhisperProcessor, WhisperForConditionalGeneration

class TamilTranscriber:
    def __init__(self, video_url, chunk_duration=1, model_name="openai/whisper-small"):
        self.video_url = video_url
        self.video_filename = "full_video.mp4"
        self.audio_path = "downloaded_audio.mp3"
        self.chunk_duration_sec = chunk_duration
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = WhisperProcessor.from_pretrained(self.model_name)
        self.model = WhisperForConditionalGeneration.from_pretrained(self.model_name).to(self.device)
        self.audio = None
        self.sr = 16000
        self.output = []

    def download_video_audio(self):
        # This is only for YouTube URL use case
        if not os.path.exists(self.video_filename):
            print("⬇️ Downloading video...")
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
                'outtmpl': self.video_filename,
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.video_url])
            print("✅ Downloaded:", self.video_filename)

        self.extract_audio_from_video()

    def extract_audio_from_video(self):
        print("🔊 Extracting audio from video...")
        clip = VideoFileClip(self.video_filename)
        clip.audio.write_audiofile(self.audio_path, verbose=False, logger=None)
        clip.close()
        print("✅ Extracted audio to:", self.audio_path)

    def load_audio(self):
        # Check if audio exists, otherwise extract it
        if not os.path.exists(self.audio_path):
            self.extract_audio_from_video()

        print("🎧 Loading audio...")
        self.audio, _ = librosa.load(self.audio_path, sr=self.sr)
        print("✅ Audio loaded.")

    def chunk_audio(self):
        chunk_size = self.chunk_duration_sec * self.sr
        return [self.audio[i:i + chunk_size] for i in range(0, len(self.audio), chunk_size)]

    def transcribe(self):
        print("🧠 Transcribing...")
        chunks = self.chunk_audio()
        for i, chunk in enumerate(chunks):
            inputs = self.processor(chunk, sampling_rate=self.sr, return_tensors="pt")
            input_features = inputs.input_features.to(self.device)

            start = i * self.chunk_duration_sec
            end = min((i + 1) * self.chunk_duration_sec, len(self.audio) // self.sr)

            forced_ids = self.processor.get_decoder_prompt_ids(language="ta", task="transcribe")
            predicted_ids = self.model.generate(input_features, forced_decoder_ids=forced_ids, max_new_tokens=32)
            tamil_text = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()

            self.output.append({
                "short_number": i + 1,
                "start_time": str(datetime.timedelta(seconds=int(start))),
                "end_time": str(datetime.timedelta(seconds=int(end))),
                "text": tamil_text
            })

            print(f"[{self.output[-1]['start_time']} - {self.output[-1]['end_time']}] {tamil_text}")

        print("💾 Saving to junk_transcript.json...")
        with open("junk_transcript.json", "w", encoding="utf-8") as f:
            json.dump(self.output, f, indent=2, ensure_ascii=False)
        print("✅ Transcription saved!")

    def run_all(self):
        self.download_video_audio()
        self.load_audio()
        self.transcribe()

    # New method for local files (you must call this explicitly in local upload route)
    def run_local(self):
        self.extract_audio_from_video()
        self.load_audio()
        self.transcribe()
