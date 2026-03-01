import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app

app = create_app()
app.debug = True

with app.app_context():
    from extensions import db
    from models import FillQuestion, FillQuizAttempt

    client = app.test_client()

    # Start a 30-word quiz
    resp = client.get('/fillquiz/start?size=30')
    print('start status:', resp.status_code)
    data = resp.get_json()
    print('start response:', data)
    attempt_id = data.get('attempt_id')

    # Load attempt to get question ids
    attempt = FillQuizAttempt.query.get(attempt_id)
    qids = []
    if attempt and attempt.question_ids:
        import json
        qids = json.loads(attempt.question_ids)

    print('question count:', len(qids))

    # Build answers dict using correct answers from DB
    answers = {}
    for qid in qids:
        q = FillQuestion.query.get(qid)
        if q:
            answers[str(qid)] = q.answer

    # Submit full quiz
    finish = client.post('/fillquiz/finish', json={'attempt_id': attempt_id, 'answers': answers})
    print('finish status:', finish.status_code)
    print('finish response:', finish.get_json())

    # Fetch results page HTML (render template)
    r = client.get(f'/fillquiz/results?attempt_id={attempt_id}')
    print('results status:', r.status_code)
    html = r.get_data(as_text=True)
    print('results preview:\n', html[:800])

    # Done
    print('smoke test complete')
