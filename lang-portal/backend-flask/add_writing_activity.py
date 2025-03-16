from app import create_app, db
from app.models import StudyActivity

app = create_app()

with app.app_context():
    # Check if Writing Practice activity already exists
    existing = StudyActivity.query.filter_by(name="Writing Practice").first()
    
    if not existing:
        # Create the Writing Practice activity
        writing_activity = StudyActivity(
            name="Writing Practice",
            description="Practice your French writing skills with AI-powered feedback. Choose from various prompts and receive detailed analysis of your writing using Google Gemini 2.0 Flash.",
            icon="edit"
        )
        
        db.session.add(writing_activity)
        db.session.commit()
        
        print(f"Added Writing Practice activity with ID: {writing_activity.id}")
    else:
        print(f"Writing Practice activity already exists with ID: {existing.id}")
