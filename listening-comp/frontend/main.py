import streamlit as st
import sys
import os
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.question_generator import QuestionGenerator
from backend.audio_generator import AudioGenerator

# Page config
st.set_page_config(
    page_title="French Listening Practice",
    page_icon="🎧",
    layout="wide"
)

def load_stored_questions():
    """Load previously stored questions from JSON file"""
    questions_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "backend", "data", "saved_questions.json"
    )
    
    if os.path.exists(questions_file):
        try:
            with open(questions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading questions: {e}")
    
    return {}

def save_question(question, practice_type, topic, audio_file=None):
    """Save a generated question to JSON file"""
    questions_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "backend", "data", "saved_questions.json"
    )
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(questions_file), exist_ok=True)
    
    # Load existing questions
    stored_questions = {}
    if os.path.exists(questions_file):
        try:
            with open(questions_file, 'r', encoding='utf-8') as f:
                stored_questions = json.load(f)
        except Exception as e:
            print(f"Error loading questions: {e}")
    
    # Create unique ID for the question
    question_id = f"{practice_type.replace(' ', '-')}_{topic.replace(' ', '-')}_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}"
    
    # Add new question
    stored_questions[question_id] = {
        "question": question,
        "practice_type": practice_type,
        "topic": topic,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "audio_file": audio_file
    }
    
    # Save to file
    try:
        with open(questions_file, 'w', encoding='utf-8') as f:
            json.dump(stored_questions, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving questions: {e}")

def render_interactive_stage():
    """Render the interactive learning stage"""
    # Initialize session state
    if 'question_generator' not in st.session_state:
        st.session_state.question_generator = QuestionGenerator()
    if 'audio_generator' not in st.session_state:
        st.session_state.audio_generator = AudioGenerator()
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'feedback' not in st.session_state:
        st.session_state.feedback = None
    if 'current_practice_type' not in st.session_state:
        st.session_state.current_practice_type = None
    if 'current_topic' not in st.session_state:
        st.session_state.current_topic = None
    if 'current_audio' not in st.session_state:
        st.session_state.current_audio = None
    if 'user_answer' not in st.session_state:
        st.session_state.user_answer = None
    if 'correct_answer' not in st.session_state:
        st.session_state.correct_answer = None
    if 'show_result' not in st.session_state:
        st.session_state.show_result = False
        
    # Load stored questions for sidebar
    stored_questions = load_stored_questions()
    
    # Create sidebar
    with st.sidebar:
        st.header("Saved Questions")
        if stored_questions:
            for qid, qdata in stored_questions.items():
                # Create a button for each question
                button_label = f"{qdata['practice_type']} - {qdata['topic']}\n{qdata['created_at']}"
                if st.button(button_label, key=qid):
                    st.session_state.current_question = qdata['question']
                    st.session_state.current_practice_type = qdata['practice_type']
                    st.session_state.current_topic = qdata['topic']
                    st.session_state.current_audio = qdata.get('audio_file')
                    st.session_state.feedback = None
                    st.session_state.user_answer = None
                    st.session_state.correct_answer = None
                    st.session_state.show_result = False
                    st.rerun()
        else:
            st.info("No saved questions yet. Generate some questions to see them here!")
    
    # Practice type selection
    practice_type = st.selectbox(
        "Select Practice Type",
        ["Dialogue Practice"]
    )
    
    # Topic selection
    topics = {
        "Dialogue Practice": ["Daily Conversation", "Shopping", "Restaurant", "Travel", "School/Work"]
    }
    
    topic = st.selectbox(
        "Select Topic",
        topics[practice_type]
    )
    
    # Generate new question button
    if st.button("Generate New Question"):
        # Generate a French exercise
        exercise = st.session_state.question_generator.generate_french_exercise(topic)
        
        # Store the exercise in session state
        st.session_state.current_question = exercise
        st.session_state.current_practice_type = practice_type
        st.session_state.current_topic = topic
        st.session_state.feedback = None
        st.session_state.user_answer = None
        st.session_state.correct_answer = exercise.get("correct_answer", "")
        st.session_state.show_result = False
        
        # Generate audio for the conversation
        conversation_text = exercise.get("conversation", "")
        if conversation_text:
            # Temporarily disable audio generation
            # audio_file = st.session_state.audio_generator.generate_audio(
            #     conversation_text, 
            #     voice_name="fr-FR-Neural2-A"  # French voice
            # )
            # st.session_state.current_audio = audio_file
            
            # Save question to file without audio
            save_question(exercise, practice_type, topic)
        
        st.rerun()
    
    # Display current question
    if st.session_state.current_question:
        exercise = st.session_state.current_question
        
        # Display conversation
        st.subheader("Conversation")
        st.markdown(f"```\n{exercise.get('conversation', '')}\n```")
        
        # Display audio player if available
        if st.session_state.current_audio:
            # Temporarily disable audio player
            # st.audio(st.session_state.current_audio)
            st.info("Audio playback is temporarily disabled.")
        else:
            st.info("Audio playback is temporarily disabled.")
        
        # Display question
        st.subheader("Question")
        st.markdown(f"**{exercise.get('question', '')}**")
        
        # Display options and handle user selection
        st.subheader("Options")
        options_text = exercise.get("options", "")
        options = []
        
        # Parse options from text
        for line in options_text.split("\n"):
            if line.strip():
                options.append(line.strip())
        
        # Display radio buttons for options
        if options and not st.session_state.show_result:
            selected_option = st.radio("Select your answer:", options, key="option_selection")
            
            # Check answer button
            if st.button("Check Answer"):
                # Get the letter of the selected option (a, b, c, or d)
                selected_index = options.index(selected_option)
                selected_letter = chr(97 + selected_index)  # 97 is ASCII for 'a'
                
                st.session_state.user_answer = selected_letter
                st.session_state.show_result = True
                st.rerun()
        
        # Show result if user has submitted an answer
        if st.session_state.show_result:
            correct_letter = st.session_state.correct_answer
            user_letter = st.session_state.user_answer
            
            if user_letter == correct_letter:
                st.success("Correct! 🎉")
            else:
                st.error(f"Wrong! The correct answer is {correct_letter}.")
            
            # Try again button
            if st.button("Try Another Question"):
                st.session_state.show_result = False
                st.session_state.user_answer = None
                st.rerun()
    else:
        st.info("Click 'Generate New Question' to start practicing!")

def main():
    st.title("French Listening Practice")
    render_interactive_stage()

if __name__ == "__main__":
    main()
