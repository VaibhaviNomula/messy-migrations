"""Flask application initialization and configuration.

This module initializes the Flask application, sets up extensions like Bcrypt,
and registers blueprints. Blueprint imports are intentionally placed after
app initialization to avoid circular dependencies.
"""

from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

from app.routes.user import user_bp
app.register_blueprint(user_bp)
