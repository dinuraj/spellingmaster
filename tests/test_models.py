from extensions import db
from models import WordList, Word, QuizResult


def test_models_crud(app):
    with app.app_context():
        wl = WordList(name='ModelList', description='desc')
        db.session.add(wl)
        db.session.commit()
        w = Word(word='apple', hint='fruit', list_id=wl.id)
        db.session.add(w)
        db.session.commit()
        assert wl.words.count() == 1
        qr = QuizResult(list_id=wl.id, total_words=1, correct_count=1, missed_words='[]')
        db.session.add(qr)
        db.session.commit()
        assert qr.score_percent == 100.0
