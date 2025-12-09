import boto3
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
from config import Config


class ProgressModel:

    def __init__(self):
        if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
            client_kwargs = {
                "region_name": Config.AWS_REGION,
                "aws_access_key_id": Config.AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": Config.AWS_SECRET_ACCESS_KEY,
            }
            if Config.AWS_SESSION_TOKEN:
                client_kwargs["aws_session_token"] = Config.AWS_SESSION_TOKEN
            self.dynamodb = boto3.resource("dynamodb", **client_kwargs)
        else:
            self.dynamodb = boto3.resource("dynamodb", region_name=Config.AWS_REGION)

        self.table = self.dynamodb.Table(Config.DYNAMODB_PROGRESS_TABLE)

    def create_progress(self, student_id, module_id, course_id, status="in_progress"):
        try:
            existing = self.get_progress(student_id, module_id, course_id)

            if existing:
                progress_id = existing["progressId"]
            else:
                progress_id = str(uuid.uuid4())

            current_time = datetime.utcnow().isoformat()

            progress_data = {
                "progressId": progress_id,
                "studentId": student_id,
                "moduleId": module_id,
                "courseId": course_id,
                "status": status,
                "completedAt": current_time if status == "completed" else None,
            }

            self.table.put_item(Item=progress_data)
            return True, progress_data

        except ClientError as e:
            return False, f"Error creating progress: {str(e)}"

    def get_progress(self, student_id, module_id, course_id):
        try:
            response = self.table.scan(
                FilterExpression="studentId = :studentId AND moduleId = :moduleId AND courseId = :courseId",
                ExpressionAttributeValues={":studentId": student_id, ":moduleId": module_id, ":courseId": course_id},
            )
            items = response.get("Items", [])
            return items[0] if items else None
        except ClientError:
            return None

    def get_progress_by_student(self, student_id):
        try:
            response = self.table.query(
                KeyConditionExpression="studentId = :studentId", ExpressionAttributeValues={":studentId": student_id}
            )
            return response.get("Items", [])
        except ClientError:
            return []

    def get_progress_by_course(self, student_id, course_id):
        try:
            response = self.table.scan(
                FilterExpression="studentId = :studentId AND courseId = :courseId",
                ExpressionAttributeValues={":studentId": student_id, ":courseId": course_id},
            )
            return response.get("Items", [])
        except ClientError:
            return []

    def mark_complete(self, student_id, module_id, course_id):
        return self.create_progress(student_id, module_id, course_id, status="completed")

    def get_completion_stats(self, student_id, course_id):
        try:
            progress_records = self.get_progress_by_course(student_id, course_id)
            completed = sum(1 for p in progress_records if p.get("status") == "completed")
            total = len(progress_records)

            return {"completed": completed, "total": total, "percentage": (completed / total * 100) if total > 0 else 0}
        except Exception:
            return {"completed": 0, "total": 0, "percentage": 0}
