from transformers import pipeline
from sentence_transformers import SentenceTransformer
import numpy as np
import torch
from config.config import EMBEDDING_MODEL_ID

class HighlightExtractor:
    def __init__(self):
        # Initialize the embedding model for similarity search
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_ID)
    
    def extract_highlights(self, video_data: dict) -> list:
        """Extract highlights from video data"""
        highlights = []
        
        # Process visual descriptions with correct timestamps
        visual_descriptions = video_data["visual_descriptions"]
        timestamps = video_data.get("timestamps", [])
        
        # Ensure we have timestamps for all descriptions
        if len(timestamps) != len(visual_descriptions):
            # Fallback to calculated timestamps if mismatch
            timestamps = [(i / len(visual_descriptions)) * video_data["duration"] 
                         for i in range(len(visual_descriptions))]
        
        for i, caption in enumerate(visual_descriptions):
            # Skip empty captions
            if not caption or not caption.strip():
                continue
                
            timestamp = timestamps[i] if i < len(timestamps) else 0
            
            # Generate embedding for similarity search
            embedding = self.embedding_model.encode(caption)
            
            highlights.append({
                "timestamp": timestamp,
                "description": caption,
                "summary": "",  # No summary needed
                "embedding": embedding
            })
        
        # Process audio transcription segments
        if "audio_transcription" in video_data and video_data["audio_transcription"]:
            audio_data = video_data["audio_transcription"]
            print(f"DEBUG: Processing audio data: {type(audio_data)}")
            
            # Check if we have segments (new format)
            if isinstance(audio_data, dict) and "segments" in audio_data:
                segments = audio_data["segments"]
                print(f"DEBUG: Found {len(segments)} audio segments")
                
                for i, segment in enumerate(segments):
                    if segment.get("text") and segment["text"].strip():
                        segment_text = segment["text"]
                        start_timestamp = segment.get("start_timestamp", 0)
                        end_timestamp = segment.get("end_timestamp", start_timestamp)
                        
                        print(f"DEBUG: Adding audio segment {i}: '{segment_text[:50]}...' ({start_timestamp:.2f}-{end_timestamp:.2f})")
                        
                        # Generate embedding for similarity search
                        embedding = self.embedding_model.encode(segment_text)
                        
                        highlights.append({
                            "timestamp": start_timestamp,
                            "end_timestamp": end_timestamp,
                            "description": segment_text,
                            "summary": "",  # No summary needed
                            "embedding": embedding
                        })
            
            # Fallback to old format (single text)
            elif isinstance(audio_data, dict) and "text" in audio_data:
                audio_text = audio_data["text"]
                if audio_text and audio_text.strip():
                    print(f"DEBUG: Adding single audio transcription (fallback): '{audio_text[:50]}...'")
                    audio_embedding = self.embedding_model.encode(audio_text)
                    
                    highlights.append({
                        "timestamp": 0,  # Audio spans the entire video
                        "end_timestamp": None,
                        "description": audio_text,
                        "summary": "",  # No summary needed
                        "embedding": audio_embedding
                    })
            else:
                print(f"DEBUG: Unexpected audio data format: {audio_data}")
        else:
            print(f"DEBUG: No audio transcription found in video_data")
        
        print(f"DEBUG: Total highlights created: {len(highlights)}")
        return highlights
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a text query"""
        return self.embedding_model.encode(text)
