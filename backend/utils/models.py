from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(50))
    review = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=4)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) 