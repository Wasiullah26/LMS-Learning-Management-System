"""
File upload routes for S3
"""

from flask import Blueprint, request, jsonify
from utils.auth import instructor_required
from utils.s3 import upload_file_to_s3
from utils.validators import validate_file_extension, validate_file_size
from config import Config

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("", methods=["POST"])
@instructor_required
def upload_file():
    """Upload file to S3 (instructor only)"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        folder_path = request.form.get("folderPath", "")

        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Validate file extension
        if not validate_file_extension(file.filename, Config.ALLOWED_EXTENSIONS):
            return (
                jsonify({"error": f'File type not allowed. Allowed types: {", ".join(Config.ALLOWED_EXTENSIONS)}'}),
                400,
            )

        # Validate file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning

        if not validate_file_size(file_size, Config.MAX_UPLOAD_SIZE):
            return jsonify({"error": f"File too large. Maximum size: {Config.MAX_UPLOAD_SIZE / (1024*1024)}MB"}), 400

        # Upload to S3
        success, result = upload_file_to_s3(file, folder_path)

        if success:
            return jsonify({"message": "File uploaded successfully", "url": result}), 201
        else:
            return jsonify({"error": result}), 500

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
