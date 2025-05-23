from flask import Blueprint, request, jsonify
from .models import db, UserReview
import re

def word_count(text):
    return len(re.findall(r'\w+', text))

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/reviews', methods=['GET'])
def get_reviews():
    reviews = UserReview.query.order_by(UserReview.timestamp.desc()).all()
    return jsonify([
        {
            'username': r.username,
            'position': r.position,
            'review': r.review,
            'rating': r.rating,
            'timestamp': r.timestamp.strftime('%Y-%m-%d %H:%M')
        } for r in reviews
    ])

@reviews_bp.route('/reviews', methods=['POST'])
def post_review():
    data = request.json
    username = data.get('username', '').strip()
    position = data.get('position', '').strip()
    review = data.get('review', '').strip()
    rating = data.get('rating', 4)
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            rating = 4
    except Exception:
        rating = 4

    # Server-side validation
    errors = []
    if not username or len(username) < 2:
        errors.append("Username must be at least 2 characters.")
    if position and len(position) > 50:
        errors.append("Position/Role must be 50 characters or less.")
    wc = word_count(review)
    if not review or wc < 20 or wc > 200:
        errors.append("Review must be between 20 and 200 words.")
    if re.search(r'(http|www\\.|<script)', review, re.IGNORECASE):
        errors.append("Links and scripts are not allowed in reviews.")
    if errors:
        return jsonify({'success': False, 'errors': errors}), 400
    new_review = UserReview(username=username, position=position, review=review, rating=rating)
    db.session.add(new_review)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Review posted successfully.'}) 