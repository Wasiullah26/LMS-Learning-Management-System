"""
Enrollment routes
"""

from flask import Blueprint, request, jsonify
from models.enrollment import EnrollmentModel
from utils.auth import token_required, student_required

enrollments_bp = Blueprint("enrollments", __name__)
enrollment_model = EnrollmentModel()


@enrollments_bp.route("", methods=["POST"])
@student_required
def create_enrollment():
    """Enroll in a course (student only)"""
    try:
        data = request.get_json()
        course_id = data.get("courseId")

        if not course_id:
            return jsonify({"error": "courseId required"}), 400

        student_id = request.current_user["user_id"]
        status = data.get("status", "active")

        success, result = enrollment_model.create_enrollment(student_id=student_id, course_id=course_id, status=status)

        if success:
            return jsonify({"message": "Enrolled successfully", "enrollment": result}), 201
        else:
            return jsonify({"error": result}), 400

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@enrollments_bp.route("", methods=["GET"])
@token_required
def list_enrollments():
    """Get enrollments"""
    try:
        current_user_id = request.current_user["user_id"]
        current_user_role = request.current_user["role"]

        course_id = request.args.get("courseId")

        if current_user_role == "student":
            # Students see their own enrollments
            enrollments = enrollment_model.get_enrollments_by_student(current_user_id)
        elif current_user_role == "instructor" and course_id:
            # Instructors can see enrollments for their courses
            enrollments = enrollment_model.get_enrollments_by_course(course_id)
        else:
            return jsonify({"error": "Invalid request"}), 400

        return jsonify({"enrollments": enrollments}), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@enrollments_bp.route("/<enrollment_id>", methods=["DELETE"])
@student_required
def delete_enrollment(enrollment_id):
    """Unenroll from course (student only)"""
    try:
        student_id = request.current_user["user_id"]

        success, error_msg = enrollment_model.delete_enrollment(enrollment_id, student_id)

        if success:
            return jsonify({"message": "Unenrolled successfully"}), 200
        else:
            return jsonify({"error": error_msg}), 400

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
