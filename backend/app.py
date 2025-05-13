from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db
from auth_routes import auth_bp
from nlp_routes import nlp_bp
from reviews import reviews_bp

def create_app():
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Configure SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(nlp_bp)
    app.register_blueprint(reviews_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app 