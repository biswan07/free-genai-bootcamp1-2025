import pytest
import json
from app.models import Word, Group, StudyActivity, StudySession

def test_get_words(client, test_database):
    """Test getting all words."""
    # Create test word
    word = Word(french='bonjour', english='hello', parts='{"part_of_speech": "interjection"}')
    test_database.session.add(word)
    test_database.session.commit()
    
    response = client.get('/api/words')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
    assert 'french' in data[0]
    assert data[0]['french'] == 'bonjour'

def test_create_word(client, test_database):
    """Test creating a new word."""
    word_data = {
        'french': 'chat',
        'english': 'cat',
        'parts': {'part_of_speech': 'noun'}
    }
    response = client.post('/api/words',
                         data=json.dumps(word_data),
                         content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['french'] == 'chat'
    assert data['english'] == 'cat'
    assert data['parts']['part_of_speech'] == 'noun'

def test_get_groups(client, test_database):
    """Test getting all groups."""
    # Create test group
    group = Group(name='Test Group')
    test_database.session.add(group)
    test_database.session.commit()
    
    response = client.get('/api/groups')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
    assert 'name' in data[0]
    assert data[0]['name'] == 'Test Group'

def test_create_study_session(client, test_database):
    """Test creating a new study session."""
    # Create test group and activity first
    group = Group(name='Test Group')
    test_database.session.add(group)
    test_database.session.commit()
    
    activity = StudyActivity(
        name='Test Activity',
        description='Test Description',
        group_id=group.id
    )
    test_database.session.add(activity)
    test_database.session.commit()
    
    session_data = {
        'group_id': group.id,
        'study_activity_id': activity.id
    }
    response = client.post('/api/study-sessions',
                         data=json.dumps(session_data),
                         content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['group_id'] == group.id
    assert data['study_activity_id'] == activity.id

def test_add_word_review(client, test_database):
    """Test adding a word review."""
    # Create test word, group, activity, and session first
    word = Word(french='test', english='test')
    test_database.session.add(word)
    test_database.session.commit()
    
    group = Group(name='Test Group')
    test_database.session.add(group)
    test_database.session.commit()
    
    activity = StudyActivity(
        name='Test Activity',
        description='Test Description',
        group_id=group.id
    )
    test_database.session.add(activity)
    test_database.session.commit()
    
    session = StudySession(
        group_id=group.id,
        study_activity_id=activity.id
    )
    test_database.session.add(session)
    test_database.session.commit()
    
    review_data = {
        'word_id': word.id,
        'study_session_id': session.id,
        'correct': True
    }
    response = client.post('/api/word-reviews',
                         data=json.dumps(review_data),
                         content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['word_id'] == word.id
    assert data['study_session_id'] == session.id
    assert data['correct'] is True
