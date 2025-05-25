from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
from pathlib import Path
import os
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

from src.processors.video_processor import VideoProcessor
from src.processors.audio_processor import AudioProcessor
from src.llm.highlight_extractor import HighlightExtractor
from src.llm.gemini_chat import GeminiChat
from src.database.db_manager import DatabaseManager
from config.config import VIDEOS_DIR, GEMINI_API_KEY
from src.llm.query_classifier import QueryClassifier

app = FastAPI(title="Video Chat API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
video_processor = VideoProcessor()
audio_processor = AudioProcessor()
highlight_extractor = HighlightExtractor()
db_manager = DatabaseManager()
gemini_chat = GeminiChat(GEMINI_API_KEY)

# Ensure videos directory exists
VIDEOS_DIR.mkdir(exist_ok=True)

class ChatQuery(BaseModel):
    query: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models_ready": video_processor.is_ready and audio_processor.is_ready
    }

def process_video_parallel(video_path: str) -> dict:
    """Process video and audio in parallel"""
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Start both tasks
        video_future = executor.submit(video_processor.process_video, video_path)
        audio_future = executor.submit(audio_processor.process_audio, video_path)
        
        # Get results
        video_data = video_future.result()
        audio_data = audio_future.result()
        
        # Combine results - audio_processor returns {"text": "...", "words": [...]}
        video_data["audio_transcription"] = audio_data
        
        print(f"DEBUG: Audio data received: {audio_data}")
        print(f"DEBUG: Combined video_data keys: {video_data.keys()}")
        
        return video_data

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """Upload and process a video file"""
    if not video_processor.is_ready or not audio_processor.is_ready:
        raise HTTPException(
            status_code=503,
            detail="Service is starting up. Models are still being loaded. Please try again in a moment."
        )
    
    try:
        print("Starting video upload...")
        
        # Clear previous data before processing new video
        print("Clearing previous video data...")
        db_manager.clear_all_data()
        
        # Save video file
        video_path = VIDEOS_DIR / file.filename
        print(f"Saving video to {video_path}")
        with video_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print("Processing video and audio in parallel...")
        # Process video and audio in parallel
        video_data = process_video_parallel(str(video_path))
        
        print("Extracting highlights...")
        # Extract highlights
        highlights = highlight_extractor.extract_highlights(video_data)
        
        print("Saving to database...")
        # Save to database
        video_id = db_manager.insert_video(file.filename, video_data["duration"])
        for highlight in highlights:
            db_manager.insert_highlight(
                video_id=video_id,
                timestamp=highlight["timestamp"],
                description=highlight["description"],
                summary=highlight["summary"],
                embedding=highlight["embedding"],
                end_timestamp=highlight.get("end_timestamp")
            )
        
        print("Generating video summary...")
        # Generate comprehensive video summary
        video_summary = gemini_chat.generate_summary(highlights, video_data)
        
        # Save summary to database
        db_manager.insert_video_summary(video_id, video_summary)
        
        print("Video processing complete!")
        return {"message": "Video processed successfully", "video_id": video_id}
    
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(query: ChatQuery):
    """Process a chat query and return relevant highlights"""
    if not video_processor.is_ready or not audio_processor.is_ready:
        raise HTTPException(
            status_code=503,
            detail="Service is starting up. Models are still being loaded. Please try again in a moment."
        )
    
    try:
        # Step 1: Classify the query to determine what data type to search
        query_classifier = QueryClassifier(gemini_chat)
        data_type = query_classifier.classify_query(query.query)
        
        print(f"Query classified as: {data_type}")
        
        # Step 2: Get query embedding
        query_embedding = highlight_extractor.get_embedding(query.query)
        
        # Step 3: Search based on classification
        if data_type == "visual":
            results = db_manager.search_visual_highlights(query_embedding)
            print("Searching visual data only")
        elif data_type == "audio":
            results = db_manager.search_audio_highlights(query_embedding)
            print("Searching audio data only")
        elif data_type == "summary":
            # Get pre-generated summary from database
            summary = db_manager.get_video_summary()
            print("Retrieving pre-generated video summary")
            
            # Create a mock result with the summary to pass through Gemini
            summary_result = [{
                "timestamp": 0,
                "end_timestamp": None,
                "description": summary,
                "summary": "",
                "filename": "video_summary",
                "user_question": query.query
            }]
            
            # Let Gemini process the question with the summary context
            gemini_response = gemini_chat.generate_response(summary_result, data_type)
            
            return {
                "query": query.query,
                "data_type_used": data_type,
                "response": gemini_response,
                "results": []
            }
        else:  # both
            results = db_manager.search_similar_highlights(query_embedding)
            print("Searching both visual and audio data")
        
        # Step 4: Generate response with Gemini
        gemini_response = gemini_chat.generate_response(results, data_type)
        
        # Step 5: Format response based on data type
        if data_type == "both" and results and isinstance(results[0], dict) and 'audio_segment' in results[0]:
            # New format: grouped audio segments with related visuals
            formatted_results = []
            for segment in results:
                audio = segment['audio_segment']
                visuals = segment['related_visuals']
                
                # Add audio segment as a result
                formatted_results.append({
                    "timestamp": float(audio["timestamp"]),
                    "end_timestamp": float(audio.get("end_timestamp", audio["timestamp"])),
                    "description": audio["description"],
                    "summary": "",
                    "video": audio["filename"],
                    "similarity": float(audio["similarity"]),
                    "type": "audio"
                })
                
                # Add related visuals as results
                for visual in visuals:
                    formatted_results.append({
                        "timestamp": float(visual["timestamp"]),
                        "end_timestamp": visual.get("end_timestamp"),
                        "description": visual["description"],
                        "summary": visual.get("summary", ""),
                        "video": visual["filename"],
                        "similarity": float(visual["similarity"]),
                        "type": "visual"
                    })
            
            response = {
                "query": query.query,
                "data_type_used": data_type,
                "response": gemini_response,
                "results": formatted_results
            }
        else:
            # Original format for visual/audio only queries
            response = {
                "query": query.query,
                "data_type_used": data_type,
                "response": gemini_response,
                "results": [
                    {
                        "timestamp": r["timestamp"],
                        "end_timestamp": r.get("end_timestamp"),
                        "description": r["description"],
                        "summary": r["summary"],
                        "video": r["filename"],
                        "similarity": float(r["similarity"])
                    }
                    for r in results
                ]
            }
        
        return response
    
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.on_event("shutdown")
def shutdown_event():
    """Clean up resources on shutdown"""
    db_manager.close()
