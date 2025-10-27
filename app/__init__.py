import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////app/data/secretsanta.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD', 'admin')

    # Email configuration
    app.config['SMTP_SERVER'] = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    app.config['SMTP_PORT'] = int(os.getenv('SMTP_PORT', '587'))
    app.config['SMTP_USERNAME'] = os.getenv('SMTP_USERNAME', '')
    app.config['SMTP_PASSWORD'] = os.getenv('SMTP_PASSWORD', '')
    app.config['FROM_EMAIL'] = os.getenv('FROM_EMAIL', '')

    db.init_app(app)

    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
