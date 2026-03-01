"""Import words from docs/words.json into the database.
Run with: python import_words.py
"""
import json
from app import create_app
from extensions import db
from models import WordList, Word
from pathlib import Path


def load_from_json(path: str | Path):
    app = create_app()
    p = Path(path)
    if not p.exists():
        print('words.json not found at', p)
        return
    data = json.loads(p.read_text(encoding='utf-8'))
    with app.app_context():
        added_lists = 0
        added_words = 0
        for month, categories in data.items():
            # For each month create a WordList named e.g. "June"
            name = month
            wl = WordList.query.filter_by(name=name).first()
            if not wl:
                wl = WordList(name=name, description=f'Imported from words.json for {month}')
                db.session.add(wl)
                db.session.commit()
                added_lists += 1
            # categories is a dict mapping subject to list
            for subject, words in categories.items():
                for w in words:
                    w_text = str(w).strip().lower()
                    # skip empty
                    if not w_text:
                        continue
                    # skip existing
                    exists = Word.query.filter_by(list_id=wl.id, word=w_text).first()
                    if exists:
                        continue
                    new = Word(word=w_text, hint=subject, list_id=wl.id)
                    db.session.add(new)
                    added_words += 1
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print('Error committing:', e)
    print(f'Imported {added_words} words into {added_lists} lists')


if __name__ == '__main__':
    load_from_json('docs/words.json')
