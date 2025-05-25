import cv2
import numpy as np
import torch
import ffmpeg
from transformers import (
    VisionEncoderDecoderModel,
    ViTImageProcessor,
    AutoTokenizer,
    pipeline
)

# -------- CONFIG ---------
VIDEO_PATH = "/Users/danieldahan/Desktop/spart.mp4"
N_FRAMES = 15
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
CAPTION_MODEL_ID = "nlpconnect/vit-gpt2-image-captioning"
ASR_MODEL_ID = "facebook/wav2vec2-base-960h"   # Change to "openai/whisper-base" for fast tests

# -------- UTILS ---------

def sample_frames(video_path, n_frames=15):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    idxs = np.linspace(0, total_frames-1, n_frames, dtype=int)
    frames = []
    current = 0
    wanted = set(idxs)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if current in wanted:
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        current += 1
        if len(frames) == n_frames:
            break
    cap.release()
    return frames

def extract_audio(video_path, audio_path="audio.wav"):
    (
        ffmpeg
        .input(video_path)
        .output(audio_path, ac=1, ar='16000')
        .overwrite_output()
        .run(quiet=True)
    )
    return audio_path

# -------- IMAGE CAPTION ---------

print("Extraction des frames vidéo...")
frames = sample_frames(VIDEO_PATH, N_FRAMES)
if not frames:
    raise ValueError("Aucune image extraite : vérifie que la vidéo est lisible !")

print("Chargement du modèle de captioning...")
model = VisionEncoderDecoderModel.from_pretrained(CAPTION_MODEL_ID).to(DEVICE)
processor = ViTImageProcessor.from_pretrained(CAPTION_MODEL_ID)
tokenizer = AutoTokenizer.from_pretrained(CAPTION_MODEL_ID)

print("Génération des captions (image-to-text)...")
pixel_values = processor(frames, return_tensors="pt").pixel_values.to(DEVICE)
with torch.no_grad():
    out = model.generate(pixel_values, max_length=20)
captions = tokenizer.batch_decode(out, skip_special_tokens=True)

print("\n---- CAPTIONS PAR FRAME ----")
for i, cap in enumerate(captions):
    print(f"[{i+1}] {cap}")

# -------- AUDIO CAPTION (SPEECH-TO-TEXT) ---------

print("\nExtraction de l'audio...")
AUDIO_PATH = extract_audio(VIDEO_PATH)

print("Transcription de l'audio (speech-to-text)...")
asr = pipeline("automatic-speech-recognition", model=ASR_MODEL_ID, device=0 if DEVICE=="cuda" else -1, return_timestamps='word')
result = asr(AUDIO_PATH)
print("\n---- TRANSCRIPTION AUDIO ----")
print(result['text'])

