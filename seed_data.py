"""Seed script to populate sample word lists for testing."""
from app import create_app, db
from models import WordList, Word

def load():
    app = create_app()
    with app.app_context():
        if WordList.query.count() > 0:
            print('Seed data already present; skipping.')
            return
        wl1 = WordList(name='Grade 3 — Common Words', description='Common words for grade 3')
        wl2 = WordList(name='Grade 3 — Animals & Nature', description='Nature words')
        wl3 = WordList(name='Sight Words — Set A', description='Sight words')
        db.session.add_all([wl1, wl2, wl3])
        db.session.commit()
        words1 = ['because','friend','beautiful','different','really','school','through','thought','people','always','every','together','sometimes','something','would']
        for w in words1:
            db.session.add(Word(word=w, hint=f'Example sentence using {w}.', list_id=wl1.id))
        words2 = ['butterfly','ocean','forest','creature','habitat','migrate','season','weather','mountain','valley']
        for w in words2:
            db.session.add(Word(word=w, hint=f'{w} example.', list_id=wl2.id))
        words3 = ['again','carry','early','enough','group','often','until','usually']
        for w in words3:
            db.session.add(Word(word=w, hint=f'{w} example.', list_id=wl3.id))
        db.session.commit()
        print('✅ Seed data loaded successfully!')

if __name__ == '__main__':
    load()
