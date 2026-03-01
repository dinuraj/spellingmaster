import sys
from pathlib import Path
import pytest

# Ensure project root is on sys.path so tests can import app, extensions, etc.
root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from app import create_app
from extensions import db as _db


@pytest.fixture(scope='session')
def app():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
