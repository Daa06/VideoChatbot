#!/usr/bin/env python3

import sys
import os
import shutil
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table

# Import existing components
from src.processors.video_processor import VideoProcessor
from src.processors.audio_processor import AudioProcessor
from src.llm.highlight_extractor import HighlightExtractor
from src.llm.gemini_chat import GeminiChat
from src.database.db_manager import DatabaseManager
from config.config import VIDEOS_DIR, GEMINI_API_KEY
from src.llm.query_classifier import QueryClassifier

console = Console()

def print_header():
    console.print(Panel.fit(
        "[bold blue]🎥 Video Chat Demo[/bold blue]\n"
        "This script demonstrates the complete video processing pipeline:\n"
        "• Video & Audio Processing\n"
        "• Highlight Extraction with LLM\n"
        "• Database Storage with Vector Embeddings\n"
        "• Intelligent Query Processing",
        border_style="blue"
    ))

def print_step(step_num: int, description: str):
    console.print(f"\n[bold green]Step {step_num}:[/bold green] {description}")

def show_database_results(db_manager: DatabaseManager, video_id: int):
    """Display stored results from database"""
    
    # Get visual highlights
    visual_table = Table(title="📹 Visual Descriptions Stored")
    visual_table.add_column("Timestamp", style="cyan", width=12)
    visual_table.add_column("Description", style="green")
    
    # Get audio highlights  
    audio_table = Table(title="🔊 Audio Segments Stored")
    audio_table.add_column("Time Range", style="cyan", width=15)
    audio_table.add_column("Transcription", style="green")
    
    # Query database for highlights
    with db_manager.conn.cursor() as cur:
        # Get visual highlights (no end_timestamp)
        cur.execute("""
            SELECT timestamp, description FROM highlights 
            WHERE video_id = %s AND end_timestamp IS NULL 
            ORDER BY timestamp LIMIT 5
        """, (video_id,))
        visual_results = cur.fetchall()
        
        for timestamp, desc in visual_results:
            visual_table.add_row(
                f"{timestamp:.1f}s",
                desc[:60] + "..." if len(desc) > 60 else desc
            )
        
        # Get audio highlights (with end_timestamp)
        cur.execute("""
            SELECT timestamp, end_timestamp, description FROM highlights 
            WHERE video_id = %s AND end_timestamp IS NOT NULL 
            ORDER BY timestamp LIMIT 5
        """, (video_id,))
        audio_results = cur.fetchall()
        
        for start, end, desc in audio_results:
            audio_table.add_row(
                f"{start:.1f}s-{end:.1f}s",
                desc[:50] + "..." if len(desc) > 50 else desc
            )
    
    console.print(visual_table)
    console.print(audio_table)
    
    # Show summary
    summary = db_manager.get_video_summary(video_id)
    if summary and summary != "No summary available for this video.":
        console.print(Panel(
            f"[yellow]{summary[:200]}...[/yellow]",
            title="📝 Generated Summary",
            border_style="yellow"
        ))

