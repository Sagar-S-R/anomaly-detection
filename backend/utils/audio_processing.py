import whisper
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import os

whisper_tiny = whisper.load_model("tiny")
whisper_large = whisper.load_model("large")

def extract_audio(video_path):
    audio_path = "temp_audio.mp3"
    video_clip = VideoFileClip(video_path)
    if video_clip.audio:
        video_clip.audio.write_audiofile(audio_path)
        return audio_path
    return None

def chunk_and_transcribe_tiny(audio_path):
    if not audio_path:
        return []
    audio = AudioSegment.from_file(audio_path)
    chunk_length_ms = 2000
    audio_chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
    transcripts = []
    for idx, chunk in enumerate(audio_chunks):
        chunk_path = f"chunk_{idx}.wav"
        chunk.export(chunk_path, format="wav")
        result = whisper_tiny.transcribe(chunk_path, fp16=False)
        transcripts.append(result["text"].strip())
        os.remove(chunk_path)
    os.remove(audio_path)
    return transcripts

def transcribe_large(audio_path):
    if not audio_path:
        return ""
    result = whisper_large.transcribe(audio_path, fp16=False)
    os.remove(audio_path)
    return result["text"].strip()