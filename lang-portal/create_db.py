from app import create_app
from app.models import db, StudyActivity

app = create_app()

with app.app_context():
    db.drop_all()  # Drop existing tables
    db.create_all()  # Create new tables
    
    # Create default study activities
    default_activities = [
        StudyActivity(
            name="Flashcards",
            description="Practice vocabulary with interactive flashcards",
            thumbnail_url="https://example.com/flashcards.jpg"
        ),
        StudyActivity(
            name="Multiple Choice",
            description="Test your knowledge with multiple choice questions",
            thumbnail_url="https://example.com/quiz.jpg"
        ),
        StudyActivity(
            name="Writing Practice",
            description="Improve your writing skills with guided exercises",
            thumbnail_url="https://example.com/writing.jpg"
        )
    ]
    
    for activity in default_activities:
        db.session.add(activity)
    
    db.session.commit()
    print("Database tables and default study activities created successfully!")
