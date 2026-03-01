"""Quiz blueprint: run quizzes and record results."""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify, current_app
from extensions import db
from models import WordList, Word, QuizResult
from datetime import datetime
import random
import json
import base64
import io
from PIL import Image, ImageOps, ImageFilter
import pytesseract
import os

# Try to detect a local Tesseract binary and configure pytesseract accordingly.
# This helps when the OS installer places tesseract at the typical Program Files path.
for _p in (os.environ.get('TESSERACT_CMD'), os.environ.get('TESSERACT_PATH'),
           r"C:\Program Files\Tesseract-OCR\tesseract.exe",
           r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"):
    if not _p:
        continue
    try:
        if os.path.exists(_p):
            pytesseract.pytesseract.tesseract_cmd = _p
            break
    except Exception:
        continue

quiz_bp = Blueprint('quiz_bp', __name__, template_folder='../templates')


@quiz_bp.route('/')
def index():
    lists = WordList.query.order_by(WordList.created_at.desc()).all()
    from models import FillQuestion
    fill_word_count = db.session.query(FillQuestion.word).distinct().count()
    return render_template('home.html', word_lists=lists, fill_word_count=fill_word_count)


@quiz_bp.route('/start', methods=['POST'])
def start_quiz():
    data = request.get_json(silent=True) or request.form
    # Accept list_id from the POST data or fall back to the current session quiz
    raw_list_id = data.get('list_id') if data is not None else None
    if not raw_list_id and session.get('quiz'):
        raw_list_id = session['quiz'].get('list_id')
    if not raw_list_id:
        flash('No word list specified to start the quiz.', 'warning')
        return redirect(url_for('quiz_bp.index'))
    try:
        list_id = int(raw_list_id)
    except (TypeError, ValueError):
        flash('Invalid word list specified.', 'warning')
        return redirect(url_for('quiz_bp.index'))
    missed_only = data.get('missed_only') in ('true', 'True', True)
    wl = WordList.query.get_or_404(list_id)
    words_q = [w.word for w in wl.words]
    if missed_only and session.get('quiz') and session['quiz'].get('wrong'):
        words = list(session['quiz']['wrong'])
    else:
        words = words_q
    if not words:
        flash('Selected list has no words.', 'warning')
        return redirect(url_for('quiz_bp.index'))
    random.shuffle(words)
    session['quiz'] = {
        'list_id': wl.id,
        'words': words,
        'current_index': 0,
        'correct': [],
        'wrong': []
    }
    return redirect(url_for('quiz_bp.play'))


@quiz_bp.route('/play')
def play():
    q = session.get('quiz')
    if not q or not q.get('words'):
        flash('Please select a word list to start a quiz.', 'warning')
        return redirect(url_for('quiz_bp.index'))
    idx = q['current_index']
    total = len(q['words'])
    # If we've advanced past the last word, show results instead of crashing
    if idx >= total:
        return redirect(url_for('quiz_bp.results'))
    current_word = q['words'][idx]
    progress_pct = int((idx / total) * 100) if total else 0
    return render_template('quiz/quiz.html', current_index=idx, total_words=total, word=current_word, hint='')


@quiz_bp.route('/check', methods=['POST'])
def check():
    if 'quiz' not in session or not session['quiz'].get('words'):
        return jsonify({'error': 'No active quiz'}), 400
    data = request.get_json(silent=True) or request.form
    answer = (data.get('answer') or '').strip().lower()
    q = session['quiz']
    idx = q['current_index']
    words = q['words']
    current = words[idx]
    is_correct = (answer == current)
    if is_correct:
        q['correct'].append(current)
    else:
        q['wrong'].append(current)
    q['current_index'] = idx + 1
    session['quiz'] = q
    next_available = q['current_index'] < len(q['words'])
    return jsonify({'correct': is_correct, 'correct_word': current, 'next_available': next_available})


@quiz_bp.route('/recognize', methods=['POST'])
def recognize_handwriting():
    # Accept JSON with { image: 'data:image/png;base64,...' }
    data = request.get_json(silent=True) or request.form
    img_b64 = data.get('image') or ''
    if not img_b64:
        return jsonify({'error': 'no image provided'}), 400
    try:
        # strip header if present
        if img_b64.startswith('data:'):
            img_b64 = img_b64.split(',', 1)[1]
        img_bytes = base64.b64decode(img_b64)
        buf = io.BytesIO(img_bytes)
        img = Image.open(buf).convert('L')
        # Smart preprocessing
        # autocontrast to improve dynamic range
        img = ImageOps.autocontrast(img)
        # estimate brightness: if image is dark overall, invert so ink is dark on light
        try:
            from PIL import ImageStat
            stat = ImageStat.Stat(img)
            mean = stat.mean[0]
        except Exception:
            mean = 255
        if mean < 127:
            img = ImageOps.invert(img)
        # median filter to reduce noise
        img = img.filter(ImageFilter.MedianFilter(size=3))
        # enhance contrast again
        img = ImageOps.autocontrast(img)
        # threshold to B/W
        img = img.point(lambda p: 255 if p > 140 else 0)
        # Resize to improve recognition
        w, h = img.size
        nw = max(300, int(w * 2))
        nh = max(100, int(h * 2))
        img = img.resize((nw, nh))
        # Ask Tesseract for a single word/line
        cfg = '-l eng --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        text = pytesseract.image_to_string(img, config=cfg)
        # cleanup
        recognized = ''.join(ch for ch in (text or '') if ch.isalpha()).strip().lower()
        # Save debug image when in debug mode for inspection
        try:
            if current_app and current_app.debug:
                outp = os.path.join(current_app.instance_path, 'ocr_debug.png')
                img.convert('RGB').save(outp)
                current_app.logger.debug(f'OCR debug image saved to {outp}')
        except Exception:
            pass
        return jsonify({'recognized': recognized, 'raw': (text or '').strip()})
    except Exception as e:
        return jsonify({'error': 'recognition_failed', 'detail': str(e)}), 500


@quiz_bp.route('/results')
def results():
    q = session.get('quiz')
    if not q:
        flash('No quiz to show results for.', 'warning')
        return redirect(url_for('quiz_bp.index'))
    total = len(q['words'])
    correct_count = len(q['correct'])
    wrong = q['wrong']
    pct = (correct_count / total) * 100 if total else 0
    if pct == 100:
        stars = 3
    elif pct >= 90:
        stars = 3
    elif pct >= 70:
        stars = 2
    else:
        stars = 1
    if pct == 100:
        message = "Amazing! You're a Spelling Superstar! 🌟"
    elif pct >= 90:
        message = 'Fantastic work! Almost perfect!'
    elif pct >= 70:
        message = 'Great job! Keep practicing those tricky words.'
    elif pct >= 50:
        message = 'Good effort! Review the words you missed and try again.'
    else:
        message = "Keep going! Practice makes perfect. You've got this! 💪"
    # Persist result
    try:
        qr = QuizResult(list_id=q['list_id'], total_words=total, correct_count=correct_count, missed_words=json.dumps(wrong))
        db.session.add(qr)
        db.session.commit()
    except Exception:
        db.session.rollback()
    # Clear session quiz
    session.pop('quiz', None)
    # Prepare lists
    wl = WordList.query.get(q['list_id'])
    return render_template('quiz/results.html', correct_count=correct_count, total_words=total, score_percent=pct, stars=stars, message=message, wrong_words=wrong, correct_words=q['correct'], list_name=wl.name if wl else '')


@quiz_bp.route('/reset', methods=['POST'])
def reset():
    session.pop('quiz', None)
    return redirect(url_for('quiz_bp.index'))
