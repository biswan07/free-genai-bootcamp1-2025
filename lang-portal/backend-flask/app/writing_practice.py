import os
import json
import random
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv
from flask import jsonify

# Load environment variables
load_dotenv()

# Get the API key
api_key = os.getenv("GOOGLE_API_KEY")
print(f"Google API Key available for Writing Practice: {bool(api_key)}")

# Configure the Gemini API if API key is available
if api_key:
    try:
        genai.configure(api_key=api_key)
        print("Successfully configured Google Generative AI for Writing Practice")
    except Exception as e:
        print(f"Error configuring Google Generative AI: {str(e)}")
else:
    print("WARNING: No Google API key found for Writing Practice. Using mock prompts instead.")

def generate_writing_prompts(count=10, language_level="intermediate"):
    """Generate a list of writing prompts using Google Gemini."""
    # Check if API key is available
    if not api_key:
        print("Using mock writing prompts due to missing API key")
        # Return mock prompts if no API key is available
        return [
            "Write a short letter to a friend about your vacation",
            "Describe your favorite restaurant and why you like it",
            "Write about your daily routine",
            "Describe your hometown to someone who has never been there",
            "Write about your favorite hobby",
            "Describe your family members",
            "Write about a memorable trip you took",
            "Describe your ideal job",
            "Write about your favorite season and why you like it",
            "Describe a person who has influenced you"
        ][:count]
    
    # Create the prompt
    prompt = f"""You are a French language teacher. Create {count} writing prompts for {language_level} level French students.
    
    The prompts should be suitable for short essays (50-200 words) and should encourage students to practice their French writing skills.
    
    Format your response as a JSON array of strings, where each string is a writing prompt in English.
    
    Example:
    ```json
    [
        "Write a short letter to a friend about your vacation",
        "Describe your favorite restaurant and why you like it"
    ]
    ```
    
    Make the prompts diverse, covering different topics like daily life, culture, travel, education, work, etc.
    """
    
    try:
        # Generate the prompts using Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        # Extract the JSON from the response
        response_text = response.text
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].strip()
        else:
            json_str = response_text
        
        prompts = json.loads(json_str)
        return prompts[:count]  # Ensure we only return the requested number
    except Exception as e:
        print(f"Error generating writing prompts: {e}")
        # Return default prompts if generation fails
        return [
            "Write a short letter to a friend about your vacation",
            "Describe your favorite restaurant and why you like it",
            "Write about your daily routine",
            "Describe your hometown to someone who has never been there",
            "Write about your favorite hobby",
            "Describe your family members",
            "Write about a memorable trip you took",
            "Describe your ideal job",
            "Write about your favorite season and why you like it",
            "Describe a person who has influenced you"
        ][:count]

def evaluate_writing(prompt: str, text: str, language_level="intermediate") -> Dict:
    """Evaluate a writing submission using Google Gemini."""
    # Check if API key is available
    if not api_key:
        print("Using mock evaluation due to missing API key")
        # Return a mock evaluation if no API key is available
        return {
            "score": 85,
            "feedback": {
                "strengths": [
                    "Good vocabulary usage",
                    "Clear structure"
                ],
                "areas_for_improvement": [
                    "Some grammar errors",
                    "Could use more complex sentence structures"
                ],
                "detailed_analysis": "Your writing shows a good understanding of the topic. You've used appropriate vocabulary and maintained a clear structure. There are some minor grammar errors that could be improved. Try to incorporate more complex sentence structures to elevate your writing."
            }
        }
    
    # Create the prompt
    evaluation_prompt = f"""You are a French language teacher evaluating a student's writing. 
    
    The student is at a {language_level} level and was given the following prompt:
    "{prompt}"
    
    Here is the student's submission:
    ```
    {text}
    ```
    
    Please evaluate the writing and provide feedback. Format your response as a JSON object with the following structure:
    ```json
    {{
        "score": 85,
        "feedback": {{
            "strengths": [
                "Point 1",
                "Point 2"
            ],
            "areas_for_improvement": [
                "Point 1",
                "Point 2"
            ],
            "detailed_analysis": "A paragraph providing detailed analysis of the writing, including specific examples and suggestions for improvement."
        }}
    }}
    ```
    
    The score should be a number between 0 and 100, representing the overall quality of the writing.
    Provide 2-4 specific strengths and 2-4 specific areas for improvement.
    The detailed analysis should be 3-5 sentences long and provide constructive feedback.
    """
    
    try:
        # Generate the evaluation using Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(evaluation_prompt)
        
        # Extract the JSON from the response
        response_text = response.text
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].strip()
        else:
            json_str = response_text
        
        evaluation = json.loads(json_str)
        return evaluation
    except Exception as e:
        print(f"Error evaluating writing: {e}")
        # Return a default evaluation if parsing fails
        return {
            "score": 70,
            "feedback": {
                "strengths": [
                    "Attempted to address the prompt",
                    "Basic vocabulary usage"
                ],
                "areas_for_improvement": [
                    "Grammar and syntax errors",
                    "Limited vocabulary range",
                    "Structure could be improved"
                ],
                "detailed_analysis": "Your submission shows an understanding of the topic, but there are several areas that need improvement. Focus on grammar rules and expanding your vocabulary. Try to organize your thoughts more clearly with an introduction, body, and conclusion."
            }
        }
