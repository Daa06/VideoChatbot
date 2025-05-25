# 🎥 Video Chat Application

An intelligent video analysis application that allows you to chat with your videos using AI. Upload a video and ask questions about its content, visual elements, audio transcription, or get comprehensive summaries.

## ✨ Features

- 🎬 **Video & Audio Processing** - Automatic extraction of visual descriptions and speech transcription
- 🤖 **Intelligent Query Classification** - Automatically routes questions to the right data type (visual, audio, both, or summary)
- 📝 **Comprehensive Summarization** - Pre-generated video summaries for quick overview questions
- 🔍 **Smart Search** - Similarity-based search with gap detection for relevant results
- 🎯 **Context-Aware Responses** - Synchronized audio-visual analysis for complete understanding
- 🐳 **Docker Ready** - One-command deployment with all dependencies included

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed and running
- [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

### Installation & Running

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Daa06/VideoChatbot.git
   cd VideoChatbot
   ```

2. **Start the application:**
   ```bash
   ./run_docker.sh
   ```

3. **Access the application:**
   - 📱 **Frontend**: http://localhost:8501
   - 🔧 **Backend API**: http://localhost:8000
   - 📚 **API Documentation**: http://localhost:8000/docs

4. **Test the setup (optional):**
   ```bash
   ./test_setup.sh
   ```

### First Use

1. Open http://localhost:8501 in your browser
2. Upload a video file (MP4, AVI, MOV supported)
3. Wait for processing to complete (1-3 minutes depending on video length)
4. Start asking questions about your video!

## 💬 Example Questions

### Summary Questions
- "What is the main topic of this video?"
- "Summarize this video"
- "What are the key points discussed?"

### Visual Questions
- "What is the person wearing?"
- "Describe the scene"
- "What objects are visible?"

### Audio Questions
- "What did they say about...?"
- "What was mentioned regarding...?"
- "What was the dialogue?"

### Combined Questions
- "What happened when they mentioned...?"
- "Describe the scene when they said..."

## 🛠️ Technical Stack

- **Backend**: FastAPI, Python
- **Frontend**: Streamlit
- **Database**: PostgreSQL with pgvector
- **AI Models**: 
  - Vision: BLIP-2 (image captioning)
  - Audio: Whisper (speech-to-text)
  - LLM: Google Gemini (chat responses)
- **Deployment**: Docker & Docker Compose

## 🔧 Configuration

The application uses environment variables defined in `docker-compose.yml`. Key configurations:

- **Database**: PostgreSQL with vector similarity search
- **Models**: Automatically downloaded on first run
- **API Keys**: Gemini API key included (replace with your own for production)

## 📁 Project Structure

```
VideoChatbot/
├── src/
│   ├── api/           # FastAPI backend
│   ├── processors/    # Video/audio processing
│   ├── llm/          # AI model integrations
│   ├── database/     # Database management
│   └── frontend/     # Streamlit UI
├── config/           # Configuration files
├── docker-compose.yml
├── Dockerfile
├── run_docker.sh     # Easy startup script
└── README.md
```

## 🐛 Troubleshooting

### Common Issues

1. **Docker not running**: Make sure Docker Desktop is started
2. **Port conflicts**: Ensure ports 8000, 8501, and 5433 are available
3. **Memory issues**: The application requires at least 4GB RAM
4. **First run slow**: Model downloads can take time on first startup

### Getting Help

1. Check the logs: `docker-compose logs backend`
2. Test connectivity: `./test_setup.sh`
3. Restart: `docker-compose down && ./run_docker.sh`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `./test_setup.sh`
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

# Test_for_team_AI
## submission  
- Submit the assignment only on Github or GitLab.  
---

## 📹 **Step 1: Video Processor with LLM-Based Highlight Extraction**

### 🎯 Task Overview:
Build a **Python-based video processing tool** that extracts descriptive highlights from videos using an **LLM (Large Language Model)**. The processed highlights should be stored in a **PostgreSQL database using pgvector** for similarity-based retrieval.

### ✅ Requirements:

#### Functional Goals:
1. Accept video files as input (e.g., `.mp4`, `.mov`).
2. Automatically extract **visual and audio descriptions** (e.g., scenes, objects, speech-to-text).
3. Use an **LLM** to:
   - Select **important moments** (e.g., explosions, people speaking, vehicle movement).
   - Generate **detailed descriptions** for each moment.
4. Save each highlight to a **PostgreSQL database** with:
   - `timestamp`
   - `description`
   - `video_id`
   - `embedding (pgvector)`
   - `LLM-generated summary`

#### Technical Constraints:
- ✅ Must use **Python**
- ✅ Must use **LMM** Help for chat
- ✅ Must store data in a **PostgreSQL + pgvector** database.
- ✅ Must follow **OOP principles** with good folder structure and separation of concerns (`processors`, `database`, `llm`, etc.).
- ✅ Must include a **Docker setup** for both the Python service and PostgreSQL (with pgvector extension).
- ✅ Must contain a **demo script** showing:
   - Video processing in action
   - Output descriptions being saved to DB

#### Deliverables:
- Python code with OOP structure
- Docker setup (`docker-compose.yml`)
- PostgreSQL schema
- ✅ A very neat and **clear README** 


## Note:
- **The examinee must select the videos. A proper video is between thirty seconds and a minute and a half. The video must be uploaded along with the assignment, At least two videos must be selected.**
- You can use free key  " https://aistudio.google.com/ "
---

## 💬 **Step 2: Interactive Chat About Video Highlights**

### 🎯 Task Overview:
Extend your system to allow users to **chat with a React frontend** and ask questions about the processed video highlights.

### ✅ Requirements:

#### Functional Goals:
1. Build a **Free choice frontend** that allows users to:
   - Enter a question (e.g., *"What happened after the person got out of the car?"*)
   - See answers pulled **only from the database**
2. Build a **Python backend (FastAPI recommended)** that:
   - Accepts chat questions
   - Uses embeddings or keyword search to match relevant highlights from the DB
   - Responds only with content from the database (no real-time LLM response)
   - Structures responses coherently based on matching highlights

#### Technical Constraints:
- ✅ Frontend in **Free choice**
- ✅ Backend in **Python** (FastAPI preferred)
- ✅ Adheres to **OOP structure** for API, data access layer, and chat logic
- ✅ Uses Docker for both frontend and backend
- ✅ Backend must pull data **only from the database** (LLM is not used in this step)
- ✅ Clean modular architecture and routing in both React and Python
- ✅ Include a **neat README** that explains:
   - How to start each container
   - Chat architecture
   - Endpoint flow

---

## 🧠 **Bonus Task: Neural Network Tic-Tac-Toe Player**

### 🎯 Task Overview:
Implement a simple neural network that learns to play **Tic-Tac-Toe** using self-play or predefined rules. Provide both a **training visualization** and a **game interface**.

### ✅ Requirements:

#### Part 1: Model Training
- Implement a **basic neural network** in PyTorch or TensorFlow.
- Train it to play against:
  - Random moves (Easy)
  - Heuristic opponent (Medium)
  - Itself (Hard)
- Log training process (e.g., win rate, loss, move preference)

#### Part 2: Game Interface
- Display the game board using a simple GUI (Tkinter, PyGame, or web-based)
- Let the user select difficulty (Easy, Medium, Hard)
- Show the model's move in real time

#### Bonus Points:
- Add visual feedback for the training process (matplotlib loss curves, win stats)
- Enable human-vs-AI play mode

