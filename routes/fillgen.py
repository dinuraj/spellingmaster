from __future__ import annotations
from flask import Blueprint, current_app, jsonify
import json
from pathlib import Path
import random
from extensions import db
from models import FillQuestion

fillgen_bp = Blueprint('fillgen_bp', __name__)


@fillgen_bp.route('/generate-fill-questions', methods=['POST'])
def generate_fill_questions():
    """Generate `data/fill_questions_llm_full.json` from the candidate pool.

    This endpoint uses deterministic, template-based sentence generation so
    it doesn't rely on an external script or external API. It is intentionally
    restricted to debug mode to avoid accidental public use.
    """
    app = current_app._get_current_object()
    if not app.debug:
        return jsonify({'error': 'Generation allowed only in debug mode'}), 403

    base = Path(app.root_path) / 'data'
    src = base / 'fill_questions.json'
    dest = base / 'fill_questions_llm_full.json'

    if not src.exists():
        return jsonify({'error': f'source not found: {src}'}), 400

    # Load candidates
    with src.open('r', encoding='utf-8') as fh:
        data = json.load(fh)

    candidates = []
    # Support both {'items':[{'word':...},...]} and simple lists
    if isinstance(data, dict) and 'items' in data:
        for it in data['items']:
            w = it.get('word') if isinstance(it, dict) else None
            if not w:
                # fallback if item is string
                w = it if isinstance(it, str) else None
            if w:
                candidates.append(w)
    elif isinstance(data, list):
        for it in data:
            if isinstance(it, dict) and 'word' in it:
                candidates.append(it['word'])
            elif isinstance(it, str):
                candidates.append(it)

    # Template pool (crafted to make sentences where the target word fits naturally)
    templates = [
        "The {word} climbed the tree to reach the acorns.",
        "We saw two {word} chasing each other across the park.",
        "The children watched the {word} gather nuts for winter.",
        "Please put the {word} back on the shelf when you're done.",
        "She was very {word} to open her surprise present.",
        "The class will {word} their project next week.",
        "He found the {word} hidden under the pillow.",
        "They used the {word} to fix the broken chair.",
        "At recess, everyone wanted to try the {word}.",
        "The teacher explained how the {word} works.",
        "We took pictures of the {word} by the river.",
        "A sudden {word} made the leaves fall from the trees.",
        "She learned that the {word} is important for healthy plants.",
        "His favorite book has a story about a {word}.",
        "Can you imagine a {word} made of chocolate?",
        "The {word} was carefully placed on the table.",
        "During the trip, they met a friendly {word}.",
        "The scientist studied the {word} in the lab.",
        "We will {word} the new toy after lunch.",
        "It took a long time for the {word} to change color.",
    ]

    items = []
    for w in candidates:
        # Use a deterministic seed so repeated calls produce same output
        seed = sum(ord(c) for c in w)
        rnd = random.Random(seed)
        qset = []
        # Pick three distinct templates
        picks = rnd.sample(templates, k=3) if len(templates) >= 3 else [templates[0]] * 3
        for t in picks:
            sentence = t.format(word=w)
            qset.append({'question': sentence, 'answer': w})

        items.append({'word': w, 'questions': qset, 'sources': [{'month': 'June', 'subject': 'ENGLISH'}]})

    out = {'meta': {'source': 'generated_from_templates', 'count': len(items)}, 'items': items}

    with dest.open('w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    return jsonify({'written': dest.as_posix(), 'count': len(items)})


@fillgen_bp.route('/import-fill-questions', methods=['POST'])
def import_fill_questions():
    """Import the two JSON files into the `FillQuestion` table.

    Allowed only in debug mode to avoid accidental writes in production.
    """
    app = current_app._get_current_object()
    if not app.debug:
        return jsonify({'error': 'Import allowed only in debug mode'}), 403

    base = Path(app.root_path) / 'data'
    files = [
        base / 'fill_questions_june_july_aug_sept.json',
        base / 'fill_questions_oct_nov_dec_jan_feb.json',
    ]

    imported = 0
    for f in files:
        if not f.exists():
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
                # Avoid duplicates: simple lookup
                exists = FillQuestion.query.filter_by(word=word, question=question_text).first()
                if exists:
                    continue
                fq = FillQuestion(word=word, question=question_text, answer=answer,
                                  month=(it.get('month') or 'June'), subject=(it.get('subject') or 'ENGLISH'),
                                  source_file=str(f.name))
                db.session.add(fq)
                imported += 1
    db.session.commit()
    return jsonify({'imported': imported})
