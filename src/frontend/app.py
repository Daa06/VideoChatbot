import streamlit as st
import requests
import os
from pathlib import Path
import json
from datetime import timedelta
import time
from requests.exceptions import ConnectionError

# API endpoint
API_URL = "http://backend:8000"

def format_timestamp(seconds):
    """Format seconds into HH:MM:SS"""
    return str(timedelta(seconds=int(seconds)))

def check_backend_ready():
    """Check if backend is ready"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=1)  # Timeout après 1 seconde
        return response.status_code == 200
    except:
        return False

def main():
    st.title("🎥 Video Chat")
    
    # Initialize session state
    if "backend_ready" not in st.session_state:
        st.session_state.backend_ready = False
        st.session_state.messages = []
        st.session_state.show_chat = False
    
    # Check backend connection
    if not st.session_state.backend_ready:
        st.session_state.backend_ready = check_backend_ready()
        if not st.session_state.backend_ready:
            st.warning("⚠️ Backend service is starting up... Some features may not be available yet.")
    
    # Main interface
    st.write("Upload a video and chat about its contents!")

    # Sidebar for video upload
    with st.sidebar:
        st.header("Upload Video")
        uploaded_file = st.file_uploader("Choose a video file", type=['mp4', 'mov'])
        
        if uploaded_file is not None:
            process_button = st.button("Process Video", disabled=not st.session_state.backend_ready)
            if process_button:
                with st.spinner("Processing video..."):
                    try:
                        # Save the uploaded file temporarily
                        temp_path = Path("temp_video.mp4")
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getvalue())
                        
                        # Upload to backend
                        files = {"file": open(temp_path, "rb")}
                        response = requests.post(f"{API_URL}/upload", files=files)
                        
                        if response.status_code == 200:
                            st.success("Video processed successfully!")
                            st.session_state.show_chat = True
                        else:
                            st.error(f"Error processing video: {response.text}")
                        
                        # Clean up
                        os.remove(temp_path)
                        files["file"].close()
                    except ConnectionError:
                        st.session_state.backend_ready = False
                        st.error("Could not connect to backend service. Please try again.")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

    # Main chat interface
    if st.session_state.show_chat:
        st.header("Chat About Video")
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if "response" in message:
                    st.write("🤖 " + message["response"])
                if "results" in message:
                    with st.expander("📽️ Related video moments"):
                        for result in message["results"]:
                            st.write(f"**At {format_timestamp(result['timestamp'])}:**")
                            st.write(f"- {result['description']}")
                            if result['summary']:
                                st.write(f"- Summary: {result['summary']}")
                            st.write(f"- Similarity: {result['similarity']:.2f}")
                            st.write("---")

        # Chat input
        if prompt := st.chat_input("Ask about the video...", disabled=not st.session_state.backend_ready):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Get response from API
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/chat",
                            json={"query": prompt}
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            # Add assistant message to chat history
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": "Here's what I found:",
                                "response": result["response"],
                                "results": result["results"]
                            })
                            
                            # Display Gemini's response
                            st.write("🤖 " + result["response"])
                            
                            # Display video moments in an expander
                            with st.expander("📽️ Related video moments"):
                                for highlight in result["results"]:
                                    st.write(f"**At {format_timestamp(highlight['timestamp'])}:**")
                                    st.write(f"- {highlight['description']}")
                                    if highlight['summary']:
                                        st.write(f"- Summary: {highlight['summary']}")
                                    st.write(f"- Similarity: {highlight['similarity']:.2f}")
                                    st.write("---")
                        else:
                            st.error(f"Error: {response.text}")
                    except ConnectionError:
                        st.session_state.backend_ready = False
                        st.error("Could not connect to backend service. Please try again.")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
    else:
        st.info("Upload and process a video to start chatting!")

if __name__ == "__main__":
    main() 