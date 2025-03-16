import pytest
from app import create_app, db
from app.models import Word, Group, StudySession, StudyActivity, WordReviewItem

@pytest.fixture
def app():
    """Create application for the tests."""
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def _db(app):
    """Create database for the tests."""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_database(_db):
    """Create a fresh test database."""
    return _db

@pytest.fixture
def populated_test_database(_db):
    """Create a test database populated with sample data."""
    # Create sample words
    word1 = Word(french='bonjour', english='hello', parts={'part_of_speech': 'interjection'})
    _db.session.add(word1)
    _db.session.flush()
    
    # Create sample groups
    group1 = Group(name='Basic Greetings')
    _db.session.add(group1)
    _db.session.flush()
    
    # Add words to groups
    group1.words.append(word1)
    
    # Create sample study activities
    activity1 = StudyActivity(name='Flashcards', group_id=group1.id)
    _db.session.add(activity1)
    _db.session.flush()
    
    # Create sample study sessions
    session1 = StudySession(group_id=group1.id, study_activity_id=activity1.id)
    _db.session.add(session1)
    _db.session.flush()
    
    # Create sample word reviews
    review1 = WordReviewItem(word_id=word1.id, study_session_id=session1.id, is_correct=True)
    _db.session.add(review1)
    _db.session.commit()
    
    return _db
