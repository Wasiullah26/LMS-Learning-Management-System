"""
Admin routes for managing users, specializations, and courses
"""

from flask import Blueprint, request, jsonify
from models.user import UserModel
from models.specialization import SpecializationModel
from models.course import CourseModel
from utils.auth import admin_required
from utils.validators import validate_email, validate_password, validate_required_fields

admin_bp = Blueprint('admin', __name__)
user_model = UserModel()
specialization_model = SpecializationModel()
course_model = CourseModel()


@admin_bp.route('/students', methods=['POST'])
@admin_required
def add_student():
    """Add a new student (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'name', 'specializationId']
        is_valid, missing = validate_required_fields(data, required_fields)
        if not is_valid:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
        
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        specialization_id = data.get('specializationId')
        
        # Validate email
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Verify specialization exists
        specialization = specialization_model.get_specialization(specialization_id)
        if not specialization:
            return jsonify({'error': 'Specialization not found'}), 400
        
        # Create student
        success, result = user_model.create_user(
            email=email,
            password=password,
            role='student',
            name=name,
            specialization_id=specialization_id
        )
        
        if success:
            return jsonify({
                'message': 'Student created successfully',
                'user': result
            }), 201
        else:
            return jsonify({'error': result}), 400
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@admin_bp.route('/instructors', methods=['POST'])
@admin_required
def add_instructor():
    """Add a new instructor (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'name', 'specializationId', 'courseIds']
        is_valid, missing = validate_required_fields(data, required_fields)
        if not is_valid:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
        
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        specialization_id = data.get('specializationId')
        course_ids = data.get('courseIds')
        
        # Validate email
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Validate courseIds is a list
        if not isinstance(course_ids, list) or len(course_ids) == 0:
            return jsonify({'error': 'At least one course must be selected'}), 400
        
        # Verify specialization exists
        specialization = specialization_model.get_specialization(specialization_id)
        if not specialization:
            return jsonify({'error': 'Specialization not found'}), 400
        
        # Verify all courses exist and belong to specialization
        for course_id in course_ids:
            course = course_model.get_course(course_id)
            if not course:
                return jsonify({'error': f'Course {course_id} not found'}), 400
            if course.get('specializationId') != specialization_id:
                return jsonify({'error': f'Course {course_id} does not belong to the selected specialization'}), 400
        
        # Check if instructor already exists
        existing_instructor = user_model.get_user_by_email(email)
        if existing_instructor:
            if existing_instructor['role'] != 'instructor':
                return jsonify({'error': 'User with this email already exists with a different role'}), 400
            
            # Update existing instructor - add new courses to their courseIds
            existing_course_ids = existing_instructor.get('courseIds', [])
            if isinstance(existing_course_ids, str):
                existing_course_ids = [existing_course_ids]
            
            # Merge course IDs (avoid duplicates)
            updated_course_ids = list(set(existing_course_ids + course_ids))
            
            # Update instructor with new courses
            user_model.update_user(existing_instructor['userId'], courseIds=updated_course_ids)
            
            # Also update the courses' instructorIds array to include this instructor
            for course_id in course_ids:
                course = course_model.get_course(course_id)
                if course:
                    instructor_ids = course.get('instructorIds', [])
                    if isinstance(instructor_ids, str):
                        instructor_ids = [instructor_ids]
                    # Also check single instructorId for backward compatibility
                    if not instructor_ids and course.get('instructorId'):
                        instructor_ids = [course.get('instructorId')]
                    
                    # Add instructor if not already in list
                    if existing_instructor['userId'] not in instructor_ids:
                        instructor_ids.append(existing_instructor['userId'])
                    
                    # Update course with instructorIds array
                    course_model.admin_update_course(
                        course_id,
                        instructorIds=instructor_ids,
                        instructorId=instructor_ids[0] if instructor_ids else None
                    )
            
            # Get updated user
            updated_user = user_model.get_user_by_id(existing_instructor['userId'])
            updated_user.pop('password', None)
            
            return jsonify({
                'message': 'Instructor updated successfully - courses added',
                'user': updated_user
            }), 200
        
        # Create new instructor
        success, result = user_model.create_user(
            email=email,
            password=password,
            role='instructor',
            name=name,
            specialization_id=specialization_id,
            course_ids=course_ids
        )
        
        if success:
            instructor_id = result['userId']
            
            # Also update the courses' instructorIds array to include this instructor
            for course_id in course_ids:
                course = course_model.get_course(course_id)
                if course:
                    instructor_ids = course.get('instructorIds', [])
                    if isinstance(instructor_ids, str):
                        instructor_ids = [instructor_ids]
                    # Also check single instructorId for backward compatibility
                    if not instructor_ids and course.get('instructorId'):
                        instructor_ids = [course.get('instructorId')]
                    
                    # Add instructor if not already in list
                    if instructor_id not in instructor_ids:
                        instructor_ids.append(instructor_id)
                    
                    # Update course with instructorIds array
                    course_model.admin_update_course(
                        course_id,
                        instructorIds=instructor_ids,
                        instructorId=instructor_ids[0] if instructor_ids else None
                    )
            
            return jsonify({
                'message': 'Instructor created successfully',
                'user': result
            }), 201
        else:
            return jsonify({'error': result}), 400
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@admin_bp.route('/specializations', methods=['GET'])
@admin_required
def list_specializations():
    """List all specializations (admin only)"""
    try:
        specializations = specialization_model.list_specializations()
        return jsonify({'specializations': specializations}), 200
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@admin_bp.route('/specializations', methods=['POST'])
@admin_required
def create_specialization():
    """Create a new specialization (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'code']
        is_valid, missing = validate_required_fields(data, required_fields)
        if not is_valid:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
        
        name = data.get('name')
        code = data.get('code')
        description = data.get('description', '')
        
        success, result = specialization_model.create_specialization(
            name=name,
            code=code,
            description=description
        )
        
        if success:
            return jsonify({
                'message': 'Specialization created successfully',
                'specialization': result
            }), 201
        else:
            return jsonify({'error': result}), 400
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@admin_bp.route('/specializations/<specialization_id>', methods=['PUT'])
@admin_required
def update_specialization(specialization_id):
    """Update a specialization (admin only)"""
    try:
        data = request.get_json()
        
        success, error = specialization_model.update_specialization(
            specialization_id,
            **data
        )
        
        if success:
            specialization = specialization_model.get_specialization(specialization_id)
            return jsonify({
                'message': 'Specialization updated successfully',
                'specialization': specialization
            }), 200
        else:
            return jsonify({'error': error}), 400
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@admin_bp.route('/specializations/<specialization_id>', methods=['DELETE'])
@admin_required
def delete_specialization(specialization_id):
    """Delete a specialization (admin only)"""
    try:
        success, error = specialization_model.delete_specialization(specialization_id)
        
        if success:
            return jsonify({'message': 'Specialization deleted successfully'}), 200
        else:
            return jsonify({'error': error}), 400
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@admin_bp.route('/specializations/<specialization_id>/courses', methods=['GET'])
@admin_required
def get_courses_by_specialization(specialization_id):
    """Get all courses for a specialization (admin only)"""
    try:
        # Verify specialization exists
        specialization = specialization_model.get_specialization(specialization_id)
        if not specialization:
            return jsonify({'error': 'Specialization not found'}), 404
        
        # Try to fix courses missing specializationId before querying
        from predefined_data import COURSES_BY_SPECIALIZATION
        all_courses = course_model.list_courses()
        courses_without_spec = [c for c in all_courses if 'specializationId' not in c]
        
        if courses_without_spec:
            # Get specialization map
            all_specs = specialization_model.list_specializations()
            specialization_map = {spec['code']: spec['specializationId'] for spec in all_specs}
            
            # Build course title to specialization map
            course_title_to_spec = {}
            for spec_code, courses_data in COURSES_BY_SPECIALIZATION.items():
                spec_id = specialization_map.get(spec_code)
                if spec_id:
                    for course_data in courses_data:
                        course_title_to_spec[course_data['title']] = spec_id
            
            # Update courses that can be matched
            for course in courses_without_spec:
                course_title = course.get('title')
                if course_title in course_title_to_spec:
                    spec_id = course_title_to_spec[course_title]
                    course_model.admin_update_course(course['courseId'], specializationId=spec_id)
        
        # Get all courses again after potential updates
        all_courses = course_model.list_courses()
        courses = [c for c in all_courses if c.get('specializationId') == specialization_id]
        
        return jsonify({'courses': courses}), 200
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    """List all users (admin only)"""
    try:
        role = request.args.get('role')
        users = user_model.list_users(role=role)
        
        # Batch fetch all specializations and courses to avoid N+1 queries
        all_specializations = specialization_model.list_specializations()
        specialization_map = {spec['specializationId']: spec['name'] for spec in all_specializations}
        
        # Collect all unique course IDs from instructors
        all_course_ids = set()
        for user in users:
            if user.get('role') == 'instructor' and user.get('courseIds'):
                course_ids = user.get('courseIds', [])
                if isinstance(course_ids, str):
                    course_ids = [course_ids]
                all_course_ids.update(course_ids)
        
        # Batch fetch all courses
        all_courses = course_model.list_courses()
        course_map = {course['courseId']: course['title'] for course in all_courses}
        
        # Enrich users with specialization names and course titles using cached maps
        for user in users:
            # Get specialization name if exists
            if user.get('specializationId'):
                user['specializationName'] = specialization_map.get(user['specializationId'], '-')
            
            # Get course titles for instructors
            if user.get('role') == 'instructor' and user.get('courseIds'):
                course_ids = user.get('courseIds', [])
                if isinstance(course_ids, str):
                    course_ids = [course_ids]
                
                course_titles = [course_map.get(course_id) for course_id in course_ids if course_map.get(course_id)]
                user['courseTitles'] = course_titles
        
        return jsonify({'users': users}), 200
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@admin_bp.route('/courses/<course_id>/instructor', methods=['PUT'])
@admin_required
def update_course_instructor(course_id):
    """Add instructor to course (supports multiple instructors per course)"""
    try:
        data = request.get_json()
        new_instructor_id = data.get('instructorId')
        
        if not new_instructor_id:
            return jsonify({'error': 'instructorId is required'}), 400
        
        # Get current course
        course = course_model.get_course(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Get current instructor IDs (support both formats)
        instructor_ids = course.get('instructorIds', [])
        if isinstance(instructor_ids, str):
            instructor_ids = [instructor_ids]
        # Also check single instructorId for backward compatibility
        if not instructor_ids and course.get('instructorId'):
            instructor_ids = [course.get('instructorId')]
        
        # Add new instructor if not already in the list
        if new_instructor_id not in instructor_ids:
            instructor_ids.append(new_instructor_id)
        
        # Update course with new instructorIds array
        success, result = course_model.admin_update_course(
            course_id,
            instructorIds=instructor_ids,
            instructorId=instructor_ids[0] if instructor_ids else None  # Keep first as instructorId for backward compatibility
        )
        
        if not success:
            return jsonify({'error': result}), 400
        
        # Update new instructor's courseIds (add this course if not already there)
        new_instructor = user_model.get_user_by_id(new_instructor_id)
        if new_instructor:
            new_course_ids = new_instructor.get('courseIds', [])
            if isinstance(new_course_ids, str):
                new_course_ids = [new_course_ids]
            if course_id not in new_course_ids:
                new_course_ids.append(course_id)
                user_model.update_user(new_instructor_id, courseIds=new_course_ids)
        
        return jsonify({
            'message': 'Instructor added to course successfully',
            'course': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@admin_bp.route('/courses', methods=['POST'])
@admin_required
def admin_create_course():
    """Create a course (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'specializationId']
        is_valid, missing = validate_required_fields(data, required_fields)
        if not is_valid:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
        
        title = data.get('title')
        description = data.get('description', '')
        specialization_id = data.get('specializationId')
        instructor_id = data.get('instructorId')  # Optional - can assign later
        
        # Verify specialization exists
        specialization = specialization_model.get_specialization(specialization_id)
        if not specialization:
            return jsonify({'error': 'Specialization not found'}), 400
        
        # If no instructor provided, try to find one, but allow course creation without instructor
        if not instructor_id:
            # Get first instructor for this specialization
            all_instructors = user_model.list_users(role='instructor')
            instructors = [inst for inst in all_instructors if inst.get('specializationId') == specialization_id]
            if instructors:
                instructor_id = instructors[0]['userId']
            else:
                # Try to find any instructor (fallback)
                if all_instructors:
                    instructor_id = all_instructors[0]['userId']
                else:
                    # Allow creating course without instructor - admin can assign later
                    instructor_id = None
        
        # Create course - use provided instructor_id or find one
        # If still no instructor_id, use admin as placeholder (courses need an instructorId field)
        if not instructor_id:
            admin_users = user_model.list_users(role='admin')
            if admin_users:
                instructor_id = admin_users[0]['userId']
            else:
                return jsonify({
                    'error': 'Cannot create course: No instructors or admins available in the system. Please create an instructor first.'
                }), 400
        
        success, result = course_model.create_course(
            instructor_id=instructor_id,
            title=title,
            description=description,
            category='General',
            specialization_id=specialization_id
        )
        
        if success:
            return jsonify({
                'message': 'Course created successfully',
                'course': result
            }), 201
        else:
            return jsonify({'error': result}), 400
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@admin_bp.route('/courses/<course_id>', methods=['DELETE'])
@admin_required
def admin_delete_course(course_id):
    """Delete course (admin only - instructors cannot delete courses)"""
    try:
        success, error_msg = course_model.admin_delete_course(course_id)
        
        if success:
            return jsonify({'message': 'Course deleted successfully'}), 200
        else:
            return jsonify({'error': error_msg}), 400
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@admin_bp.route('/seed-courses', methods=['POST'])
@admin_required
def seed_courses_manual():
    """Manually trigger course seeding (admin only)"""
    try:
        from setup.database_seeder import seed_database
        
        stats = seed_database(silent=False)
        
        return jsonify({
            'message': f'Seeding completed. Created {stats["courses_created"]} courses, {stats["instructors_created"]} instructors, and {stats["modules_created"]} modules.',
            'created_count': stats['courses_created'],
            'instructors_created_count': stats['instructors_created'],
            'modules_created_count': stats['modules_created'],
            'specializations_created': stats['specializations_created'],
            'errors': stats['errors'] if stats['errors'] else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@admin_bp.route('/users/<user_id>/password', methods=['PUT'])
@admin_required
def admin_change_user_password(user_id):
    """Admin changes user password (admin only)"""
    try:
        data = request.get_json()
        
        if 'password' not in data:
            return jsonify({'error': 'Password is required'}), 400
        
        new_password = data.get('password')
        
        # Validate password
        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        success, error = user_model.admin_change_password(user_id, new_password)
        
        if success:
            return jsonify({'message': 'Password changed successfully'}), 200
        else:
            return jsonify({'error': error}), 400
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

