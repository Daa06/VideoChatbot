import ffmpeg
from pathlib import Path
from transformers import pipeline
from config.config import ASR_MODEL_ID, DEVICE

class AudioProcessor:
    _instance = None
    _is_initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AudioProcessor, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._is_initialized:
            print("Initializing AudioProcessor and loading models...")
            # Initialize speech recognition
            self.asr = pipeline(
                "automatic-speech-recognition",
                model=ASR_MODEL_ID,
                device=0 if DEVICE=="cuda" else -1,
                return_timestamps='word'
            )
            print("Audio models loaded successfully!")
            self._is_initialized = True
    
    @property
    def is_ready(self):
        return self._is_initialized
    
    def process_audio(self, video_path: str) -> dict:
        """Process audio from video file and return transcription"""
        if not self._is_initialized:
            raise RuntimeError("AudioProcessor not properly initialized. Models not loaded.")
            
        print("Starting audio processing...")
        
        # Extract audio from video
        audio_path = self._extract_audio(video_path)
        
        # Process audio and generate transcription
        print("Transcribing audio...")
        audio_transcription = self._process_audio(audio_path)
        
        print("Audio processing complete!")
        return audio_transcription
    
    def _extract_audio(self, video_path: str, audio_path: str = "temp_audio.wav") -> str:
        """Extract audio from video file"""
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, ac=1, ar='16000')
            .overwrite_output()
            .run(quiet=True)
        )
        return audio_path
    
    def _process_audio(self, audio_path: str) -> dict:
        """Process audio and generate transcription with segments"""
        result = self.asr(audio_path)
        
        print(f"DEBUG: ASR raw result: {result}")
        
        if not result:
            return {"text": "", "words": [], "segments": []}
        
        # The ASR model returns 'chunks' when using return_timestamps='word'
        text = result.get("text", "")
        chunks = result.get("chunks", [])
        
        # Convert chunks to words format for consistency
        words = []
        for chunk in chunks:
            if isinstance(chunk, dict) and "text" in chunk and "timestamp" in chunk:
                words.append({
                    "text": chunk["text"],
                    "start": chunk["timestamp"][0] if isinstance(chunk["timestamp"], tuple) else chunk["timestamp"],
                    "end": chunk["timestamp"][1] if isinstance(chunk["timestamp"], tuple) and len(chunk["timestamp"]) > 1 else chunk["timestamp"]
                })
        
        # Create segments based on speech breaks
        segments = self._create_audio_segments(words)
        
        print(f"DEBUG: Processed audio - text: '{text[:100]}...', words count: {len(words)}, segments count: {len(segments)}")
        
        # Format the result
        return {
            "text": text,
            "words": words,
            "segments": segments
        }
    
    def _create_audio_segments(self, words: list) -> list:
        """Create audio segments based on natural speech breaks"""
        if not words:
            return []
        
        segments = []
        current_segment_words = []
        
        for i, word in enumerate(words):
            current_segment_words.append(word)
            
            # Check if this is the end of a segment
            is_end_of_segment = False
            
            # End of segment if:
            # 1. It's the last word
            if i == len(words) - 1:
                is_end_of_segment = True
            # 2. There's a gap > 2 seconds to the next word
            elif i < len(words) - 1:
                next_word = words[i + 1]
                gap = next_word["start"] - word["end"]
                if gap > 2.0:  # 2 second gap
                    is_end_of_segment = True
            
            # 3. We have enough words for a meaningful segment (max 8 words)
            if len(current_segment_words) >= 8:
                is_end_of_segment = True
            
            if is_end_of_segment and current_segment_words:
                # Create segment
                segment_text = " ".join([w["text"] for w in current_segment_words])
                start_time = current_segment_words[0]["start"]
                end_time = current_segment_words[-1]["end"]
                
                segments.append({
                    "text": segment_text,
                    "start_timestamp": float(start_time),
                    "end_timestamp": float(end_time),
                    "word_count": len(current_segment_words)
                })
                
                print(f"DEBUG: Created segment ({start_time:.2f}-{end_time:.2f}): '{segment_text[:50]}...'")
                
                # Reset for next segment
                current_segment_words = []
        
        return segments
