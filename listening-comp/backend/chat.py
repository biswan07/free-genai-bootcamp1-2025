# Create GeminiChat
# gemini_chat.py
import google.generativeai as genai
import streamlit as st
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Model name
MODEL_NAME = "gemini-2.0-flash"

class GeminiChat:
    def __init__(self, model_name: str = MODEL_NAME):
        """Initialize Gemini chat client"""
        self.model = genai.GenerativeModel(model_name)

    def generate_response(self, message: str, inference_config: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Generate a response using Google Gemini"""
        if inference_config is None:
            inference_config = {"temperature": 0.7}
        
        try:
            response = self.model.generate_content(
                message,
                generation_config=inference_config
            )
            return response.text
            
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return None


if __name__ == "__main__":
    chat = GeminiChat()
    while True:
        user_input = input("You: ")
        if user_input.lower() == '/exit':
            break
        response = chat.generate_response(user_input)
        print("Bot:", response)
