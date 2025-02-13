from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime, timezone

db = SQLAlchemy()

# Association table for Word-Group many-to-many relationship
words_groups = db.Table('words_groups',
    db.Column('word_id', db.Integer, db.ForeignKey('words.id', ondelete='CASCADE'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True)
)

class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    french = db.Column(db.String, nullable=False)
    english = db.Column(db.String, nullable=False)
    parts = db.Column(db.String)  # JSON string
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    groups = db.relationship('Group', secondary='words_groups', back_populates='words')
    review_items = db.relationship('WordReviewItem', backref='word', cascade='all, delete-orphan')

    @property
    def parts_dict(self):
        return json.loads(self.parts) if self.parts else {}

    @parts_dict.setter
    def parts_dict(self, value):
        self.parts = json.dumps(value) if value else None

    @property
    def stats(self):
        correct = sum(1 for item in self.review_items if item.correct)
        wrong = sum(1 for item in self.review_items if not item.correct)
        return {"correct_count": correct, "wrong_count": wrong}

class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    words = db.relationship('Word', secondary='words_groups', back_populates='groups')
    study_sessions = db.relationship('StudySession', backref='group', cascade='all, delete-orphan')
    study_activities = db.relationship('StudyActivity', backref='group', cascade='all, delete-orphan')

    @property
    def word_count(self):
        return len(self.words)

class StudySession(db.Model):
    __tablename__ = 'study_sessions'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id', ondelete='CASCADE'), nullable=False)
    study_activity_id = db.Column(db.Integer, db.ForeignKey('study_activities.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    review_items = db.relationship('WordReviewItem', backref='study_session', cascade='all, delete-orphan')

class StudyActivity(db.Model):
    __tablename__ = 'study_activities'
    __table_args__ = (
        db.UniqueConstraint('name', 'group_id', name='_activity_name_group_uc'),
    )
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    thumbnail_url = db.Column(db.String)
    description = db.Column(db.String)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    study_sessions = db.relationship('StudySession', backref='study_activity', cascade='all, delete-orphan')

class WordReviewItem(db.Model):
    __tablename__ = 'word_review_items'
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id', ondelete='CASCADE'), nullable=False)
    study_session_id = db.Column(db.Integer, db.ForeignKey('study_sessions.id', ondelete='CASCADE'), nullable=False)
    correct = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
