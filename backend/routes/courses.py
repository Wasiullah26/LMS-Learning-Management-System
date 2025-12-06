"""
Course management routes
"""

from flask import Blueprint, request, jsonify
from models.course import CourseModel
from models.module import ModuleModel
from utils.auth import token_required, instructor_required
from utils.validators import validate_required_fields

courses_bp = Blueprint('courses', __name__)
course_model = CourseModel()
module_model = ModuleModel()


@courses_bp.route('', methods=['GET'])
@token_required
def list_courses():
    """List courses - filtered by role and specialization"""
    try:
        current_user = request.current_user
        user_role = current_user.get('role')
        user_id = current_user.get('user_id')
        
        # Get user's specialization if they are a student
        specialization_id = None
        if user_role == 'student':
            from models.user import UserModel
            user_model = UserModel()
            user = user_model.get_user_by_id(user_id)
            if user and user.get('specializationId'):
                specialization_id = user.get('specializationId')
        
        # Get query parameters
        instructor_id = request.args.get('instructorId')
        category = request.args.get('category')
        
        # For students, filter by their specialization
        if user_role == 'student' and specialization_id:
            courses = course_model.list_courses(specialization_id=specialization_id)
        # For instructors, filter by their instructorId (unless explicitly filtered by another instructorId)
        elif user_role == 'instructor':
            # If instructorId is provided in query params, use it (for admin viewing instructor's courses)
            # Otherwise, filter by the logged-in instructor's ID
            filter_instructor_id = instructor_id if instructor_id else user_id
            courses = course_model.list_courses(instructor_id=filter_instructor_id, category=category)
        # For admins, show all courses (unless filtered by instructorId)
        else:
            courses = course_model.list_courses(
                instructor_id=instructor_id,
                category=category
            )
        
        return jsonify({'courses': courses}), 200
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@courses_bp.route('/<course_id>', methods=['GET'])
@token_required
def get_course(course_id):
    """Get course details with modules"""
    try:
        course = course_model.get_course(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Get modules for this course
        modules = module_model.get_modules_by_course(course_id)
        course['modules'] = modules
        
        return jsonify({'course': course}), 200
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@courses_bp.route('', methods=['POST'])
@instructor_required
def create_course():
    """Create a new course (instructor only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description']
        is_valid, missing = validate_required_fields(data, required_fields)
        if not is_valid:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
        
        instructor_id = request.current_user['user_id']
        title = data.get('title')
        description = data.get('description')
        category = data.get('category')
        
        success, result = course_model.create_course(
            instructor_id=instructor_id,
            title=title,
            description=description,
            category=category
        )
        
        if success:
            return jsonify({'message': 'Course created successfully', 'course': result}), 201
        else:
            return jsonify({'error': result}), 400
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@courses_bp.route('/<course_id>', methods=['PUT'])
@instructor_required
def update_course(course_id):
    """Update course (instructor only)"""
    try:
        data = request.get_json()
        instructor_id = request.current_user['user_id']
        
        update_data = {}
        if 'title' in data:
            update_data['title'] = data['title']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'category' in data:
            update_data['category'] = data['category']
        
        if not update_data:
            return jsonify({'error': 'No fields to update'}), 400
        
        success, result = course_model.update_course(
            course_id=course_id,
            instructor_id=instructor_id,
            **update_data
        )
        
        if success:
            return jsonify({'message': 'Course updated successfully', 'course': result}), 200
        else:
            return jsonify({'error': result}), 400
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@courses_bp.route('/<course_id>', methods=['DELETE'])
@instructor_required
def delete_course(course_id):
    """Delete course (instructor only)"""
    try:
        instructor_id = request.current_user['user_id']
        
        success, error_msg = course_model.delete_course(
            course_id=course_id,
            instructor_id=instructor_id
        )
        
        if success:
            return jsonify({'message': 'Course deleted successfully'}), 200
        else:
            return jsonify({'error': error_msg}), 400
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

