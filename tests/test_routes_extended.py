from extensions import db
from models import WordList, Word


def test_admin_add_word_json(app, client):
    with app.app_context():
        wl = WordList(name='JsonList', description='d')
        db.session.add(wl)
        db.session.commit()
        lid = wl.id
    # Add word via JSON endpoint
    res = client.post(f'/admin/list/{lid}/word/add', json={'word': 'hello', 'hint': 'greet'})
    assert res.status_code == 200
    data = res.get_json()
    assert data.get('success') is True


def test_quiz_flow(app, client):
    with app.app_context():
        wl = WordList(name='QList', description='q')
        db.session.add(wl)
        db.session.commit()
        w = Word(word='cat', hint='', list_id=wl.id)
        db.session.add(w)
        db.session.commit()
        lid = wl.id
    # Start quiz (form POST)
    res = client.post('/quiz/start', json={'list_id': lid}, follow_redirects=True)
    assert res.status_code in (200, 302)
    # Play page
    res = client.get('/quiz/play')
    assert res.status_code == 200
    # Submit correct answer
    res = client.post('/quiz/check', json={'answer': 'cat'})
    assert res.status_code == 200
    data = res.get_json()
    assert 'correct' in data
