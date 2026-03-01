from __future__ import annotations
from flask import Blueprint, current_app, request, jsonify, render_template, url_for, redirect, session, flash
from extensions import db
from models import FillQuestion, FillQuizAttempt
from datetime import datetime
import json
import random
import math

fillquiz_bp = Blueprint('fillquiz_bp', __name__)

QUESTIONS_PER_PAGE = 5


@fillquiz_bp.route('/')
def index():
    """Fill quiz launcher showing word count, size selector, and recent attempts."""
    total_words = db.session.query(FillQuestion.word).distinct().count()
    total_questions = FillQuestion.query.count()
    recent_attempts = FillQuizAttempt.query.order_by(FillQuizAttempt.created_at.desc()).limit(5).all()
    return render_template('fillquiz/index.html',
                           total_words=total_words,
                           total_questions=total_questions,
                           recent_attempts=recent_attempts)


@fillquiz_bp.route('/start', methods=['POST'])
def start_quiz():
    """Start a new fill-blank quiz with user-selected size."""
    size_raw = (request.form.get('size') or '30').strip()
    missed_only = request.form.get('missed_only') in ('true', 'True', '1')

    # Get unique words available
    words = [w[0] for w in db.session.query(FillQuestion.word).distinct().all()]
    if not words:
        flash('No fill questions available. Please import questions first.', 'warning')
        return redirect(url_for('fillquiz_bp.index'))

    # Handle "practice missed words" flow
    if missed_only and session.get('fill_missed_words'):
        words = list(session['fill_missed_words'])
    else:
        # Determine quiz size
        if size_raw == 'all':
            size = len(words)
        else:
            try:
                size = int(size_raw)
            except ValueError:
                size = 30
            size = min(size, len(words))
        random.shuffle(words)
        words = words[:size]

    # Pick one random question per word
    question_ids = []
    for w in words:
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

    # Store in session
    session['fill_attempt_id'] = attempt.id
    session['fill_answers'] = {}
    session.pop('fill_missed_words', None)

    return redirect(url_for('fillquiz_bp.play_page', page=1))


@fillquiz_bp.route('/play', methods=['GET', 'POST'])
def play_page():
    """Render one page of 5 questions, or save answers and navigate."""
    attempt_id = session.get('fill_attempt_id')
    if not attempt_id:
        flash('Please start a fill quiz first.', 'warning')
        return redirect(url_for('fillquiz_bp.index'))

    attempt = FillQuizAttempt.query.get(attempt_id)
    if not attempt:
        session.pop('fill_attempt_id', None)
        flash('Quiz not found. Please start a new one.', 'warning')
        return redirect(url_for('fillquiz_bp.index'))

    qids = json.loads(attempt.question_ids or '[]')
    total_pages = math.ceil(len(qids) / QUESTIONS_PER_PAGE) or 1

    # On POST: save current page answers, then navigate
    if request.method == 'POST':
        answers = session.get('fill_answers', {})
        for key, val in request.form.items():
            if key.startswith('answer_'):
                qid = key.replace('answer_', '')
                answers[qid] = val.strip()
        session['fill_answers'] = answers

        action = request.form.get('action', 'next')
        current = int(request.form.get('current_page', 1))

        if action == 'prev':
            page = max(1, current - 1)
            return redirect(url_for('fillquiz_bp.play_page', page=page))
        elif action == 'finish':
            return redirect(url_for('fillquiz_bp.finish_quiz'))
        else:  # next
            page = min(total_pages, current + 1)
            return redirect(url_for('fillquiz_bp.play_page', page=page))

    # GET: render the requested page
    page = int(request.args.get('page', 1))
    page = max(1, min(page, total_pages))

    start = (page - 1) * QUESTIONS_PER_PAGE
    slice_ids = qids[start:start + QUESTIONS_PER_PAGE]

    questions = []
    for i, qid in enumerate(slice_ids):
        q = FillQuestion.query.get(qid)
        if q:
            questions.append({
                'id': q.id,
                'number': start + i + 1,
                'question': q.question,
            })

    answers = session.get('fill_answers', {})
    progress_pct = int((page / total_pages) * 100)

    return render_template('fillquiz/play.html',
                           attempt_id=attempt.id,
                           page=page,
                           total_pages=total_pages,
                           questions=questions,
                           answers=answers,
                           progress_pct=progress_pct,
                           total_questions=len(qids))


@fillquiz_bp.route('/finish', methods=['GET', 'POST'])
def finish_quiz():
    """Score the quiz, save results, redirect to results page."""
    attempt_id = session.get('fill_attempt_id')
    if not attempt_id:
        flash('No active quiz to finish.', 'warning')
        return redirect(url_for('fillquiz_bp.index'))

    attempt = FillQuizAttempt.query.get(attempt_id)
    if not attempt:
        flash('Quiz not found.', 'warning')
        return redirect(url_for('fillquiz_bp.index'))

    answers = session.get('fill_answers', {})
    qids = json.loads(attempt.question_ids or '[]')

    results = []
    correct = 0
    missed_words = []
    for qid in qids:
        q = FillQuestion.query.get(qid)
        if not q:
            continue
        submitted = (answers.get(str(qid)) or '').strip()
        is_correct = submitted.lower() == (q.answer or '').lower()
        if is_correct:
            correct += 1
        else:
            missed_words.append(q.word)
        results.append({
            'question_id': qid,
            'word': q.word,
            'question': q.question,
            'answer': q.answer,
            'submitted': submitted,
            'correct': is_correct,
        })

    attempt.completed_at = datetime.utcnow()
    attempt.correct_count = correct
    attempt.results = json.dumps(results)
    db.session.commit()

    # Store missed words for "practice missed" flow
    session['fill_missed_words'] = missed_words
    # Clean up session quiz state
    session.pop('fill_attempt_id', None)
    session.pop('fill_answers', None)

    return redirect(url_for('fillquiz_bp.results_page', attempt_id=attempt.id))


@fillquiz_bp.route('/results')
def results_page():
    """Show quiz results with score card, stars, and review."""
    attempt_id = request.args.get('attempt_id')
    attempt = FillQuizAttempt.query.get(attempt_id) if attempt_id else None
    if not attempt or not attempt.results:
        flash('No results to display.', 'warning')
        return redirect(url_for('fillquiz_bp.index'))

    results = json.loads(attempt.results or '[]')
    total = attempt.total_questions
    correct_count = attempt.correct_count or 0
    pct = (correct_count / total * 100) if total else 0

    if pct >= 90:
        stars = 3
    elif pct >= 70:
        stars = 2
    else:
        stars = 1

    if pct == 100:
        message = "Amazing! You're a Fill-in-the-Blank Superstar! 🌟"
    elif pct >= 90:
        message = 'Fantastic work! Almost perfect!'
    elif pct >= 70:
        message = 'Great job! Keep practicing those tricky words.'
    elif pct >= 50:
        message = 'Good effort! Review the words you missed and try again.'
    else:
        message = "Keep going! Practice makes perfect. You've got this! 💪"

    correct_words = [r['word'] for r in results if r['correct']]
    wrong_results = [r for r in results if not r['correct']]
    wrong_words = [r['word'] for r in wrong_results]

    return render_template('fillquiz/results.html',
                           attempt=attempt,
                           results=results,
                           correct_count=correct_count,
                           total=total,
                           score_percent=pct,
                           stars=stars,
                           message=message,
                           correct_words=correct_words,
                           wrong_results=wrong_results,
                           wrong_words=wrong_words)
