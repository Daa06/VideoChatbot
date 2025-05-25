from src.llm.gemini_chat import GeminiChat

class QueryClassifier:
    def __init__(self, gemini_chat: GeminiChat):
        self.gemini_chat = gemini_chat
    
    def classify_query(self, user_question: str) -> str:
        """Classify if question needs visual, audio, or both data"""
        
        classification_prompt = f"""
        CONTEXT: You are helping a video analysis system decide which type of data to search through to answer a user's question.

        SYSTEM EXPLANATION:
        - We have a video that has been processed into different types of data:
          1. VISUAL DATA: Descriptions of what can be seen in each frame (people, objects, actions, scenes, clothing, facial expressions, etc.)
          2. AUDIO DATA: Speech-to-text transcription of what was said in the video (dialogue, narration, spoken words)
          3. SUMMARY DATA: A comprehensive summary of the entire video covering main topics, key points, and overall narrative
        
        - The user will ask questions about the video content
        - We need to search the most relevant data type to give accurate answers
        - Searching the right data type improves accuracy and speed

        YOUR TASK: Analyze the user's question and determine which data type(s) are needed to answer it accurately.

        CLASSIFICATION RULES WITH EXAMPLES:
        
        Choose "summary" for GENERAL questions about the entire video:
        - "What is the main topic?"
        - "Summarize this video"
        - "What is this video about?"
        - "Give me an overview"
        - "What's the general theme?"
        - "What happens in this video?"
        - "Tell me about this video"
        - "What's the content of this video?"
        
        Choose "visual" ONLY if the question is specifically about what can be SEEN:
        - "What is the man wearing?"
        - "What color is his shirt?"
        - "How many people are in the scene?"
        - "What objects are visible?"
        - "What does he look like?"
          
        Choose "audio" ONLY if the question is specifically about what was SAID or HEARD:
        - "What did he say?"
        - "What are they talking about?"
        - "What was mentioned about...?"
        - "What words did he use?"
        - "What was the dialogue?"
        
        Choose "both" for questions that need CONTEXT from specific moments:
        - "What happened when he mentioned Athens?" (needs both visual context and spoken content from that moment)
        - "Describe the scene when he said..." (needs both what was seen and said at that time)

        IMPORTANT: 
        - For GENERAL questions about the whole video → summary
        - For SPECIFIC visual details → visual
        - For SPECIFIC speech content → audio  
        - For SPECIFIC moments combining both → both

        USER QUESTION: "{user_question}"

        Think step by step:
        1. Is this asking for a general overview/summary of the entire video? → summary
        2. Is this asking specifically about what can be SEEN? → visual
        3. Is this asking specifically about what was SAID? → audio  
        4. Is this asking about a SPECIFIC MOMENT with both visual and audio? → both

        Respond with EXACTLY ONE word: summary, visual, audio, or both

        Answer:"""
        
        try:
            response = self.gemini_chat.generate_response_simple(classification_prompt)
            
            # Clean and validate response
            classification = response.strip().lower()
            if classification in ["visual", "audio", "both", "summary"]:
                print(f"Classification result: '{user_question}' → {classification}")
                return classification
            else:
                print(f"Invalid classification response: {response}, defaulting to 'both'")
                return "both"  # Default fallback
        except Exception as e:
            print(f"Error in query classification: {e}")
            return "both"  # Fallback on error 