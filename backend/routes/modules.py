"""
Module management routes
"""

from flask import Blueprint, request, jsonify
from models.module import ModuleModel
from utils.auth import token_required, instructor_required
from utils.validators import validate_required_fields

modules_bp = Blueprint('modules', __name__)
module_model = ModuleModel()


@modules_bp.route('/courses/<course_id>/modules', methods=['GET'])
@token_required
def list_modules(course_id):
    """List all modules for a course"""
    try:
        modules = module_model.get_modules_by_course(course_id)
        return jsonify({'modules': modules}), 200
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@modules_bp.route('/<module_id>', methods=['GET'])
@token_required
def get_module(module_id):
    """Get module details"""
    try:
        course_id = request.args.get('courseId')
        if not course_id:
            return jsonify({'error': 'courseId parameter required'}), 400
        
        module = module_model.get_module(module_id, course_id)
        if module:
            return jsonify({'module': module}), 200
        else:
            return jsonify({'error': 'Module not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@modules_bp.route('/courses/<course_id>/modules', methods=['POST'])
@instructor_required
def create_module(course_id):
    """Create a new module (instructor only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'order']
        is_valid, missing = validate_required_fields(data, required_fields)
        if not is_valid:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
        
        title = data.get('title')
        description = data.get('description')
        order = data.get('order')
        materials = data.get('materials', [])
        
        success, result = module_model.create_module(
            course_id=course_id,
            title=title,
            description=description,
            order=order,
            materials=materials
        )
        
        if success:
            return jsonify({'message': 'Module created successfully', 'module': result}), 201
        else:
            return jsonify({'error': result}), 400
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@modules_bp.route('/<module_id>', methods=['PUT'])
@instructor_required
def update_module(module_id):
    """Update module (instructor only)"""
    try:
        data = request.get_json()
        course_id = data.get('courseId')
        
        if not course_id:
            return jsonify({'error': 'courseId required in request body'}), 400
        
        update_data = {}
        if 'title' in data:
            update_data['title'] = data['title']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'order' in data:
            update_data['order'] = data['order']
        if 'materials' in data:
            update_data['materials'] = data['materials']
        
        if not update_data:
            return jsonify({'error': 'No fields to update'}), 400
        
        success, result = module_model.update_module(
            module_id=module_id,
            course_id=course_id,
            **update_data
        )
        
        if success:
            return jsonify({'message': 'Module updated successfully', 'module': result}), 200
        else:
            return jsonify({'error': result}), 400
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@modules_bp.route('/<module_id>', methods=['DELETE'])
@instructor_required
def delete_module(module_id):
    """Delete module (instructor only)"""
    try:
        course_id = request.args.get('courseId')
        if not course_id:
            return jsonify({'error': 'courseId parameter required'}), 400
        
        success, error_msg = module_model.delete_module(module_id, course_id)
        
        if success:
            return jsonify({'message': 'Module deleted successfully'}), 200
        else:
            return jsonify({'error': error_msg}), 400
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

