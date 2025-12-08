import jwt
import datetime
from functools import wraps
from flask import request, jsonify
from config import Config


def generate_token(user_id, role):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=Config.JWT_EXPIRATION_HOURS),
        "iat": datetime.datetime.utcnow(),
    }

    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    return token


def verify_token(token):
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_from_request():
    auth_header = request.headers.get("Authorization")
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
            return token
        except IndexError:
            return None
    return None


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "Token is invalid or expired"}), 401

        request.current_user = {"user_id": payload["user_id"], "role": payload["role"]}

        return f(*args, **kwargs)

    return decorated


def instructor_required(f):
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.current_user["role"] != "instructor":
            return jsonify({"error": "Instructor access required"}), 403
        return f(*args, **kwargs)

    return decorated


def student_required(f):
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.current_user["role"] != "student":
            return jsonify({"error": "Student access required"}), 403
        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.current_user["role"] != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)

    return decorated
