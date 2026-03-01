from app import create_app
import json


def test_play_and_finish_grading():
    app = create_app({'TESTING': True, 'WTF_CSRF_ENABLED': False})
    app.debug = True
    with app.app_context():
        client = app.test_client()
        # ensure questions exist (run import)
        client.post('/admin/import-fill-questions')

        # start small quiz
        r = client.get('/fillquiz/start?size=10')
        assert r.status_code == 200
        start = r.get_json()
        aid = start['attempt_id']

        # fetch page 1
        p1 = client.get(f'/fillquiz/play?attempt_id={aid}&page=1')
        assert p1.status_code == 200
        data = p1.get_json()
        questions = data['questions']
        # prepare answers with half correct, half wrong
        answers = {}
        for i, q in enumerate(questions):
            qid = q['id']
            # fetch correct answer from DB via page / use import
            # call finish will grade against DB
            if i % 2 == 0:
                # leave correct by fetching the FillQuestion from DB via model
                from models import FillQuestion
                fq = FillQuestion.query.get(qid)
                answers[str(qid)] = fq.answer
            else:
                answers[str(qid)] = 'wronganswer'

        # submit full quiz answers (only for first page we set answers; others left blank)
        finish = client.post('/fillquiz/finish', json={'attempt_id': aid, 'answers': answers})
        assert finish.status_code == 200
        res = finish.get_json()
        assert 'correct' in res and 'total' in res
        assert res['total'] == start['total']
        # correct should be <= total
        assert 0 <= res['correct'] <= res['total']