def process_video_demo(video_path: str):
    """Demonstrate the complete video processing pipeline"""
    
    print_step(1, "Initializing AI Models")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
    ) as progress:
        init_task = progress.add_task("Loading models...", total=100)
        
        # Initialize all components (same as API)
        video_processor = VideoProcessor()
        audio_processor = AudioProcessor()
        highlight_extractor = HighlightExtractor()
        db_manager = DatabaseManager()
        gemini_chat = GeminiChat(GEMINI_API_KEY)
        
        progress.update(init_task, completed=100)
    
    print_step(2, "Processing Video & Audio")
    with Progress() as progress:
        # Clear previous data
        clear_task = progress.add_task("Clearing previous data...", total=100)
        db_manager.clear_all_data()
        progress.update(clear_task, completed=100)
        
        # Process video and audio (parallel like in API)
        process_task = progress.add_task("Processing video & audio...", total=100)
        
        # Video processing
        video_data = video_processor.process_video(video_path)
        progress.update(process_task, advance=50)
        
        # Audio processing
        audio_data = audio_processor.process_audio(video_path)
        video_data["audio_transcription"] = audio_data
        progress.update(process_task, completed=100)
    
    print_step(3, "Extracting Highlights with LLM")
    with Progress() as progress:
        extract_task = progress.add_task("Extracting highlights...", total=100)
        
        # Extract highlights using LLM (same as API)
        highlights = highlight_extractor.extract_highlights(video_data)
        
        progress.update(extract_task, completed=100)
    
    print_step(4, "Storing in Database with Vector Embeddings")
    with Progress() as progress:
        store_task = progress.add_task("Storing to database...", total=100)
        
        # Save to database (same as API)
        video_id = db_manager.insert_video(os.path.basename(video_path), video_data["duration"])
        progress.update(store_task, advance=25)
        
        for highlight in highlights:
            db_manager.insert_highlight(
                video_id=video_id,
                timestamp=highlight["timestamp"],
                description=highlight["description"],
                summary=highlight["summary"],
                embedding=highlight["embedding"],
                end_timestamp=highlight.get("end_timestamp")
            )
        progress.update(store_task, advance=50)
        
        # Generate and store summary
        video_summary = gemini_chat.generate_summary(highlights, video_data)
        db_manager.insert_video_summary(video_id, video_summary)
        progress.update(store_task, completed=100)
    
    print_step(5, "Database Results")
    show_database_results(db_manager, video_id)
    
    return video_id, gemini_chat, highlight_extractor, db_manager

def demo_queries(video_id: int, gemini_chat: GeminiChat, highlight_extractor: HighlightExtractor, db_manager: DatabaseManager):
    """Demonstrate different types of queries"""
    
    print_step(6, "Testing Intelligent Query System")
    
    # Initialize query classifier
    query_classifier = QueryClassifier(gemini_chat)
    
    # Test different query types
    test_queries = [
        "What is the main topic of this video?",  # summary
        "What are the people wearing?",           # visual
        "What was said about Spartans?",          # audio
        "What happened when they mentioned Athens?" # both
    ]
    
    for i, query in enumerate(test_queries, 1):
        console.print(f"\n[bold cyan]Query {i}:[/bold cyan] {query}")
        
        # Classify query
        data_type = query_classifier.classify_query(query)
        console.print(f"[yellow]→ Classified as:[/yellow] {data_type}")
        
        # Get results based on classification
        query_embedding = highlight_extractor.get_embedding(query)
        
        if data_type == "visual":
            results = db_manager.search_visual_highlights(query_embedding, limit=2)
        elif data_type == "audio":
            results = db_manager.search_audio_highlights(query_embedding, limit=2)
        elif data_type == "summary":
            summary = db_manager.get_video_summary(video_id)
            console.print(f"[green]→ Response:[/green] {summary[:150]}...")
            continue
        else:  # both
            results = db_manager.search_similar_highlights(query_embedding, limit=2)
        
        # Generate response
        if results:
            response = gemini_chat.generate_response(results, data_type)
            console.print(f"[green]→ Response:[/green] {response[:150]}...")
        else:
            console.print("[red]→ No relevant results found[/red]")

def main():
    if len(sys.argv) != 2:
        console.print("[red]Please provide a video file path as argument[/red]")
        console.print("Usage: python demo.py path/to/video.mp4")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        console.print(f"[red]Video file not found: {video_path}[/red]")
        sys.exit(1)
    
    print_header()
    
    try:
        # Process video
        video_id, gemini_chat, highlight_extractor, db_manager = process_video_demo(video_path)
        
        # Demo queries
        demo_queries(video_id, gemini_chat, highlight_extractor, db_manager)
        
        console.print(Panel(
            "[bold green]✅ Demo completed successfully![/bold green]\n"
            "The video has been processed and stored in the database.\n"
            "You can now use the web interface to chat with your video!",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        import traceback
        console.print(f"[red]{traceback.format_exc()}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
