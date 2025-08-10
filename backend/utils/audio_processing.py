import whisper
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import os
import pyaudio
import wave
from collections import deque
from threading import Thread
from tempfile import NamedTemporaryFile

whisper_tiny = whisper.load_model("tiny")
whisper_large = whisper.load_model("large")

class AudioStream:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000  # Whisper compatible
        self.stream = None
        self.buffer = deque(maxlen=32)  # ~2 sec at 1024 chunk (32 chunks ~2 sec)
        self.running = False

    def start(self):
        self.stream = self.p.open(format=self.format, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk)
        self.running = True
        Thread(target=self._capture).start()

    def _capture(self):
        while self.running:
            data = self.stream.read(self.chunk)
            self.buffer.append(data)

    def get_chunk(self):
        if len(self.buffer) < self.buffer.maxlen:
            return None
        
        try:
            # Concatenate buffer to audio bytes
            audio_bytes = b''.join(self.buffer)
            with NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                wf = wave.open(temp_audio.name, 'wb')
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.p.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(audio_bytes)
                wf.close()
                return temp_audio.name
        except Exception as e:
            print(f"Error creating audio chunk: {e}")
            return None

    def stop(self):
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

def extract_audio(video_path):
    # Existing batch function
    audio_path = "temp_audio.mp3"
    video_clip = VideoFileClip(video_path)
    if video_clip.audio:
        video_clip.audio.write_audiofile(audio_path)
        return audio_path
    return None

def chunk_and_transcribe_tiny(audio_path):
    # Existing
    if not audio_path or not os.path.exists(audio_path):
        return []
    
    try:
        audio = AudioSegment.from_file(audio_path)
        chunk_length_ms = 2000
        audio_chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
        transcripts = []
        for idx, chunk in enumerate(audio_chunks):
            chunk_path = f"chunk_{idx}.wav"
            try:
                chunk.export(chunk_path, format="wav")
                result = whisper_tiny.transcribe(chunk_path, fp16=False)
                transcripts.append(result["text"].strip())
                if os.path.exists(chunk_path):
                    os.remove(chunk_path)
            except Exception as e:
                print(f"Error processing audio chunk {idx}: {e}")
                continue
        
        # Clean up main audio file
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception as e:
            print(f"Error removing audio file: {e}")
            
        return transcripts
    except Exception as e:
        print(f"Error in chunk_and_transcribe_tiny: {e}")
        return []

def transcribe_large(audio_path):
    # Existing
    if not audio_path or not os.path.exists(audio_path):
        return ""
    
    try:
        result = whisper_large.transcribe(audio_path, fp16=False)
        text = result["text"].strip()
        
        # Clean up audio file
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception as e:
            print(f"Error removing audio file: {e}")
            
        return text
    except Exception as e:
        print(f"Error in transcribe_large: {e}")
        return ""