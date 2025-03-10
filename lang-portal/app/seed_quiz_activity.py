from app import create_app, db
from app.models import StudyActivity

def seed_quiz_activity():
    """Add the Multiple Choice Quiz activity to the database."""
    app = create_app()
    
    with app.app_context():
        # Check if the activity already exists
        existing_activity = StudyActivity.query.filter_by(name='Multiple Choice Quiz').first()
        
        if not existing_activity:
            # Create the new activity
            quiz_activity = StudyActivity(
                name='Multiple Choice Quiz',
                description='Test your knowledge with multiple-choice questions generated using Google Gemini 2.0 Flash. Practice vocabulary and grammar with interactive quizzes.',
                thumbnail_url='/static/images/quiz-icon.png'
            )
            
            db.session.add(quiz_activity)
            db.session.commit()
            print('Multiple Choice Quiz activity added successfully!')
        else:
            print('Multiple Choice Quiz activity already exists.')

if __name__ == '__main__':
    seed_quiz_activity()
