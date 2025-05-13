from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models import db, User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@auth_bp.route('/php_auth/login.php', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'errors': ['Please provide both username and password']})
    
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password_hash, password):
        # Update last login time
        user.last_login = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'errors': ['Invalid username or password']})

@auth_bp.route('/php_auth/register.php', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    position = request.form.get('position', 'User')
    
    errors = []
    
    # Validation
    if not username or len(username) < 3:
        errors.append('Username must be at least 3 characters')
    if not password or len(password) < 8:
        errors.append('Password must be at least 8 characters')
    if not email or '@' not in email:
        errors.append('Please provide a valid email address')
    
    if errors:
        return jsonify({'success': False, 'errors': errors})
    
    # Check if username or email already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'errors': ['Username already exists']})
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'errors': ['Email already registered']})
    
    # Create new user
    new_user = User(
        username=username,
        password_hash=generate_password_hash(password),
        email=email,
        position=position,
        role='user'
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'errors': ['Registration failed. Please try again.']}) 