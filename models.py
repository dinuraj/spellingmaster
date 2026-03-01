"""SQLAlchemy models for Spelling Master."""
from __future__ import annotations
from datetime import datetime
from extensions import db
from typing import List
import json


class WordList(db.Model):
    __tablename__ = 'word_lists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    words = db.relationship('Word', backref='list', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self) -> str:
        return f"<WordList {self.name!r}>"


class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    hint = db.Column(db.String(255))
    list_id = db.Column(db.Integer, db.ForeignKey('word_lists.id'), nullable=False)

    def __repr__(self) -> str:
        return f"<Word {self.word!r} in list {self.list_id}>"


class QuizResult(db.Model):
    __tablename__ = 'quiz_results'
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('word_lists.id'))
    total_words = db.Column(db.Integer, default=0)
    correct_count = db.Column(db.Integer, default=0)
    missed_words = db.Column(db.Text)  # JSON string
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def score_percent(self) -> float:
        if not self.total_words:
            return 0.0
        return (self.correct_count / self.total_words) * 100.0

    def missed_list(self) -> List[str]:
        try:
            return json.loads(self.missed_words or '[]')
        except Exception:
            return []

    def __repr__(self) -> str:
        return f"<QuizResult list={self.list_id} score={self.score_percent:.1f}%>"


class FillQuestion(db.Model):
    __tablename__ = 'fill_questions'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False, index=True)
    question = db.Column(db.String(1000), nullable=False)
    answer = db.Column(db.String(100), nullable=False)
    month = db.Column(db.String(20))
    subject = db.Column(db.String(50))
    source_file = db.Column(db.String(200))

    def as_dict(self):
        return {'id': self.id, 'word': self.word, 'question': self.question, 'answer': self.answer}


class FillQuizAttempt(db.Model):
    __tablename__ = 'fill_quiz_attempts'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    total_questions = db.Column(db.Integer, default=0)
    correct_count = db.Column(db.Integer, default=0)
    question_ids = db.Column(db.Text)  # JSON list of question ids in order
    results = db.Column(db.Text)  # JSON list of per-question results

    def __repr__(self) -> str:
        return f"<FillQuizAttempt id={self.id} total={self.total_questions} correct={self.correct_count}>"
