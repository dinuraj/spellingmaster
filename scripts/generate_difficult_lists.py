import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from extensions import db
from models import WordList, Word
import random
import re

MONTHS = ["january","february","march","april","may","june","july","august","september","october","november","december"]

app = create_app()

def difficulty_score(word: str) -> int:
    w = word.lower()
    score = len(w)
    for ch in 'qxzjk':
        if ch in w:
            score += 5
    # penalize very short words
    if len(w) <= 3:
        score -= 5
    return score

with app.app_context():
    # Find lists that look like monthly lists
    month_lists = WordList.query.filter(
        db.or_(*[WordList.name.ilike(f"%{m}%") for m in MONTHS])
    ).all()
    if not month_lists:
        month_lists = WordList.query.all()
    # collect candidate words
    candidates = []
    for wl in month_lists:
        for w in wl.words:
            candidates.append((w.word, wl.name))
    # deduplicate by word (keep first occurrence)
    seen = {}
    uniq = []
    for word, src in candidates:
        key = word.strip().lower()
        if not key or key in seen:
            continue
        seen[key] = src
        uniq.append((word, src))
    if not uniq:
        print("No source words found to build lists.")
        raise SystemExit(1)
    # score and sort
    scored = [(difficulty_score(w), w, src) for (w, src) in uniq]
    scored.sort(reverse=True)
    top_pool = [w for _, w, _ in scored[:400]]  # top 400 candidates

    created = []
    num_lists = 5
    for i in range(1, num_lists+1):
        if len(top_pool) < 15:
            selection = random.sample([w for _, w, _ in scored], min(15, len(scored)))
        else:
            selection = random.sample(top_pool, 15)
        name = f"Difficult Mix {i}"
        desc = f"Automatically generated list of {len(selection)} difficult words (mix)."
        wl = WordList(name=name, description=desc)
        db.session.add(wl)
        db.session.flush()  # get id
        for word in selection:
            db.session.add(Word(word=word, hint='', list_id=wl.id))
        db.session.commit()
        created.append((wl.id, name, selection))
        print(f"Created list {wl.id} '{name}' with {len(selection)} words")
    print("Done.")
