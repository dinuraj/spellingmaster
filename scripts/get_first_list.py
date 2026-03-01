import sys, os
root = os.path.dirname(os.path.dirname(__file__))
if root not in sys.path:
    sys.path.insert(0, root)

from app import create_app
from models import WordList

app = create_app()
with app.app_context():
    wl = WordList.query.first()
    print(wl.id if wl else '')
