import boto3
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
from config import Config


class CourseModel:

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

        self.table = self.dynamodb.Table(Config.DYNAMODB_COURSES_TABLE)

    def create_course(
        self, instructor_id, title, description, category=None, specialization_id=None, instructor_ids=None
    ):
        try:
            course_id = str(uuid.uuid4())
            current_time = datetime.utcnow().isoformat()

            course_data = {
                "courseId": course_id,
                "title": title,
                "description": description,
                "category": category or "General",
                "createdAt": current_time,
                "updatedAt": current_time,
            }

            if instructor_ids and isinstance(instructor_ids, list):
                course_data["instructorIds"] = instructor_ids
                if instructor_ids:
                    course_data["instructorId"] = instructor_ids[0]
            else:
                course_data["instructorId"] = instructor_id
                course_data["instructorIds"] = [instructor_id] if instructor_id else []

            if specialization_id:
                course_data["specializationId"] = specialization_id

            self.table.put_item(Item=course_data)
            return True, course_data

        except ClientError as error:
            return False, f"Error creating course: {str(error)}"

    def get_course(self, course_id):
        try:
            response = self.table.get_item(Key={"courseId": course_id})
            return response.get("Item")
        except ClientError:
            return None

    def update_course(self, course_id, instructor_id, **kwargs):
        try:
            course = self.get_course(course_id)
            if not course:
                return False, "Course not found"

            instructor_ids = course.get("instructorIds", [])
            if isinstance(instructor_ids, str):
                instructor_ids = [instructor_ids]
            single_instructor_id = course.get("instructorId")

            if instructor_id not in instructor_ids and single_instructor_id != instructor_id:
                return False, "Unauthorized to update this course"

            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}

            for key, value in kwargs.items():
                update_expression += f"#{key} = :{key}, "
                expression_attribute_names[f"#{key}"] = key
                expression_attribute_values[f":{key}"] = value

            update_expression += "#updatedAt = :updatedAt"
            expression_attribute_names["#updatedAt"] = "updatedAt"
            expression_attribute_values[":updatedAt"] = datetime.utcnow().isoformat()

            self.table.update_item(
                Key={"courseId": course_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW",
            )

            updated_course = self.get_course(course_id)
            return True, updated_course

        except ClientError as error:
            return False, f"Error updating course: {str(error)}"

    def admin_update_course(self, course_id, **kwargs):
        try:
            course = self.get_course(course_id)
            if not course:
                return False, "Course not found"

            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}

            for key, value in kwargs.items():
                if value is not None:
                    update_expression += f"#{key} = :{key}, "
                    expression_attribute_names[f"#{key}"] = key
                    expression_attribute_values[f":{key}"] = value

            update_expression += "#updatedAt = :updatedAt"
            expression_attribute_names["#updatedAt"] = "updatedAt"
            expression_attribute_values[":updatedAt"] = datetime.utcnow().isoformat()

            self.table.update_item(
                Key={"courseId": course_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW",
            )

            updated_course = self.get_course(course_id)
            return True, updated_course

        except ClientError as error:
            return False, f"Error updating course: {str(error)}"

    def delete_course(self, course_id, instructor_id):
        try:
            course = self.get_course(course_id)
            if not course:
                return False, "Course not found"

            instructor_ids = course.get("instructorIds", [])
            if isinstance(instructor_ids, str):
                instructor_ids = [instructor_ids]
            single_instructor_id = course.get("instructorId")

            if instructor_id not in instructor_ids and single_instructor_id != instructor_id:
                return False, "Unauthorized to delete this course"

            self.table.delete_item(Key={"courseId": course_id})
            return True, None

        except ClientError as error:
            return False, f"Error deleting course: {str(error)}"

    def admin_delete_course(self, course_id):
        try:
            course = self.get_course(course_id)
            if not course:
                return False, "Course not found"

            self.table.delete_item(Key={"courseId": course_id})
            return True, None

        except ClientError as error:
            return False, f"Error deleting course: {str(error)}"

    def list_courses(self, instructor_id=None, category=None, specialization_id=None):
        try:
            if instructor_id:
                response = self.table.scan()
                items = response.get("Items", [])
                filtered_items = []
                for item in items:
                    if item.get("instructorId") == instructor_id:
                        filtered_items.append(item)
                    elif "instructorIds" in item:
                        instructor_ids = item.get("instructorIds", [])
                        if isinstance(instructor_ids, str):
                            instructor_ids = [instructor_ids]
                        if instructor_id in instructor_ids:
                            filtered_items.append(item)
                return filtered_items
            elif specialization_id:
                response = self.table.scan(
                    FilterExpression="#specializationId = :specializationId",
                    ExpressionAttributeNames={"#specializationId": "specializationId"},
                    ExpressionAttributeValues={":specializationId": specialization_id},
                )
            elif category:
                response = self.table.scan(
                    FilterExpression="category = :category", ExpressionAttributeValues={":category": category}
                )
            else:
                response = self.table.scan()

            return response.get("Items", [])
        except ClientError:
            return []
