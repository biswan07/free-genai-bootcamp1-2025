import pytest
from flask import json
from app.models import Word, Group, StudySession, StudyActivity

def test_get_words_success(client, populated_test_database):
    """Test successful GET /api/words endpoint."""
    response = client.get('/api/words')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'items' in data
    assert 'pagination' in data
    assert len(data['items']) > 0
    assert all(key in data['items'][0] for key in ['id', 'french', 'english', 'parts'])

def test_create_word_success(client, test_database):
    """Test successful POST /api/words endpoint."""
    word_data = {
        'french': 'merci',
        'english': 'thank you',
        'parts': {'part_of_speech': 'interjection'}
    }
    response = client.post('/api/words', 
                          data=json.dumps(word_data),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['french'] == word_data['french']
    assert data['english'] == word_data['english']
    assert data['parts'] == word_data['parts']

def test_create_word_invalid_data(client, test_database):
    """Test POST /api/words with invalid data."""
    invalid_data = {'french': 'merci'}  # Missing required 'english' field
    response = client.post('/api/words', 
                          data=json.dumps(invalid_data),
                          content_type='application/json')
    assert response.status_code == 400

def test_get_groups_success(client, populated_test_database):
    """Test successful GET /api/groups endpoint."""
    response = client.get('/api/groups')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'items' in data
    assert 'pagination' in data
    assert len(data['items']) > 0
    assert all(key in data['items'][0] for key in ['id', 'name', 'word_count'])

def test_create_group_success(client, test_database):
    """Test successful POST /api/groups endpoint."""
    group_data = {'name': 'Test Group'}
    response = client.post('/api/groups',
                          data=json.dumps(group_data),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == group_data['name']

def test_create_group_invalid_data(client, test_database):
    """Test POST /api/groups with invalid data."""
    invalid_data = {}  # Missing required 'name' field
    response = client.post('/api/groups',
                          data=json.dumps(invalid_data),
                          content_type='application/json')
    assert response.status_code == 400

def test_create_study_session_success(client, populated_test_database):
    """Test successful POST /api/study_sessions endpoint."""
    # Create test data
    group = Group(name="Test Group")
    populated_test_database.session.add(group)
    populated_test_database.session.flush()
    
    activity = StudyActivity(name="Test Activity")
    populated_test_database.session.add(activity)
    populated_test_database.session.commit()
    
    session_data = {
        'group_id': group.id,
        'study_activity_id': activity.id
    }
    response = client.post('/api/study_sessions',
                          data=json.dumps(session_data),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['group_id'] == session_data['group_id']
    assert data['study_activity_id'] == session_data['study_activity_id']

def test_create_study_session_invalid_data(client, test_database):
    """Test POST /api/study_sessions with invalid data."""
    invalid_data = {'group_id': 999}  # Invalid group_id and missing study_activity_id
    response = client.post('/api/study_sessions',
                          data=json.dumps(invalid_data),
                          content_type='application/json')
    assert response.status_code == 400

def test_word_review_success(client, populated_test_database):
    """Test successful POST /api/study_sessions/:id/words/:word_id/review endpoint."""
    # Create test data
    word = Word(french="test", english="test")
    populated_test_database.session.add(word)
    populated_test_database.session.flush()
    
    group = Group(name="Test Group")
    populated_test_database.session.add(group)
    populated_test_database.session.flush()
    
    activity = StudyActivity(name="Test Activity")
    populated_test_database.session.add(activity)
    populated_test_database.session.flush()
    
    session = StudySession(
        group_id=group.id,
        study_activity_id=activity.id
    )
    populated_test_database.session.add(session)
    populated_test_database.session.commit()
    
    review_data = {'is_correct': True}
    response = client.post(f'/api/study_sessions/{session.id}/words/{word.id}/review',
                          data=json.dumps(review_data),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['word_id'] == word.id
    assert data['study_session_id'] == session.id
    assert data['is_correct'] == review_data['is_correct']

def test_word_review_invalid_data(client, test_database):
    """Test POST /api/study_sessions/:id/words/:word_id/review with invalid data."""
    response = client.post('/api/study_sessions/999/words/999/review',
                          data=json.dumps({'is_correct': True}),
                          content_type='application/json')
    assert response.status_code == 404
