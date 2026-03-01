import sys
from pathlib import Path

# Ensure project root is on sys.path when running from scripts/
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app

app = create_app()
app.debug = True

with app.app_context():
    from routes.fillgen import import_fill_questions
    resp = import_fill_questions()
    try:
        out = resp.get_json()
    except Exception:
        out = str(resp)
    import json
    print(json.dumps(out, indent=2, ensure_ascii=False))
