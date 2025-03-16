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
print(f"Google API Key available: {bool(api_key)}")

# Configure the Gemini API if API key is available
if api_key:
    try:
        genai.configure(api_key=api_key)
        print("Successfully configured Google Generative AI")
    except Exception as e:
        print(f"Error configuring Google Generative AI: {str(e)}")
else:
    print("WARNING: No Google API key found. Using mock questions instead.")

def generate_quiz_question(words, focus_area=None):
    """Generate a multiple-choice question using Google Gemini."""
    # Check if API key is available
    if not api_key:
        print("Using mock question due to missing API key")
        # Return a mock question if no API key is available
        return {
            "question": "What is the French word for 'hello'?",
            "options": ["Bonjour", "Au revoir", "Merci", "S'il vous plaît"],
            "correct_answer": "Bonjour",
            "explanation": "Bonjour means 'hello' or 'good day' in French."
        }
    
    # Select a subset of words if there are many
    if len(words) > 5:
        selected_words = random.sample(words, 5)
    else:
        selected_words = words
    
    word_str = ", ".join([f"{word['french']} ({word['english']})" for word in selected_words])
    
    # Choose a focus area if not provided
    focus_areas = ["vocabulary usage", "grammar", "translation", "word meaning"]
    if not focus_area:
        focus_area = random.choice(focus_areas)
    
    # Create the prompt
    prompt = f"""You are a French language quiz generator. Create a multiple-choice question based on the following vocabulary words:
    
    {word_str}
    
    Focus on {focus_area}.
    
    The question should be challenging but fair, with 4 possible answers where only one is correct.
    
    Format your response as a JSON object with the following structure:
    ```json
    {{
        "question": "The question text in English",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer": "The correct option exactly as it appears in the options array",
        "explanation": "A brief explanation of why the answer is correct"
    }}
    
    Make sure the options are distinct and plausible. The correct_answer must be exactly one of the options.
    """
    
    try:
        # Generate the question using Gemini
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
        
        question_data = json.loads(json_str)
        return question_data
    except Exception as e:
        print(f"Error parsing question: {e}")
        # Return a default structure if parsing fails
        return {
            "question": "What is the French word for 'hello'?",
            "options": ["Bonjour", "Au revoir", "Merci", "S'il vous plaît"],
            "correct_answer": "Bonjour",
            "explanation": "Bonjour means 'hello' or 'good day' in French."
        }

def generate_quiz(words: List[Dict], question_count: int = 10) -> Dict:
    """Generate a quiz with the specified number of questions."""
    # Check if API key is available and provide a warning
    if not api_key:
        print("Warning: No Google API key found. Using mock quiz questions.")
    
    questions = []
    focus_areas = ["vocabulary usage", "grammar", "translation", "word meaning"]
    
    # Generate the requested number of questions
    for i in range(question_count):
        focus_area = focus_areas[i % len(focus_areas)]  # Cycle through focus areas
        question = generate_quiz_question(words, focus_area)
        questions.append(question)
    
    # Return the quiz state
    return {
        "questions": questions,
        "correct_count": 0,
        "incorrect_count": 0
    }

def check_answer(quiz_state: Dict, question_index: int, selected_answer: str) -> Dict:
    """Check if the selected answer is correct."""
    if question_index >= len(quiz_state.get("questions", [])):
        return {"error": "Invalid question index"}
    
    question = quiz_state["questions"][question_index]
    is_correct = selected_answer == question["correct_answer"]
    
    # Update the question with the user's answer
    question["user_answer"] = selected_answer
    question["is_correct"] = is_correct
    quiz_state["questions"][question_index] = question
    
    # Update the quiz statistics
    quiz_state["correct_count"] = sum(1 for q in quiz_state["questions"] if q.get("is_correct", False))
    quiz_state["incorrect_count"] = sum(1 for q in quiz_state["questions"] if "is_correct" in q and not q["is_correct"])
    
    return quiz_state

def get_quiz_summary(quiz_state: Dict) -> Dict:
    """Get a summary of the quiz results."""
    questions = quiz_state.get("questions", [])
    total_questions = len(questions)
    answered_questions = sum(1 for q in questions if "user_answer" in q)
    correct_answers = sum(1 for q in questions if q.get("is_correct", False))
    
    if answered_questions == 0:
        accuracy = 0
    else:
        accuracy = (correct_answers / answered_questions) * 100
    
    return {
        "total_questions": total_questions,
        "answered_questions": answered_questions,
        "correct_answers": correct_answers,
        "accuracy": round(accuracy, 2),
        "questions": questions
    }
