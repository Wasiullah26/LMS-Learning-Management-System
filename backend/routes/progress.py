from flask import Blueprint, request, jsonify
from models.progress import ProgressModel
from utils.auth import student_required

progress_bp = Blueprint("progress", __name__)
progress_model = ProgressModel()


@progress_bp.route("", methods=["POST"])
@student_required
def create_progress():
    try:
        data = request.get_json()

        module_id = data.get("moduleId")
        course_id = data.get("courseId")
        status = data.get("status", "in_progress")

        if not module_id or not course_id:
            return jsonify({"error": "moduleId and courseId required"}), 400

        student_id = request.current_user["user_id"]

        success, result = progress_model.create_progress(
            student_id=student_id, module_id=module_id, course_id=course_id, status=status
        )

        if success:
            return jsonify({"message": "Progress updated", "progress": result}), 201
        else:
            return jsonify({"error": result}), 400

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@progress_bp.route("", methods=["GET"])
@student_required
def get_progress():
    try:
        student_id = request.current_user["user_id"]
        course_id = request.args.get("courseId")

        if course_id:
            progress = progress_model.get_progress_by_course(student_id, course_id)
        else:
            progress = progress_model.get_progress_by_student(student_id)

        return jsonify({"progress": progress}), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@progress_bp.route("/complete", methods=["POST"])
@student_required
def mark_complete():
    try:
        data = request.get_json()

        module_id = data.get("moduleId")
        course_id = data.get("courseId")

        if not module_id or not course_id:
            return jsonify({"error": "moduleId and courseId required"}), 400

        student_id = request.current_user["user_id"]

        success, result = progress_model.mark_complete(student_id=student_id, module_id=module_id, course_id=course_id)

        if success:
            return jsonify({"message": "Module marked as completed", "progress": result}), 200
        else:
            return jsonify({"error": result}), 400

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@progress_bp.route("/stats", methods=["GET"])
@student_required
def get_stats():
    try:
        student_id = request.current_user["user_id"]
        course_id = request.args.get("courseId")

        if not course_id:
            return jsonify({"error": "courseId parameter required"}), 400

        stats = progress_model.get_completion_stats(student_id, course_id)
        return jsonify({"stats": stats}), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
