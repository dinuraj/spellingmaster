from __future__ import annotations
from flask import Blueprint, current_app, request, jsonify, render_template, url_for, redirect
from extensions import db
from models import FillQuestion, FillQuizAttempt
from datetime import datetime
import json
import random

fillquiz_bp = Blueprint('fillquiz_bp', __name__)


@fillquiz_bp.route('/start', methods=['POST', 'GET'])
def start_quiz():
    """Start a new fill-blank quiz.

    Query params: `size` (int, default 30)
    Creates a `FillQuizAttempt` with a random selection of distinct words and
    one question per word chosen at random.
    """
    size = int(request.args.get('size', 30))
    # Get unique words available
    words = db.session.query(FillQuestion.word).distinct().all()
    words = [w[0] for w in words]
    if not words:
        return jsonify({'error': 'no fill questions available'}), 400

    # Choose up to `size` distinct words
    rnd = random.Random()
    chosen_words = rnd.sample(words, k=min(size, len(words)))

    question_ids = []
    for w in chosen_words:
        q = FillQuestion.query.filter_by(word=w).order_by(db.func.random()).first()
        if q:
            question_ids.append(q.id)

    attempt = FillQuizAttempt(
        created_at=datetime.utcnow(),
        total_questions=len(question_ids),
        question_ids=json.dumps(question_ids),
    )
    db.session.add(attempt)
    db.session.commit()

    return jsonify({'attempt_id': attempt.id, 'total': attempt.total_questions, 'pages': (attempt.total_questions + 4)//5})


@fillquiz_bp.route('/play')
def play_page():
    """Return one page of questions for an attempt.

    Query params: `attempt_id` and `page` (1-based).
    """
    attempt_id = request.args.get('attempt_id')
    page = int(request.args.get('page', 1))
    if not attempt_id:
        return jsonify({'error': 'missing attempt_id'}), 400
    attempt = FillQuizAttempt.query.get(attempt_id)
    if not attempt:
        return jsonify({'error': 'attempt not found'}), 404

    qids = json.loads(attempt.question_ids or '[]')
    per_page = 5
    start = (page - 1) * per_page
    slice_ids = qids[start:start+per_page]
    questions = []
    for qid in slice_ids:
        q = FillQuestion.query.get(qid)
        if q:
            questions.append({'id': q.id, 'question': q.question})

    return jsonify({'attempt_id': attempt.id, 'page': page, 'questions': questions, 'total': attempt.total_questions})


@fillquiz_bp.route('/finish', methods=['POST'])
def finish_quiz():
    """Submit answers for the full quiz. Expects JSON: {attempt_id: int, answers: {qid: answer}}"""
    data = request.get_json(force=True)
    attempt_id = data.get('attempt_id')
    answers = data.get('answers', {})
    attempt = FillQuizAttempt.query.get(attempt_id)
    if not attempt:
        return jsonify({'error': 'attempt not found'}), 404

    qids = json.loads(attempt.question_ids or '[]')
    results = []
    correct = 0
    for qid in qids:
        q = FillQuestion.query.get(qid)
        submitted = (answers.get(str(qid)) or '').strip()
        is_correct = submitted.lower() == (q.answer or '').lower()
        if is_correct:
            correct += 1
        results.append({'question_id': qid, 'word': q.word, 'question': q.question, 'answer': q.answer, 'submitted': submitted, 'correct': is_correct})

    attempt.completed_at = datetime.utcnow()
    attempt.correct_count = correct
    attempt.results = json.dumps(results)
    db.session.commit()

    return jsonify({'attempt_id': attempt.id, 'correct': correct, 'total': attempt.total_questions})


@fillquiz_bp.route('/results')
def results_page():
    attempt_id = request.args.get('attempt_id')
    attempt = FillQuizAttempt.query.get(attempt_id) if attempt_id else None
    if not attempt:
        return 'Attempt not found', 404
    results = json.loads(attempt.results or '[]')
    return render_template('fillquiz/results.html', attempt=attempt, results=results)
