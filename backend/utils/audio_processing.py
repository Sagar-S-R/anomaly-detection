import whisper
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import os
import pyaudio
import wave
import time
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
        try:
            self.stream = self.p.open(format=self.format, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk)
            self.running = True
            Thread(target=self._capture).start()
        except Exception as e:
            print(f"Audio stream start error: {e}")
            self.running = False

    def _capture(self):
        while self.running:
            try:
                data = self.stream.read(self.chunk)
                self.buffer.append(data)
            except Exception as e:
                print(f"Audio capture error: {e}")
                break

    def get_chunk(self):
        if len(self.buffer) < self.buffer.maxlen:
            return None
<<<<<<< HEAD
        
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
=======
        try:
            # Concatenate buffer to audio bytes
            audio_bytes = b''.join(self.buffer)
            with NamedTemporaryFile(delete=False, suffix=".wav", prefix="audio_") as temp_audio:
                temp_path = temp_audio.name
            
            # Write audio file with proper error handling
            wf = wave.open(temp_path, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(audio_bytes)
            wf.close()
            
            # Small delay to ensure file is fully written
            time.sleep(0.01)
            
            # Verify file exists and has content before returning
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 44:  # WAV header is 44 bytes
                return temp_path
            else:
                print(f"Audio file creation failed: {temp_path}")
                return None
        except Exception as e:
            print(f"Audio processing error: {e}")
>>>>>>> bab5fe86a117a6a2f2f34b20ac47abe0d4c53b3f
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
<<<<<<< HEAD
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
=======
    # Simplified version that works directly with WAV files
    if not audio_path:
        return []
    try:
        # Verify file exists and has content
        if not os.path.exists(audio_path):
            print(f"Audio file not found: {audio_path}")
            return []
        if os.path.getsize(audio_path) == 0:
            print(f"Audio file is empty: {audio_path}")
            return []
        
        # Try direct transcription without chunking for WAV files
        result = whisper_tiny.transcribe(audio_path, fp16=False)
        transcript = result["text"].strip()
        
        # Clean up file
        try:
            os.remove(audio_path)
        except:
            pass
            
        return [transcript] if transcript else []
        
    except Exception as e:
        print(f"Audio transcription error: {e}")
        # Clean up on error
        try:
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
        except:
            pass
        return []
>>>>>>> bab5fe86a117a6a2f2f34b20ac47abe0d4c53b3f

def transcribe_large(audio_path):
    # Existing
    if not audio_path or not os.path.exists(audio_path):
        return ""
<<<<<<< HEAD
    
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
=======
    try:
        # Verify file exists and has content
        if not os.path.exists(audio_path):
            return ""
        if os.path.getsize(audio_path) == 0:
            return ""
        
        result = whisper_large.transcribe(audio_path, fp16=False)
        text = result["text"].strip()
        
        # Clean up file
        try:
            os.remove(audio_path)
        except:
            pass  # File might already be deleted
        
        return text
    except Exception as e:
        print(f"Transcription error: {e}")
        # Clean up file on error
        try:
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
        except:
            pass
>>>>>>> bab5fe86a117a6a2f2f34b20ac47abe0d4c53b3f
        return ""