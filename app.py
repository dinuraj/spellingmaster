from __future__ import annotations
"""Application factory for Spelling Master."""
from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

from extensions import db
from extensions import db, csrf


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    # Ensure the instance folder exists (Flask's instance folder holds the DB)
    try:
        Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    except Exception:
        os.makedirs(app.instance_path, exist_ok=True)

    # Determine database URI: prefer environment, otherwise use absolute path
    default_db_path = Path(app.instance_path) / 'spelling.db'
    default_db_uri = f"sqlite:///{default_db_path.as_posix()}"
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', default_db_uri),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from routes.admin import admin_bp
    from routes.quiz import quiz_bp
    from routes.fillgen import fillgen_bp
    from routes.fillquiz import fillquiz_bp

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(fillgen_bp, url_prefix='/admin')
    app.register_blueprint(fillquiz_bp, url_prefix='/fillquiz')
    app.register_blueprint(quiz_bp, url_prefix='/quiz')

    @app.route('/')
    def index():
        return redirect(url_for('quiz_bp.index'))

    # Create DB tables if missing
    with app.app_context():
        db.create_all()

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
