from flask import Blueprint, request, jsonify
from models.user import UserModel
from utils.auth import generate_token, token_required
from utils.validators import validate_password, validate_required_fields

auth_bp = Blueprint("auth", __name__)
user_model = UserModel()


@auth_bp.route("/register", methods=["POST"])
def register():
    # registration is disabled, admin has to create users
    return jsonify({"error": "Registration is disabled. Please contact your administrator to create an account."}), 403


@auth_bp.route("/login", methods=["POST"])
def login():
    # login endpoint, checks email and password then gives token
    try:
        data = request.get_json()

        # check if email and password are provided
        required_fields = ["email", "password"]
        is_valid, missing = validate_required_fields(data, required_fields)
        if not is_valid:
            return jsonify({"error": f'Missing required fields: {", ".join(missing)}'}), 400

        email = data.get("email")
        password = data.get("password")

        # check if user exists and password is correct
        success, result = user_model.authenticate_user(email, password)

        if success:
            # create jwt token
            token = generate_token(result["userId"], result["role"])
            return jsonify({"message": "Login successful", "user": result, "token": token}), 200
        else:
            return jsonify({"error": result}), 401

    except Exception as error:
        return jsonify({"error": f"Server error: {str(error)}"}), 500


@auth_bp.route("/change-password", methods=["POST"])
@token_required
def change_password():
    # user can change their password here
    try:
        data = request.get_json()

        # check required fields
        required_fields = ["oldPassword", "newPassword"]
        is_valid, missing = validate_required_fields(data, required_fields)
        if not is_valid:
            return jsonify({"error": f'Missing required fields: {", ".join(missing)}'}), 400

        old_password = data.get("oldPassword")
        new_password = data.get("newPassword")

        # validate new password strength
        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        user_id = request.current_user["user_id"]

        # update password
        success, error = user_model.change_password(user_id, old_password, new_password)

        if success:
            return jsonify({"message": "Password changed successfully"}), 200
        else:
            return jsonify({"error": error}), 400

    except Exception as error:
        return jsonify({"error": f"Server error: {str(error)}"}), 500
