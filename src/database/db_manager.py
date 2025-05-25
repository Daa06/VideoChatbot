import psycopg2
from psycopg2.extras import DictCursor
import numpy as np
from config.config import DB_CONFIG

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish connection to PostgreSQL database"""
        self.conn = psycopg2.connect(**DB_CONFIG)
        # Enable pgvector extension
        with self.conn.cursor() as cur:
            cur.execute('CREATE EXTENSION IF NOT EXISTS vector;')
        self.conn.commit()
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        with self.conn.cursor() as cur:
            # Videos table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    duration FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Highlights table with vector embedding
            cur.execute("""
                CREATE TABLE IF NOT EXISTS highlights (
                    id SERIAL PRIMARY KEY,
                    video_id INTEGER REFERENCES videos(id),
                    timestamp FLOAT NOT NULL,
                    end_timestamp FLOAT,
                    description TEXT NOT NULL,
                    summary TEXT,
                    embedding vector(384),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Video summaries table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS video_summaries (
                    id SERIAL PRIMARY KEY,
                    video_id INTEGER REFERENCES videos(id),
                    summary TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Add end_timestamp column if it doesn't exist (for existing databases)
            cur.execute("""
                ALTER TABLE highlights 
                ADD COLUMN IF NOT EXISTS end_timestamp FLOAT;
            """)
        self.conn.commit()
    
    def insert_video(self, filename: str, duration: float) -> int:
        """Insert a new video record and return its ID"""
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO videos (filename, duration) VALUES (%s, %s) RETURNING id",
                (filename, duration)
            )
            video_id = cur.fetchone()[0]
        self.conn.commit()
        return video_id
    
    def insert_highlight(self, video_id: int, timestamp: float, description: str, 
                        summary: str, embedding: np.ndarray, end_timestamp: float = None):
        """Insert a new highlight with its embedding"""
        # Convert numpy array to list and ensure it's a flat list
        vector_list = embedding.flatten().tolist()
        
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO highlights 
                (video_id, timestamp, end_timestamp, description, summary, embedding)
                VALUES (%s, %s, %s, %s, %s, %s::vector)
                """,
                (video_id, timestamp, end_timestamp, description, summary, vector_list)
            )
        self.conn.commit()
    
    def insert_video_summary(self, video_id: int, summary: str):
        """Insert a video summary"""
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO video_summaries (video_id, summary) VALUES (%s, %s)",
                (video_id, summary)
            )
        self.conn.commit()
        print(f"Video summary saved for video_id: {video_id}")

    def get_video_summary(self, video_id: int = None) -> str:
        """Get video summary by video_id, or get the latest if no video_id provided"""
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            if video_id:
                cur.execute(
                    "SELECT summary FROM video_summaries WHERE video_id = %s ORDER BY created_at DESC LIMIT 1",
                    (video_id,)
                )
            else:
                # Get the most recent summary if no video_id specified
                cur.execute(
                    "SELECT summary FROM video_summaries ORDER BY created_at DESC LIMIT 1"
                )
            
            result = cur.fetchone()
            return result['summary'] if result else "No summary available for this video."

    def search_visual_highlights(self, query_embedding: np.ndarray, limit: int = 5):
        """Search only visual descriptions (excludes audio transcription)"""
        # Convert numpy array to list and ensure it's a flat list
        vector_list = query_embedding.flatten().tolist()
        
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                """
                SELECT h.*, v.filename,
                1 - (h.embedding <-> %s::vector) as similarity
                FROM highlights h
                JOIN videos v ON h.video_id = v.id
                WHERE h.timestamp > 0  -- Exclude audio (timestamp = 0)
                ORDER BY h.embedding <-> %s::vector
                LIMIT %s
                """,
                (vector_list, vector_list, limit)
            )
            results = cur.fetchall()
            print(f"DEBUG: Visual search returned {len(results)} results")
            for i, r in enumerate(results[:2]):  # Show first 2
                print(f"DEBUG: Visual result {i}: timestamp={r['timestamp']}, desc='{r['description'][:50]}...'")
            return results

    def search_audio_highlights(self, query_embedding: np.ndarray, limit: int = 5):
        """Search only audio transcription with similarity gap detection"""
        # Convert numpy array to list and ensure it's a flat list
        vector_list = query_embedding.flatten().tolist()
        
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                """
                SELECT h.*, v.filename,
                1 - (h.embedding <-> %s::vector) as similarity
                FROM highlights h
                JOIN videos v ON h.video_id = v.id
                WHERE h.timestamp >= 0 AND h.end_timestamp IS NOT NULL  -- Only audio segments
                ORDER BY h.embedding <-> %s::vector
                """,
                (vector_list, vector_list)
            )
            all_results = cur.fetchall()
            
            # Apply similarity gap detection with stricter threshold for max 2 results
            results = self._filter_by_similarity_gap(all_results, gap_threshold=0.05)
            
            print(f"DEBUG: Audio search returned {len(results)} results (from {len(all_results)} candidates)")
            for i, r in enumerate(results):
                print(f"DEBUG: Audio result {i}: timestamp={r['timestamp']:.2f}-{r.get('end_timestamp', 'N/A')}, similarity={r['similarity']:.3f}, desc='{r['description'][:50]}...'")
            return results

    def search_similar_highlights(self, query_embedding: np.ndarray, limit: int = 5):
        """Search for similar highlights - returns audio segments + related visuals"""
        # Get relevant audio segments first
        audio_segments = self.search_audio_highlights(query_embedding)
        
        results = []
        
        for audio_segment in audio_segments:
            # Get visual highlights from the same time period
            start_time = audio_segment['timestamp']
            end_time = audio_segment.get('end_timestamp', start_time + 5)  # Default 5 second window
            
            related_visuals = self.search_visual_highlights_in_timerange(
                start_time - 2,  # 2 seconds before
                end_time + 2,    # 2 seconds after
                limit=3
            )
            
            # Create a grouped result
            segment_result = {
                'audio_segment': audio_segment,
                'related_visuals': related_visuals,
                'timestamp': start_time,
                'end_timestamp': end_time
            }
            results.append(segment_result)
        
        print(f"DEBUG: Combined search returned {len(results)} audio segments with related visuals")
        for i, result in enumerate(results):
            audio = result['audio_segment']
            visuals_count = len(result['related_visuals'])
            print(f"DEBUG: Segment {i}: audio ({audio['timestamp']:.2f}-{audio.get('end_timestamp', 'N/A')}) + {visuals_count} visuals")
        
        return results

    def search_visual_highlights_in_timerange(self, start_time: float, end_time: float, limit: int = 3):
        """Find visual highlights within a specific time range"""
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                """
                SELECT h.*, v.filename,
                0.8 as similarity  -- Default similarity for time-based matches
                FROM highlights h
                JOIN videos v ON h.video_id = v.id
                WHERE h.timestamp BETWEEN %s AND %s 
                AND h.end_timestamp IS NULL  -- Only visual highlights
                ORDER BY h.timestamp
                LIMIT %s
                """,
                (start_time, end_time, limit)
            )
            return cur.fetchall()

    def _filter_by_similarity_gap(self, results, gap_threshold=0.05, max_results=2):
        """Filter results using similarity gap detection with absolute maximum limit"""
        if not results:
            return []
        
        # Always include the first (best) result
        filtered_results = [results[0]]
        
        # Check each subsequent result for similarity gaps
        for i in range(1, len(results)):
            # Stop if we've reached the maximum number of results
            if len(filtered_results) >= max_results:
                print(f"DEBUG: Reached maximum limit of {max_results} results")
                break
                
            current = results[i-1]  # Previous result (already in filtered_results)
            next_result = results[i]  # Current result being evaluated
            
            # Check similarity gap
            similarity_gap = current['similarity'] - next_result['similarity']
            
            print(f"DEBUG: Checking gap: {current['similarity']:.3f} -> {next_result['similarity']:.3f} (gap: {similarity_gap:.3f})")
            
            if similarity_gap > gap_threshold:
                print(f"DEBUG: Similarity gap detected: {current['similarity']:.3f} -> {next_result['similarity']:.3f} (gap: {similarity_gap:.3f}) - stopping here")
                break
            else:
                # Gap is small enough, include this result
                filtered_results.append(next_result)
        
        print(f"DEBUG: Gap filtering: {len(results)} -> {len(filtered_results)} results")
        return filtered_results
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()

    def clear_all_data(self):
        """Clear all videos and highlights from the database"""
        with self.conn.cursor() as cur:
            # Delete in correct order to avoid foreign key constraint violations
            cur.execute("DELETE FROM video_summaries;")  # Delete summaries first
            cur.execute("DELETE FROM highlights;")       # Then highlights
            cur.execute("DELETE FROM videos;")           # Finally videos
        self.conn.commit()
        print("Database cleared: all videos, highlights, and summaries removed")
