import boto3
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
from config import Config


class EnrollmentModel:

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

        self.table = self.dynamodb.Table(Config.DYNAMODB_ENROLLMENTS_TABLE)

    def create_enrollment(self, student_id, course_id, status="active"):
        try:
            existing = self.get_enrollment_by_student_and_course(student_id, course_id)
            if existing:
                return False, "Already enrolled in this course"

            enrollment_id = str(uuid.uuid4())
            current_time = datetime.utcnow().isoformat()

            enrollment_data = {
                "enrollmentId": enrollment_id,
                "studentId": student_id,
                "courseId": course_id,
                "status": status,
                "enrolledAt": current_time,
            }

            self.table.put_item(Item=enrollment_data)
            return True, enrollment_data

        except ClientError as e:
            return False, f"Error creating enrollment: {str(e)}"

    def get_enrollment(self, enrollment_id, student_id):
        try:
            response = self.table.get_item(Key={"enrollmentId": enrollment_id, "studentId": student_id})
            return response.get("Item")
        except ClientError:
            return None

    def get_enrollment_by_student_and_course(self, student_id, course_id):
        try:
            response = self.table.scan(
                FilterExpression="studentId = :studentId AND courseId = :courseId",
                ExpressionAttributeValues={":studentId": student_id, ":courseId": course_id},
            )
            items = response.get("Items", [])
            return items[0] if items else None
        except ClientError:
            return None

    def get_enrollments_by_student(self, student_id):
        try:
            response = self.table.scan(
                FilterExpression="studentId = :studentId", ExpressionAttributeValues={":studentId": student_id}
            )
            return response.get("Items", [])
        except ClientError:
            return []

    def get_enrollments_by_course(self, course_id):
        try:
            response = self.table.scan(
                FilterExpression="courseId = :courseId", ExpressionAttributeValues={":courseId": course_id}
            )
            return response.get("Items", [])
        except ClientError:
            return []

    def update_enrollment_status(self, enrollment_id, student_id, status):
        try:
            self.table.update_item(
                Key={"enrollmentId": enrollment_id, "studentId": student_id},
                UpdateExpression="SET #status = :status",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={":status": status},
                ReturnValues="ALL_NEW",
            )

            updated_enrollment = self.get_enrollment(enrollment_id, student_id)
            return True, updated_enrollment

        except ClientError as e:
            return False, f"Error updating enrollment: {str(e)}"

    def delete_enrollment(self, enrollment_id, student_id):
        try:
            self.table.delete_item(Key={"enrollmentId": enrollment_id, "studentId": student_id})
            return True, None
        except ClientError as e:
            return False, f"Error deleting enrollment: {str(e)}"
