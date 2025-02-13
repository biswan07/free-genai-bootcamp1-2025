import pytest
from app import create_app
from app.models import db, Word, Group, StudySession, StudyActivity, WordReviewItem

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def test_database(app):
    """Create a fresh database for each test."""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def populated_test_database(app):
    """Create test database with sample data."""
    with app.app_context():
        # Create sample word
        word = Word(french='bonjour', english='hello', parts='{"part_of_speech": "interjection"}')
        db.session.add(word)
        
        # Create sample group
        group = Group(name='Greetings')
        db.session.add(group)
        
        # Add word to group
        group.words.append(word)
        
        # Create study activity
        activity = StudyActivity(
            name='Basic Greetings Quiz',
            description='Practice basic greeting words',
            group_id=1
        )
        db.session.add(activity)
        db.session.flush()  # Get the activity ID
        
        # Create study session
        study_session = StudySession(
            group_id=1,
            study_activity_id=activity.id
        )
        db.session.add(study_session)
        
        # Create word review
        word_review = WordReviewItem(
            word_id=1,
            study_session_id=1,
            correct=True
        )
        db.session.add(word_review)
        
        db.session.commit()
        
        yield db
