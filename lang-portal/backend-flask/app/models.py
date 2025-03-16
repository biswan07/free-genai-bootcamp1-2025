from datetime import datetime
from app import db

# Association table for Word-Group many-to-many relationship
word_group = db.Table('words_groups',
    db.Column('word_id', db.Integer, db.ForeignKey('words.id', ondelete='CASCADE'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True)
)

class Word(db.Model):
    """Word model."""
    __tablename__ = 'words'
    
    id = db.Column(db.Integer, primary_key=True)
    french = db.Column(db.String(100), nullable=False)
    english = db.Column(db.String(100), nullable=False)
    parts = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    groups = db.relationship('Group', secondary=word_group, back_populates='words')
    review_items = db.relationship('WordReviewItem', back_populates='word', cascade='all, delete-orphan')
    
    @property
    def parts_dict(self):
        if isinstance(self.parts, str):
            import json
            return json.loads(self.parts)
        return self.parts or {}
    
    @property
    def stats(self):
        correct = sum(1 for item in self.review_items if item.is_correct)
        wrong = sum(1 for item in self.review_items if not item.is_correct)
        return {"correct_count": correct, "wrong_count": wrong}

class Group(db.Model):
    """Group model."""
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    words = db.relationship('Word', secondary=word_group, back_populates='groups')
    study_sessions = db.relationship('StudySession', backref='group', lazy=True, cascade='all, delete-orphan')
    study_activities = db.relationship('StudyActivity', backref='group', lazy=True, cascade='all, delete-orphan')

class StudySession(db.Model):
    """Study session model."""
    __tablename__ = 'study_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    study_activity_id = db.Column(db.Integer, db.ForeignKey('study_activities.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    questions = db.Column(db.Text, nullable=True)  # To store JSON-serialized quiz questions
    
    # Relationships
    review_items = db.relationship('WordReviewItem', back_populates='study_session', cascade='all, delete-orphan')
    study_activity = db.relationship('StudyActivity', back_populates='study_sessions')

class StudyActivity(db.Model):
    """Study activity model."""
    __tablename__ = 'study_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    thumbnail_url = db.Column(db.String(500), nullable=True)
    description = db.Column(db.Text, nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Add unique constraint for name within a group
    __table_args__ = (
        db.UniqueConstraint('name', 'group_id', name='_name_group_uc'),
    )
    
    # Relationships
    study_sessions = db.relationship('StudySession', back_populates='study_activity', cascade='all, delete-orphan')

class WordReviewItem(db.Model):
    """Word review item model."""
    __tablename__ = 'word_review_items'
    
    id = db.Column(db.Integer, primary_key=True)
    study_session_id = db.Column(db.Integer, db.ForeignKey('study_sessions.id'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    word = db.relationship('Word', back_populates='review_items')
    study_session = db.relationship('StudySession', back_populates='review_items')
