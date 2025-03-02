import json
import os
from typing import Dict, List, Optional, Any
from backend.vector_store import QuestionVectorStore
import google.generativeai as genai
from dotenv import load_dotenv
from backend.structured_data import TranscriptStructurer

# Load environment variables from .env file
load_dotenv()

class QuestionGenerator:
    def __init__(self):
        """Initialize vector store and Gemini model"""
        self.vector_store = QuestionVectorStore()
        self.transcript_structurer = TranscriptStructurer()
        
        # Initialize Gemini 2.0 Flash with API key from .env
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in the .env file.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def _invoke_gemini(self, prompt: str) -> Optional[str]:
        """Invoke Gemini with the given prompt"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error invoking Gemini: {e}")
            return None

    def generate_similar_question(self, section_num: int, topic: str) -> Dict:
        """Generate a new question similar to existing ones on a given topic"""
        # Get similar questions for context
        similar_questions = self.vector_store.search_similar_questions(section_num, topic, n_results=3)
        
        if not similar_questions:
            return None
        
        # Create context from similar questions
        context = "Here are some example JLPT listening questions:\\n\\n"
        for idx, q in enumerate(similar_questions, 1):
            if section_num == 2:
                context += f"Example {idx}:\\n"
                context += f"Introduction: {q.get('Introduction', '')}\\n"
                context += f"Conversation: {q.get('Conversation', '')}\\n"
                context += f"Question: {q.get('Question', '')}\\n"
                if 'Options' in q:
                    context += "Options:\\n"
                    for i, option in enumerate(q['Options'], 1):
                        context += f"{i}. {option}\\n"
            elif section_num == 3:
                context += f"Example {idx}:\\n"
                context += f"Situation: {q.get('Situation', '')}\\n"
                context += f"Question: {q.get('Question', '')}\\n"
        
        # Generate prompt for Gemini
        prompt = f"Generate a new JLPT listening question similar to these examples:\\n\\n{context}\\n\\nThe new question should also be about the topic: {topic}."
        
        # Invoke Gemini to generate the question
        new_question_text = self._invoke_gemini(prompt)
        
        # Parse the generated question text
        if new_question_text:
            try:
                new_question = json.loads(new_question_text)
                return new_question
            except json.JSONDecodeError:
                print(f"Error decoding JSON: {new_question_text}")
                return None
        else:
            return None
            
    def generate_french_exercise(self, topic: str) -> Dict[str, Any]:
        """Generate a French conversation and question based on the given topic"""
        return self.transcript_structurer.generate_french_exercise(topic)

    def get_feedback(self, question: Dict, selected_answer: int) -> Dict:
        """
        Generate feedback for the user's answer using Gemini
        
        Args:
            question: The question dictionary
            selected_answer: The index of the selected answer (1-based)
            
        Returns:
            A dictionary containing feedback information:
            {
                'correct': bool,
                'correct_answer': int,
                'explanation': str
            }
        """
        # Determine the correct answer (for demo purposes, we'll use Gemini to determine this)
        prompt = f"""
        Analyze this JLPT listening question and determine the correct answer.
        
        Question:
        {json.dumps(question, ensure_ascii=False, indent=2)}
        
        The user selected answer #{selected_answer}.
        
        Provide your response in the following JSON format:
        {{
            "correct": true/false,
            "correct_answer": [number between 1-4],
            "explanation": "Detailed explanation in English of why the answer is correct/incorrect"
        }}
        
        Make sure your response is valid JSON.
        """
        
        feedback_text = self._invoke_gemini(prompt)
        
        if feedback_text:
            try:
                feedback = json.loads(feedback_text)
                return feedback
            except json.JSONDecodeError:
                print(f"Error decoding feedback JSON: {feedback_text}")
                # Return a default feedback if parsing fails
                return {
                    "correct": False,
                    "correct_answer": 1,
                    "explanation": "Sorry, I couldn't analyze your answer properly. Please try again."
                }
        else:
            return {
                "correct": False,
                "correct_answer": 1,
                "explanation": "Sorry, I couldn't generate feedback for your answer. Please try again."
            }