import google.generativeai as genai
from config.config import GEMINI_API_KEY

class GeminiChat:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')

    def generate_response_simple(self, prompt: str) -> str:
        """Generate a simple response without highlights context"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=200
                )
            )
            return response.text
        except Exception as e:
            print(f"Error generating simple response: {e}")
            return "both"  # Fallback for classification

    def generate_response(self, highlights, data_type="unknown"):
        """Generate response from highlights - handles both simple and grouped formats"""
        if not highlights:
            return "Please provide the highlights from the video. I need the text of the highlights to be able to give you a detailed response."
        
        # Check if this is the new grouped format (audio segments + visuals)
        if isinstance(highlights[0], dict) and 'audio_segment' in highlights[0]:
            # New grouped format - audio segments with related visuals
            context_parts = []
            context_parts.append("CONTEXT: You are analyzing a video where audio (speech) and visual elements occur simultaneously.")
            context_parts.append("The following data shows what was SAID (audio) and what was SEEN (visual) at the same time periods.")
            context_parts.append("Use both the speech content and visual descriptions to provide a complete understanding.\n")
            
            for i, segment in enumerate(highlights):
                audio = segment['audio_segment']
                visuals = segment['related_visuals']
                
                # Add audio segment with clear context
                context_parts.append(f"TIME PERIOD {i+1} ({audio['timestamp']:.1f}s-{audio.get('end_timestamp', 'N/A')}s):")
                context_parts.append(f"  SPEECH: \"{audio['description']}\"")
                
                # Add related visuals with clear context
                if visuals:
                    context_parts.append(f"  VISUAL SCENE during this speech:")
                    for j, visual in enumerate(visuals):
                        context_parts.append(f"    - At {visual['timestamp']:.1f}s: {visual['description']}")
                else:
                    context_parts.append(f"  VISUAL SCENE: No visual data available for this time period")
                context_parts.append("")  # Empty line for readability
            
            context = "\n".join(context_parts)
            prompt = f"""You are a video analysis assistant. Your mission is to understand and explain what happened in a video by combining both what was spoken (audio) and what was visible (visual elements).

When you receive data with timestamps, the audio and visual elements from the same time period are connected - they show what the speaker was saying while specific things were happening on screen.

{context}

Based on this synchronized audio-visual information, provide a factual response that connects what was said with what was seen:"""
        else:
            # Simple format - handle based on data type
            if data_type == "visual":
                context = "\n".join([f"At {h['timestamp']:.1f}s: {h['description']}" for h in highlights])
                prompt = f"""You are a video analysis assistant specializing in visual content analysis. Your mission is to analyze what can be seen in video frames and describe visual elements, objects, people, actions, and scenes.

The following are visual descriptions from specific moments in the video:

{context}

Based on these visual observations, provide a factual response about what was seen:"""
            
            elif data_type == "audio":
                context = "\n".join([f"At {h['timestamp']:.1f}s-{h.get('end_timestamp', 'N/A')}s: \"{h['description']}\"" for h in highlights])
                prompt = f"""You are a video analysis assistant specializing in audio content analysis. Your mission is to analyze speech and dialogue from videos, understanding what was said, by whom, and in what context.

The following are speech segments from the video with their timestamps:

{context}

Based on these speech segments, provide a factual response about what was said:"""
            
            elif data_type == "summary":
                # For summary questions, we receive the pre-generated comprehensive summary
                summary_content = highlights[0]['description'] if highlights else "No summary available"
                prompt = f"""You are a video analysis assistant. You have access to a comprehensive summary of a video. Your mission is to answer specific questions about the video content using this summary.

COMPREHENSIVE VIDEO SUMMARY:
{summary_content}

USER QUESTION: {highlights[0].get('user_question', 'Please provide information about this video.')}

Based on the comprehensive summary above, provide a focused answer to the user's specific question. If the question asks for general information, provide an overview. If it asks for specific details, extract and focus on those particular aspects from the summary."""
            
            else:
                # Fallback for unknown data type
                context = "\n".join([f"Timestamp: {h['timestamp']}, Description: {h['description']}, Summary: {h.get('summary', '')}" for h in highlights])
                prompt = f"""You are a video analysis assistant. Analyze the following video content and provide a factual response:

{context}

Response:"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.6,
                    max_output_tokens=200
                )
            )
            return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while generating the response. Please try again."

    def generate_summary(self, highlights, video_data):
        """Generate a comprehensive video summary using all available data"""
        try:
            # Separate audio and visual highlights
            audio_highlights = [h for h in highlights if h.get('end_timestamp')]
            visual_highlights = [h for h in highlights if not h.get('end_timestamp')]
            
            # Format audio transcript
            audio_text = ""
            if audio_highlights:
                audio_segments = []
                for h in sorted(audio_highlights, key=lambda x: x['timestamp']):
                    audio_segments.append(f"[{h['timestamp']:.1f}s-{h.get('end_timestamp', 'N/A')}s]: {h['description']}")
                audio_text = "\n".join(audio_segments)
            
            # Format visual descriptions
            visual_text = ""
            if visual_highlights:
                visual_scenes = []
                for h in sorted(visual_highlights, key=lambda x: x['timestamp']):
                    visual_scenes.append(f"[{h['timestamp']:.1f}s]: {h['description']}")
                visual_text = "\n".join(visual_scenes)
            
            # Create comprehensive summary prompt
            prompt = f"""You are a video summarization expert. Create a comprehensive summary of this video.

VIDEO METADATA:
- Duration: {video_data.get('duration', 'Unknown')} seconds
- Total visual scenes: {len(visual_highlights)}
- Total speech segments: {len(audio_highlights)}

COMPLETE AUDIO TRANSCRIPT:
{audio_text if audio_text else "No audio content available"}

VISUAL SCENES THROUGHOUT VIDEO:
{visual_text if visual_text else "No visual descriptions available"}

Based on this complete information, provide a comprehensive summary that covers:
1. Main topic and theme
2. Key points discussed or presented
3. Visual context and setting
4. Overall narrative, message, or purpose

Keep the summary informative but concise (2-3 paragraphs maximum)."""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4,  # Lower temperature for more factual summaries
                    max_output_tokens=400  # Allow longer summaries
                )
            )
            return response.text
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "I apologize, but I encountered an error while generating the video summary."