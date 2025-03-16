from typing import Optional, Dict, List, Any
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Model name
MODEL_NAME = "gemini-2.0-flash"

class TranscriptStructurer:
    def __init__(self, model_name: str = MODEL_NAME):
        """Initialize Gemini model"""
        self.model = genai.GenerativeModel(model_name)
        self.french_prompt = """Generate a French conversation about {topic} between two people. 
        The conversation should be 5-8 lines long and be suitable for intermediate French learners.
        
        Then create a question about the conversation with 4 multiple-choice answers (a, b, c, d).
        Only ONE answer should be correct.
        
        Format your response exactly like this:
        
        <conversation>
        Person 1: [French text]
        Person 2: [French text]
        Person 1: [French text]
        ...
        </conversation>
        
        <question>
        [Question in French]
        </question>
        
        <options>
        a) [Option 1 in French]
        b) [Option 2 in French]
        c) [Option 3 in French]
        d) [Option 4 in French]
        </options>
        
        <correct_answer>
        [The correct letter (a, b, c, or d)]
        </correct_answer>
        """

    def generate_french_exercise(self, topic: str) -> Dict[str, Any]:
        """Generate a French conversation and question based on the given topic"""
        prompt = self.french_prompt.format(topic=topic)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.7}
            )
            
            result = response.text
            
            # Parse the response
            conversation = self._extract_section(result, "conversation")
            question = self._extract_section(result, "question")
            options = self._extract_section(result, "options")
            correct_answer = self._extract_section(result, "correct_answer")
            
            return {
                "conversation": conversation,
                "question": question,
                "options": options,
                "correct_answer": correct_answer.strip() if correct_answer else ""
            }
        except Exception as e:
            print(f"Error generating French exercise: {str(e)}")
            return {
                "conversation": "Error generating conversation.",
                "question": "",
                "options": "",
                "correct_answer": ""
            }
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a section from the generated text"""
        start_tag = f"<{section_name}>"
        end_tag = f"</{section_name}>"
        
        try:
            start_idx = text.index(start_tag) + len(start_tag)
            end_idx = text.index(end_tag)
            return text[start_idx:end_idx].strip()
        except ValueError:
            return ""

    # Keep the existing methods for backward compatibility
    def _invoke_gemini(self, prompt: str, transcript: str) -> Optional[str]:
        """Make a single call to Gemini with the given prompt"""
        full_prompt = f"{prompt}\n\nHere's the transcript:\n{transcript}"
        
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config={"temperature": 0}
            )
            return response.text
        except Exception as e:
            print(f"Error invoking Gemini: {str(e)}")
            return None

    def structure_transcript(self, transcript: str) -> Dict[int, str]:
        """Structure the transcript into three sections using separate prompts"""
        results = {}
        # Skipping section 1 for now
        for section_num in range(2, 4):
            result = self._invoke_gemini(self.prompts[section_num], transcript)
            if result:
                results[section_num] = result
        return results

    def save_questions(self, structured_sections: Dict[int, str], base_filename: str) -> bool:
        """Save each section to a separate file"""
        try:
            # Create questions directory if it doesn't exist
            os.makedirs(os.path.dirname(base_filename), exist_ok=True)
            
            # Save each section
            for section_num, content in structured_sections.items():
                filename = f"{os.path.splitext(base_filename)[0]}_section{section_num}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
            return True
        except Exception as e:
            print(f"Error saving questions: {str(e)}")
            return False

    def load_transcript(self, filename: str) -> Optional[str]:
        """Load transcript from a file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading transcript: {str(e)}")
            return None

    def prompts(self, section_num: int) -> str:
        """Return the prompt for the given section number"""
        prompts = {
            1: """Extract questions from section 問題1 of this JLPT transcript where the answer can be determined solely from the conversation without needing visual aids.
            
            ONLY include questions that meet these criteria:
            - The answer can be determined purely from the spoken dialogue
            - No spatial/visual information is needed (like locations, layouts, or physical appearances)
            - No physical objects or visual choices need to be compared
            
            For example, INCLUDE questions about:
            - Times and dates
            - Numbers and quantities
            - Spoken choices or decisions
            - Clear verbal directions
            
            DO NOT include questions about:
            - Physical locations that need a map or diagram
            - Visual choices between objects
            - Spatial arrangements or layouts
            - Physical appearances of people or things

            Format each question exactly like this:

            <question>
            Introduction:
            [the situation setup in japanese]
            
            Conversation:
            [the dialogue in japanese]
            
            Question:
            [the question being asked in japanese]

            Options:
            1. [first option in japanese]
            2. [second option in japanese]
            3. [third option in japanese]
            4. [fourth option in japanese]
            </question>

            Rules:
            - Only extract questions from the 問題1 section
            - Only include questions where answers can be determined from dialogue alone
            - Ignore any practice examples (marked with 例)
            - Do not translate any Japanese text
            - Do not include any section descriptions or other text
            - Output questions one after another with no extra text between them
            """,
            
            2: """Extract questions from section 問題2 of this JLPT transcript where the answer can be determined solely from the conversation without needing visual aids.
            
            ONLY include questions that meet these criteria:
            - The answer can be determined purely from the spoken dialogue
            - No spatial/visual information is needed (like locations, layouts, or physical appearances)
            - No physical objects or visual choices need to be compared
            
            For example, INCLUDE questions about:
            - Times and dates
            - Numbers and quantities
            - Spoken choices or decisions
            - Clear verbal directions
            
            DO NOT include questions about:
            - Physical locations that need a map or diagram
            - Visual choices between objects
            - Spatial arrangements or layouts
            - Physical appearances of people or things

            Format each question exactly like this:

            <question>
            Introduction:
            [the situation setup in japanese]
            
            Conversation:
            [the dialogue in japanese]
            
            Question:
            [the question being asked in japanese]
            </question>

            Rules:
            - Only extract questions from the 問題2 section
            - Only include questions where answers can be determined from dialogue alone
            - Ignore any practice examples (marked with 例)
            - Do not translate any Japanese text
            - Do not include any section descriptions or other text
            - Output questions one after another with no extra text between them
            """,
            
            3: """Extract all questions from section 問題3 of this JLPT transcript.
            Format each question exactly like this:

            <question>
            Situation:
            [the situation in japanese where a phrase is needed]
            
            Question:
            何と言いますか
            </question>

            Rules:
            - Only extract questions from the 問題3 section
            - Ignore any practice examples (marked with 例)
            - Do not translate any Japanese text
            - Do not include any section descriptions or other text
            - Output questions one after another with no extra text between them
            """
        }
        return prompts.get(section_num, "")

if __name__ == "__main__":
    structurer = TranscriptStructurer()
    transcript = structurer.load_transcript("backend/data/transcripts/sY7L5cfCWno.txt")
    if transcript:
        structured_sections = structurer.structure_transcript(transcript)
        structurer.save_questions(structured_sections, "backend/data/questions/sY7L5cfCWno.txt")