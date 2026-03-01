import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app
from extensions import db

app = create_app()

with app.app_context():
    # create tables (simple migration fallback)
    print('Creating database tables (db.create_all)')
    db.create_all()
    # import fill questions
    from routes.fillgen import import_fill_questions
    resp = import_fill_questions()
    try:
        print('Import result:', resp.get_json())
    except Exception:
        print('Import called; check logs for details')

    print('Seed complete')
