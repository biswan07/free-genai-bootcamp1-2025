import pytest
from flask import json
from datetime import datetime, timedelta
from app.models import Word, Group, StudySession, StudyActivity, WordReviewItem

@pytest.fixture(autouse=True)
def reset_database(populated_test_database):
    """Reset database before each test."""
    populated_test_database.session.query(WordReviewItem).delete()
    populated_test_database.session.query(StudySession).delete()
    populated_test_database.session.query(StudyActivity).delete()
    populated_test_database.session.query(Word).delete()
    populated_test_database.session.query(Group).delete()
    populated_test_database.session.commit()
    return populated_test_database

def test_get_last_study_session(client, populated_test_database):
    """Test GET /api/dashboard/last_study_session endpoint."""
    # Create test data
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
    
    # Test endpoint
    response = client.get('/api/dashboard/last_study_session')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['id'] == session.id
    assert data['group_id'] == group.id
    assert data['group_name'] == group.name
    assert data['study_activity_id'] == activity.id

def test_get_study_progress(client, populated_test_database):
    """Test GET /api/dashboard/study_progress endpoint."""
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
    populated_test_database.session.flush()
    
    review = WordReviewItem(
        word_id=word.id,
        study_session_id=session.id,
        is_correct=True
    )
    populated_test_database.session.add(review)
    populated_test_database.session.commit()
    
    # Test endpoint
    response = client.get('/api/dashboard/study_progress')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'total_words_studied' in data
    assert 'total_available_words' in data
    assert data['total_words_studied'] == 1
    assert data['total_available_words'] == 1

def test_get_quick_stats(client, populated_test_database):
    """Test GET /api/dashboard/quick-stats endpoint."""
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
    populated_test_database.session.flush()
    
    # Add one correct and one incorrect review
    review1 = WordReviewItem(
        word_id=word.id,
        study_session_id=session.id,
        is_correct=True
    )
    review2 = WordReviewItem(
        word_id=word.id,
        study_session_id=session.id,
        is_correct=False
    )
    populated_test_database.session.add(review1)
    populated_test_database.session.add(review2)
    populated_test_database.session.commit()
    
    # Test endpoint
    response = client.get('/api/dashboard/quick-stats')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'success_rate' in data
    assert 'total_study_sessions' in data
    assert 'total_active_groups' in data
    assert 'study_streak_days' in data
    
    assert data['success_rate'] == 50.0  # 1 correct out of 2 reviews
    assert data['total_study_sessions'] == 1
    assert data['total_active_groups'] == 1
