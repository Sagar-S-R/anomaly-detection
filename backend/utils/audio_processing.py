import whisper
from moviepy import VideoFileClip
from pydub import AudioSegment
import os
import pyaudio
import wave
import time
from collections import deque
from threading import Thread
from tempfile import NamedTemporaryFile

whisper_tiny = whisper.load_model("tiny")
whisper_large = whisper.load_model("tiny")

def cleanup_temp_audio_files():
    """Clean up old temporary audio files"""
    try:
        temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp_audio')
        if os.path.exists(temp_dir):
            for filename in os.listdir(temp_dir):
                if filename.endswith('.wav'):
                    file_path = os.path.join(temp_dir, filename)
                    try:
                        os.remove(file_path)
                        print(f"Cleaned up old audio file: {filename}")
                    except:
                        pass
    except Exception as e:
        print(f"Error cleaning up temp audio files: {e}")

# Clean up any existing temp files on startup
cleanup_temp_audio_files()

class AudioStream:
    def __init__(self):
        try:
            self.p = pyaudio.PyAudio()
            self.chunk = 1024
            self.format = pyaudio.paInt16
            self.channels = 1
            self.rate = 16000  # Whisper compatible
            self.stream = None
            self.buffer = deque(maxlen=16)  # Reduced from 32 to 16 for faster filling (~1 sec)
            self.running = False
            print("AudioStream initialized successfully")
        except Exception as e:
            print(f"AudioStream initialization error: {e}")
            self.p = None

    def start(self):
        if not self.p:
            print("PyAudio not available, skipping audio")
            return
            
        try:
            print("Starting audio stream...")
            self.stream = self.p.open(
                format=self.format, 
                channels=self.channels, 
                rate=self.rate, 
                input=True, 
                frames_per_buffer=self.chunk
            )
            self.running = True
            Thread(target=self._capture).start()
            print("Audio stream started successfully")
        except Exception as e:
            print(f"Audio stream start error: {e}")
            self.running = False

    def _capture(self):
        print("Audio capture thread started")
        chunk_count = 0
        while self.running:
            try:
                if self.stream and self.stream.is_active():
                    data = self.stream.read(self.chunk, exception_on_overflow=False)
                    self.buffer.append(data)
                    chunk_count += 1
                    # Removed annoying log spam
                else:
                    print("Audio stream not active")
                    break
            except Exception as e:
                print(f"Audio capture error: {e}")
                break
        print("Audio capture thread ended")

    def get_chunk(self):
        """Get audio chunk with non-blocking approach and timeout handling"""
        if not self.running:
            return None
            
        # Be more lenient - allow processing with fewer chunks
        min_chunks = max(4, self.buffer.maxlen // 4)  # At least 4 chunks or quarter buffer
        if len(self.buffer) < min_chunks:
            return None
            
        try:
            # Use available buffer data
            available_chunks = list(self.buffer)
            audio_bytes = b''.join(available_chunks)
            
            # Create temp directory if it doesn't exist
            temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp_audio')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Create temp file in the temp_audio directory
            temp_path = os.path.join(temp_dir, f"audio_{int(time.time() * 1000)}.wav")
            
            # Write audio file with proper error handling
            with wave.open(temp_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.p.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(audio_bytes)
            
            # Verify file exists and has content before returning
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 44:  # WAV header is 44 bytes
                return temp_path
            else:
                return None
        except Exception as e:
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
    """Transcribe audio with timeout and robust error handling"""
    if not audio_path:
        print("🎤 No audio path provided")
        return []
        
    if not os.path.exists(audio_path):
        print(f"🎤 Audio file not found: {audio_path}")
        return []
        
    try:
        file_size = os.path.getsize(audio_path)
        # Only log significant audio events, not every chunk
        if file_size < 1000:
            # Clean up small file
            try:
                os.remove(audio_path)
            except:
                pass
            return []
        
        # Use threading timeout for Windows compatibility
        import threading
        import queue
        
        result_queue = queue.Queue()
        
        def transcribe_with_timeout():
            try:
                result = whisper_tiny.transcribe(audio_path, fp16=False)
                result_queue.put(("success", result))
            except Exception as e:
                result_queue.put(("error", str(e)))
        
        # Start transcription in a separate thread
        transcription_thread = threading.Thread(target=transcribe_with_timeout)
        transcription_thread.daemon = True
        transcription_thread.start()
        
        try:
            # Wait for result with 1-second timeout (reduced from 3)
            result_type, result_data = result_queue.get(timeout=1.0)
            
            if result_type == "error":
                return []
            
            text = result_data["text"].strip()
            if text:
                print(f"🎤 Audio detected: '{text}'")  # Only log when we actually get text
                return [text]
            else:
                return []
                
        except queue.Empty:
            return []
        
    except Exception as e:
        print(f"🎤 Transcription error: {e}")
        return []
    finally:
        # Always clean up file
        try:
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception as cleanup_error:
            pass

def transcribe_large(audio_path):
    # Enhanced version with better error handling
    if not audio_path:
        print("No audio path provided for large transcription")
        return ""
        
    if not os.path.exists(audio_path):
        print(f"Audio file not found for large transcription: {audio_path}")
        return ""
        
    try:
        file_size = os.path.getsize(audio_path)
        if file_size <= 44:  # WAV header size
            print(f"Audio file too small for large transcription ({file_size} bytes): {audio_path}")
            return ""
        
        print(f"Large transcribing audio file: {audio_path} ({file_size} bytes)")
        
        result = whisper_large.transcribe(audio_path, fp16=False)
        text = result["text"].strip()
        
        print(f"Large transcription result: '{text}'")
        
        # Clean up file
        try:
            os.remove(audio_path)
            print(f"Cleaned up large audio file: {audio_path}")
        except Exception as cleanup_error:
            print(f"Warning: Could not delete {audio_path}: {cleanup_error}")
        
        return text
    except Exception as e:
        print(f"Large transcription error: {e}")
        # Clean up file on error
        try:
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
                print(f"Cleaned up failed large audio file: {audio_path}")
        except:
            pass
        return ""

# AudioCapture alias for compatibility
AudioCapture = AudioStream

class MockAudio:
    """Mock audio class for testing when audio is unavailable"""
    def __init__(self):
        self.running = False
        print("MockAudio initialized for testing")
    
    def start(self):
        self.running = True
        print("MockAudio started")
        
    def get_chunk(self):
        """Mock method that returns None - no audio data"""
        return None
    
    def stop(self):
        self.running = False
        print("MockAudio stopped")