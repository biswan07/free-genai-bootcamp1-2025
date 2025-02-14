import pytest
import json
from app.models import Word, Group, StudySession, StudyActivity, WordReviewItem
from datetime import datetime

def test_word_creation(test_database):
    """Test creating a new word."""
    word = Word(
        french='merci',
        english='thank you',
        parts=json.dumps({'part_of_speech': 'interjection'})
    )
    test_database.session.add(word)
    test_database.session.commit()
    
    assert word.id is not None
    assert word.french == 'merci'
    assert word.english == 'thank you'
    assert word.parts_dict['part_of_speech'] == 'interjection'

def test_group_word_relationship(test_database):
    """Test the many-to-many relationship between words and groups."""
    word = Word(french='au revoir', english='goodbye')
    group = Group(name='Basic Phrases')
    
    group.words.append(word)
    test_database.session.add(group)
    test_database.session.commit()
    
    assert word in group.words
    assert group in word.groups

def test_study_session_creation(test_database):
    """Test creating a study session with associated activities."""
    group = Group(name='Test Group')
    test_database.session.add(group)
    test_database.session.flush()
    
    activity = StudyActivity(
        name='Test Activity',
        description='Test Description',
        group_id=group.id
    )
    test_database.session.add(activity)
    test_database.session.flush()
    
    session = StudySession(
        group_id=group.id,
        study_activity_id=activity.id
    )
    test_database.session.add(session)
    test_database.session.commit()
    
    assert session.id is not None
    assert session.group_id == group.id
    assert session.study_activity_id == activity.id
    assert isinstance(session.created_at, datetime)

def test_word_review_item(test_database):
    """Test creating and querying word review items."""
    word = Word(french='oui', english='yes')
    test_database.session.add(word)
    
    group = Group(name='Test Group')
    test_database.session.add(group)
    test_database.session.flush()
    
    activity = StudyActivity(
        name='Test Activity',
        description='Test Description',
        group_id=group.id
    )
    test_database.session.add(activity)
    test_database.session.flush()
    
    session = StudySession(
        group_id=group.id,
        study_activity_id=activity.id
    )
    test_database.session.add(session)
    test_database.session.flush()
    
    review = WordReviewItem(
        word_id=word.id,
        study_session_id=session.id,
        is_correct=True
    )
    test_database.session.add(review)
    test_database.session.commit()
    
    assert review.is_correct is True
    assert isinstance(review.created_at, datetime)
    assert review.word == word
    assert review.study_session == session
