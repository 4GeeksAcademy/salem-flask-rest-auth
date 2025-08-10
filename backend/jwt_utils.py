"""
JWT Authentication utilities
"""
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from models import User

def jwt_required_custom(optional=False):
    """
    Custom JWT required decorator that works with both Authorization header and query params
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Try to verify JWT from request
                verify_jwt_in_request(optional=optional)
                return f(*args, **kwargs)
            except Exception as e:
                if optional:
                    return f(*args, **kwargs)
                return jsonify({"msg": "Token required"}), 401
        return decorated_function
    return decorator

def get_current_user():
    """
    Get the current authenticated user from JWT token
    """
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return None
        user = User.query.get(user_id)
        return user
    except:
        return None

def admin_required(f):
    """
    Decorator to require admin privileges
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"msg": "Authentication required"}), 401
        
        # Check if user is admin (you can implement your own admin logic)
        if user.email != 'admin@starwars.com':
            return jsonify({"msg": "Admin privileges required"}), 403
        
        return f(*args, **kwargs)
    return decorated_function
