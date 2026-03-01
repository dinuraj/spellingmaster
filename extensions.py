"""Application extensions (shared singletons)."""
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

# Single SQLAlchemy instance for the app
db = SQLAlchemy()
# CSRF protection for forms and mutating endpoints
csrf = CSRFProtect()
