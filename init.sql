-- Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the videos table
CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    duration FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the highlights table with the correct vector dimension
CREATE TABLE IF NOT EXISTS highlights (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id),
    timestamp FLOAT NOT NULL,
    description TEXT NOT NULL,
    summary TEXT,
    embedding vector(384),  -- Dimension spécifique pour all-MiniLM-L6-v2
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 