"""One-time script to import fill questions from JSON into the database."""
from app import create_app
from extensions import db
from models import FillQuestion
from pathlib import Path
import json

app = create_app()
with app.app_context():
    base = Path(app.root_path) / 'data'
    files = [
        base / 'fill_questions_june_july_aug_sept.json',
        base / 'fill_questions_oct_nov_dec_jan_feb.json',
    ]
    imported = 0
    skipped = 0
    for f in files:
        if not f.exists():
            print(f'File not found: {f}')
            continue
        with f.open('r', encoding='utf-8') as fh:
            data = json.load(fh)
        items = data.get('items') if isinstance(data, dict) else data
        for it in items:
            word = it.get('word')
            qs = it.get('questions', [])
            for q in qs:
                question_text = q.get('question')
                answer = q.get('answer') or word
                exists = FillQuestion.query.filter_by(word=word, question=question_text).first()
                if exists:
                    skipped += 1
                    continue
                fq = FillQuestion(
                    word=word, question=question_text, answer=answer,
                    month=(it.get('month') or ''),
                    subject=(it.get('subject') or 'ENGLISH'),
                    source_file=str(f.name),
                )
                db.session.add(fq)
                imported += 1
    db.session.commit()
    total = FillQuestion.query.count()
    words = db.session.query(FillQuestion.word).distinct().count()
    print(f'Imported {imported}, skipped {skipped}')
    print(f'Total in DB: {total} questions, {words} unique words')
