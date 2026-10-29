"""Fábrica da aplicação Clube Aurora."""

import os
from pathlib import Path

from flask import Flask

from . import db


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
        DATABASE=os.environ.get("DATABASE", str(Path(app.instance_path) / "aurora.db")),
        SEED_PASSWORD=os.environ.get("SEED_PASSWORD", "dev-only-change-me"),
    )
    if test_config:
        app.config.update(test_config)

    db_path = Path(app.config["DATABASE"])
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        app.config["DATABASE"] = str(Path("/tmp") / "aurora.db")

    app.teardown_appcontext(db.close_db)

    from .main import bp

    app.register_blueprint(bp)

    @app.after_request
    def add_security_headers(response):
        """Aplica os cabeçalhos defensivos a todas as respostas HTTP."""
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
        )
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.cli.command("init-db")
    def init_db_command():
        """Recria o banco com dados de exemplo."""
        db.init_db()
        print("Banco inicializado.")

    with app.app_context():
        if not Path(app.config["DATABASE"]).exists() or os.path.getsize(app.config["DATABASE"]) == 0:
            db.init_db()

    return app
