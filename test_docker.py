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
from concurrent.futures import ThreadPoolExecutor
import os

# -------- CONFIG ---------
VIDEO_PATH = "/app/videos/test.mp4"  # Chemin dans le conteneur
N_FRAMES = 15
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
CAPTION_MODEL_ID = "nlpconnect/vit-gpt2-image-captioning"
ASR_MODEL_ID = "facebook/wav2vec2-base-960h"   # Or "openai/whisper-base" for faster tests

# -------- UTILS ---------

def sample_frames(video_path, n_frames=15):
    print(f"Tentative d'ouverture de la vidéo: {video_path}")
    print(f"Le fichier existe: {os.path.exists(video_path)}")
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

def image_caption_pipeline():
    print("Extraction des frames vidéo...")
    frames = sample_frames(VIDEO_PATH, N_FRAMES)
    if not frames:
        raise ValueError("Aucune image extraite : vérifie que la vidéo est lisible !")
    print("Chargement du modèle de captioning...")
    model = VisionEncoderDecoderModel.from_pretrained(CAPTION_MODEL_ID).to(DEVICE)
    processor = ViTImageProcessor.from_pretrained(CAPTION_MODEL_ID)
    tokenizer = AutoTokenizer.from_pretrained(CAPTION_MODEL_ID)
    print("Génération des captions (image-to-text)...")
    pixel_values = processor(frames, return_tensors="pt").pixel_values.to(DEVICE)
    with torch.no_grad():
        out = model.generate(pixel_values, max_length=20)
    captions = tokenizer.batch_decode(out, skip_special_tokens=True)
    output = "\n---- CAPTIONS PAR FRAME ----\n"
    for i, cap in enumerate(captions):
        output += f"[{i+1}] {cap}\n"
    return output

def speech_to_text_pipeline():
    print("\nExtraction de l'audio...")
    AUDIO_PATH = extract_audio(VIDEO_PATH)
    print("Transcription de l'audio (speech-to-text)...")
    asr = pipeline("automatic-speech-recognition", model=ASR_MODEL_ID, device=0 if DEVICE=="cuda" else -1, return_timestamps='word')
    result = asr(AUDIO_PATH)
    return "\n---- TRANSCRIPTION AUDIO ----\n" + result['text']

if __name__ == "__main__":
    print("Démarrage du test...")
    print(f"Utilisation du device: {DEVICE}")
    with ThreadPoolExecutor() as executor:
        fut1 = executor.submit(image_caption_pipeline)
        fut2 = executor.submit(speech_to_text_pipeline)
        for fut in [fut1, fut2]:
            try:
                print(fut.result())
            except Exception as e:
                print(f"Erreur: {str(e)}")
    print("✅ Les deux tâches sont terminées (en parallèle) !") 