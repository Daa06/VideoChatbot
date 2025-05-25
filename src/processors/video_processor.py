import cv2
import numpy as np
import torch
from pathlib import Path
from transformers import (
    VisionEncoderDecoderModel,
    ViTImageProcessor,
    AutoTokenizer
)
from config.config import CAPTION_MODEL_ID, N_FRAMES, DEVICE

class VideoProcessor:
    _instance = None
    _is_initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VideoProcessor, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._is_initialized:
            print("Initializing VideoProcessor and loading models...")
            # Initialize vision models
            self.caption_model = VisionEncoderDecoderModel.from_pretrained(CAPTION_MODEL_ID).to(DEVICE)
            self.processor = ViTImageProcessor.from_pretrained(CAPTION_MODEL_ID)
            self.tokenizer = AutoTokenizer.from_pretrained(CAPTION_MODEL_ID)
            print("Vision models loaded successfully!")
            self._is_initialized = True
    
    @property
    def is_ready(self):
        return self._is_initialized
    
    def process_video(self, video_path: str) -> dict:
        """Process a video file and return visual descriptions"""
        if not self._is_initialized:
            raise RuntimeError("VideoProcessor not properly initialized. Models not loaded.")
            
        print("Starting video processing...")
        
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        print("Getting video duration...")
        # Get video duration
        cap = cv2.VideoCapture(str(video_path))
        duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        
        print("Processing frames...")
        # Process frames
        frames, timestamps = self._sample_frames(str(video_path))
        print(f"Processing {len(frames)} frames...")
        visual_descriptions = self._process_frames(frames)
        
        print("Video processing complete!")
        return {
            "duration": duration,
            "visual_descriptions": visual_descriptions,
            "timestamps": timestamps
        }
    
    def _sample_frames(self, video_path: str) -> list:
        """Sample one frame per second from the video"""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        
        print(f"Video info: {total_frames} frames, {fps} FPS, {duration:.2f} seconds")
        
        frames = []
        timestamps = []
        
        # Get one frame per second, starting from the first valid frame
        for second in range(int(duration)):
            frame_index = int(second * fps)
            if frame_index >= total_frames:
                break
                
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ret, frame = cap.read()
            if ret and frame is not None and frame.size > 0:
                # Convert to RGB and check if frame is not empty
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                if rgb_frame.size > 0 and not np.all(rgb_frame == 0):
                    frames.append(rgb_frame)
                    timestamps.append(second)
                    print(f"Successfully read frame at second {second} (index {frame_index})")
                else:
                    print(f"Empty or invalid frame at second {second} (index {frame_index})")
            else:
                print(f"Could not read frame at second {second} (index {frame_index})")
        
        cap.release()
        print(f"Total valid frames sampled: {len(frames)}")
        return frames, timestamps
    
    def _process_frames(self, frames: list) -> list:
        """Process frames and generate captions"""
        # Process frames in batches to optimize memory usage
        batch_size = 4
        captions = []
        
        for i in range(0, len(frames), batch_size):
            batch = frames[i:i + batch_size]
            pixel_values = self.processor(batch, return_tensors="pt").pixel_values.to(DEVICE)
            with torch.no_grad():
                out = self.caption_model.generate(
                    pixel_values, 
                    max_length=40,
                    min_length=20,
                    temperature=0.6,
                    
                )
            batch_captions = self.tokenizer.batch_decode(out, skip_special_tokens=True)
            captions.extend(batch_captions)
        
        return captions
