import pytest
import json
from app.models import Word, Group, StudySession, StudyActivity, WordReviewItem, db

def test_database_word_crud(test_database):
    """Test CRUD operations for Word model."""
    # Create
    word = Word(
        french='pomme',
        english='apple',
        parts=json.dumps({'part_of_speech': 'noun'})
    )
    test_database.session.add(word)
    test_database.session.commit()
    assert word.id is not None
    
    # Read
    retrieved_word = Word.query.filter_by(french='pomme').first()
    assert retrieved_word is not None
    assert retrieved_word.english == 'apple'
    assert retrieved_word.parts_dict['part_of_speech'] == 'noun'
    
    # Update
    retrieved_word.english = 'Apple fruit'
    test_database.session.commit()
    updated_word = test_database.session.get(Word, retrieved_word.id)
    assert updated_word.english == 'Apple fruit'
    
    # Delete
    test_database.session.delete(retrieved_word)
    test_database.session.commit()
    deleted_word = test_database.session.get(Word, retrieved_word.id)
    assert deleted_word is None

def test_database_relationships(test_database):
    """Test database relationships between models."""
    # Create and save group first
    group = Group(name='Nouns')
    test_database.session.add(group)
    test_database.session.flush()  # Get group.id
    
    # Create and save word
    word = Word(french='livre', english='book')
    test_database.session.add(word)
    test_database.session.flush()  # Get word.id
    
    # Link word to group
    group.words.append(word)
    
    # Create and save activity
    activity = StudyActivity(
        name='Vocabulary Quiz',
        description='Test your vocabulary',
        group_id=group.id  # Now group.id exists
    )
    test_database.session.add(activity)
    test_database.session.flush()  # Get activity.id
    
    # Create study session
    session = StudySession(
        group_id=group.id,
        study_activity_id=activity.id
    )
    test_database.session.add(session)
    test_database.session.flush()  # Get session.id
    
    # Create word review
    review = WordReviewItem(
        word_id=word.id,
        study_session_id=session.id,
        correct=True
    )
    test_database.session.add(review)
    
    # Commit all changes
    test_database.session.commit()
    
    # Test relationships
    assert word in group.words
    assert session.group_id == group.id
    assert session.study_activity_id == activity.id
    assert review.word == word
    assert review.study_session == session

def test_cascade_delete(test_database):
    """Test cascade delete operations."""
    # Create and save group first
    group = Group(name='Test Group')
    test_database.session.add(group)
    test_database.session.flush()  # Get group.id
    
    # Create and save word
    word = Word(french='test', english='test')
    test_database.session.add(word)
    test_database.session.flush()
    
    # Link word to group
    group.words.append(word)
    
    # Create activity with valid group_id
    activity = StudyActivity(
        name='Test Activity',
        description='Test Description',
        group_id=group.id  # Now group.id exists
    )
    test_database.session.add(activity)
    test_database.session.flush()
    
    # Create session with valid IDs
    session = StudySession(
        group_id=group.id,
        study_activity_id=activity.id
    )
    test_database.session.add(session)
    
    # Commit all changes
    test_database.session.commit()
    
    # Delete the group
    test_database.session.delete(group)
    test_database.session.commit()
    
    # Check if related objects are deleted or updated appropriately
    assert StudySession.query.filter_by(group_id=group.id).first() is None
    assert StudyActivity.query.filter_by(group_id=group.id).first() is None

def test_database_constraints(test_database):
    """Test database constraints and validations."""
    # Create a test group first
    group = Group(name='Test Group')
    test_database.session.add(group)
    test_database.session.flush()  # Get group.id
    
    # Test unique constraint on activity name within the same group
    activity1 = StudyActivity(
        name='Unique Activity',
        description='Test Description',
        group_id=group.id
    )
    test_database.session.add(activity1)
    test_database.session.commit()
    
    # Try to create another activity with the same name in the same group
    activity2 = StudyActivity(
        name='Unique Activity',  # Same name
        description='Different Description',
        group_id=group.id  # Same group
    )
    test_database.session.add(activity2)
    
    # This should raise an IntegrityError due to unique constraint
    with pytest.raises(Exception) as exc_info:
        test_database.session.commit()
    assert "IntegrityError" in str(exc_info.value)
