"""
User management routes
"""

from flask import Blueprint, request, jsonify
from models.user import UserModel
from utils.auth import token_required, instructor_required
from utils.validators import validate_email, validate_password, validate_role, validate_required_fields

users_bp = Blueprint('users', __name__)
user_model = UserModel()


@users_bp.route('', methods=['GET'])
@instructor_required
def list_users():
    """List all users (instructor only)"""
    try:
        role = request.args.get('role')
        users = user_model.list_users(role=role)
        return jsonify({'users': users}), 200
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@users_bp.route('/<user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """Get user by ID"""
    try:
        # Users can only view their own profile unless they're instructors
        current_user_id = request.current_user['user_id']
        current_user_role = request.current_user['role']
        
        if user_id != current_user_id and current_user_role != 'instructor':
            return jsonify({'error': 'Unauthorized'}), 403
        
        user = user_model.get_user_by_id(user_id)
        if user:
            return jsonify({'user': user}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@users_bp.route('/<user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    """Update user information"""
    try:
        # Users can only update their own profile
        current_user_id = request.current_user['user_id']
        if user_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        update_data = {}
        
        # Validate and add fields to update
        if 'name' in data:
            update_data['name'] = data['name']
        
        if 'email' in data:
            if not validate_email(data['email']):
                return jsonify({'error': 'Invalid email format'}), 400
            update_data['email'] = data['email']
        
        if 'password' in data:
            is_valid, error_msg = validate_password(data['password'])
            if not is_valid:
                return jsonify({'error': error_msg}), 400
            update_data['password'] = data['password']
        
        if not update_data:
            return jsonify({'error': 'No fields to update'}), 400
        
        success, result = user_model.update_user(user_id, **update_data)
        
        if success:
            return jsonify({'message': 'User updated successfully', 'user': result}), 200
        else:
            return jsonify({'error': result}), 400
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@users_bp.route('/<user_id>', methods=['DELETE'])
@instructor_required
def delete_user(user_id):
    """Delete user (instructor only)"""
    try:
        success, error_msg = user_model.delete_user(user_id)
        
        if success:
            return jsonify({'message': 'User deleted successfully'}), 200
        else:
            return jsonify({'error': error_msg}), 400
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

