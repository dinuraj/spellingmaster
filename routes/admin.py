"""Admin blueprint: manage word lists and words."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from extensions import db
from models import WordList, Word
from datetime import datetime
import re
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from models import FillQuestion

admin_bp = Blueprint('admin_bp', __name__, template_folder='../templates')


class FillQuestionForm(FlaskForm):
    question = TextAreaField('Question', validators=[DataRequired(), Length(max=1000)])
    answer = StringField('Answer', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Save')

WORD_RE = re.compile(r"^[a-zA-Z-]{1,50}$")


@admin_bp.route('/')
def index():
    lists = WordList.query.order_by(WordList.created_at.desc()).all()
    fill_question_count = FillQuestion.query.count()
    fill_word_count = db.session.query(FillQuestion.word).distinct().count()
    return render_template('admin/manage_lists.html', word_lists=lists,
                           fill_question_count=fill_question_count,
                           fill_word_count=fill_word_count)


@admin_bp.route('/list/new', methods=['GET', 'POST'])
def create_list():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        desc = request.form.get('description', '').strip()
        if not (2 <= len(name) <= 100):
            flash('List name must be 2–100 characters.', 'error')
            return redirect(url_for('admin_bp.index'))
        try:
            wl = WordList(name=name, description=desc)
            db.session.add(wl)
            db.session.commit()
            flash('List created.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Could not create list: ' + str(e), 'error')
        return redirect(url_for('admin_bp.index'))
    return render_template('admin/manage_lists.html')


@admin_bp.route('/list/<int:list_id>/edit', methods=['GET', 'POST'])
def edit_list(list_id: int):
    wl = WordList.query.get_or_404(list_id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        desc = request.form.get('description', '').strip()
        if not (2 <= len(name) <= 100):
            flash('List name must be 2–100 characters.', 'error')
            return redirect(url_for('admin_bp.edit_list', list_id=list_id))
        wl.name = name
        wl.description = desc
        try:
            db.session.commit()
            flash('List updated.', 'success')
        except Exception:
            db.session.rollback()
            flash('Could not update list.', 'error')
        return redirect(url_for('admin_bp.edit_list', list_id=list_id))
    words = wl.words.order_by(Word.id).all()
    return render_template('admin/edit_list.html', word_list=wl, words=words)


@admin_bp.route('/list/<int:list_id>/delete', methods=['POST'])
def delete_list(list_id: int):
    wl = WordList.query.get_or_404(list_id)
    try:
        db.session.delete(wl)
        db.session.commit()
        flash('List deleted.', 'success')
    except Exception:
        db.session.rollback()
        flash('Could not delete list.', 'error')
    return redirect(url_for('admin_bp.index'))


@admin_bp.route('/list/<int:list_id>/word/add', methods=['POST'])
def add_word(list_id: int):
    wl = WordList.query.get_or_404(list_id)
    data = request.get_json(silent=True) or request.form
    word_text = (data.get('word') or '').strip().lower()
    hint = (data.get('hint') or '').strip()
    if not WORD_RE.match(word_text):
        return jsonify({'success': False, 'error': 'Invalid word format'}), 400
    # Skip duplicates
    existing = Word.query.filter_by(list_id=wl.id, word=word_text).first()
    if existing:
        return jsonify({'success': False, 'error': 'Duplicate'}), 200
    try:
        w = Word(word=word_text, hint=hint, list_id=wl.id)
        db.session.add(w)
        db.session.commit()
        return jsonify({'success': True, 'word': {'id': w.id, 'word': w.word, 'hint': w.hint}})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/word/<int:word_id>/delete', methods=['POST'])
def delete_word(word_id: int):
    w = Word.query.get_or_404(word_id)
    try:
        db.session.delete(w)
        db.session.commit()
        return jsonify({'success': True})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False}), 500


@admin_bp.route('/list/<int:list_id>/bulk', methods=['POST'])
def bulk_import(list_id: int):
    wl = WordList.query.get_or_404(list_id)
    text = request.form.get('bulk_text', '')
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    added = 0
    for line in lines:
        if '|' in line:
            parts = line.split('|', 1)
            w = parts[0].strip().lower()
            hint = parts[1].strip()
        else:
            w = line.strip().lower()
            hint = ''
        if not WORD_RE.match(w):
            continue
        existing = Word.query.filter_by(list_id=wl.id, word=w).first()
        if existing:
            continue
        try:
            db.session.add(Word(word=w, hint=hint, list_id=wl.id))
            added += 1
        except Exception:
            db.session.rollback()
    try:
        db.session.commit()
        flash(f'Imported {added} words.', 'success')
    except Exception:
        db.session.rollback()
        flash('Import failed.', 'error')
    return redirect(url_for('admin_bp.edit_list', list_id=list_id))


@admin_bp.route('/fillquestions')
def list_fill_questions():
    page = int(request.args.get('page', 1))
    per_page = 50
    qstr = (request.args.get('q') or '').strip()
    q = FillQuestion.query
    if qstr:
        # simple search in word or question text
        q = q.filter((FillQuestion.word.ilike(f"%{qstr}%")) | (FillQuestion.question.ilike(f"%{qstr}%")))
    q = q.order_by(FillQuestion.id)
    pagination = q.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('admin/fill_questions.html', pagination=pagination, qstr=qstr)


@admin_bp.route('/fillquestions/<int:qid>/edit', methods=['GET', 'POST'])
def edit_fill_question(qid: int):
    fq = FillQuestion.query.get_or_404(qid)
    form = FillQuestionForm(obj=fq)
    if form.validate_on_submit():
        fq.question = form.question.data.strip()
        fq.answer = form.answer.data.strip()
        try:
            db.session.commit()
            flash('Fill question updated.', 'success')
        except Exception:
            db.session.rollback()
            flash('Could not update.', 'error')
        return redirect(url_for('admin_bp.list_fill_questions'))
    return render_template('admin/edit_fill_question.html', form=form, fq=fq)


@admin_bp.route('/fillquestions/<int:qid>/delete', methods=['POST'])
def delete_fill_question(qid: int):
    fq = FillQuestion.query.get_or_404(qid)
    try:
        db.session.delete(fq)
        db.session.commit()
        flash('Deleted.', 'success')
    except Exception:
        db.session.rollback()
        flash('Could not delete.', 'error')
    return redirect(url_for('admin_bp.list_fill_questions'))


@admin_bp.route('/fillquestions/bulk_edit', methods=['GET', 'POST'])
def bulk_edit_fill_questions():
    """Bulk edit multiple fill questions. GET shows textarea with lines 'id|question|answer'. POST parses and updates."""
    if request.method == 'POST':
        text = request.form.get('bulk_text', '')
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        updated = 0
        for line in lines:
            parts = line.split('|')
            if len(parts) < 3:
                continue
            try:
                qid = int(parts[0].strip())
            except Exception:
                continue
            fq = FillQuestion.query.get(qid)
            if not fq:
                continue
            fq.question = parts[1].strip()
            fq.answer = parts[2].strip()
            updated += 1
        try:
            db.session.commit()
            flash(f'Updated {updated} items.', 'success')
        except Exception:
            db.session.rollback()
            flash('Bulk update failed.', 'error')
        return redirect(url_for('admin_bp.list_fill_questions'))
    # GET
    return render_template('admin/bulk_edit_fill_questions.html')
