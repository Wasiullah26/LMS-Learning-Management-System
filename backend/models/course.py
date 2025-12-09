import boto3
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
from config import Config


class CourseModel:
    # handles all course stuff in dynamodb

    def __init__(self):
        # setup dynamodb connection
        if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
            client_kwargs = {
                "region_name": Config.AWS_REGION,
                "aws_access_key_id": Config.AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": Config.AWS_SECRET_ACCESS_KEY,
            }
            # add session token if we have it
            if Config.AWS_SESSION_TOKEN:
                client_kwargs["aws_session_token"] = Config.AWS_SESSION_TOKEN
            self.dynamodb = boto3.resource("dynamodb", **client_kwargs)
        else:
            self.dynamodb = boto3.resource("dynamodb", region_name=Config.AWS_REGION)

        self.table = self.dynamodb.Table(Config.DYNAMODB_COURSES_TABLE)

    def create_course(
        self, instructor_id, title, description, category=None, specialization_id=None, instructor_ids=None
    ):
        # create a new course
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

            # support multiple instructors
            if instructor_ids and isinstance(instructor_ids, list):
                course_data["instructorIds"] = instructor_ids
                # also set instructorId for backwards compatibility
                if instructor_ids:
                    course_data["instructorId"] = instructor_ids[0]
            else:
                # single instructor
                course_data["instructorId"] = instructor_id
                course_data["instructorIds"] = [instructor_id] if instructor_id else []

            if specialization_id:
                course_data["specializationId"] = specialization_id

            self.table.put_item(Item=course_data)
            return True, course_data

        except ClientError as error:
            return False, f"Error creating course: {str(error)}"

    def get_course(self, course_id):
        # get course by id
        try:
            response = self.table.get_item(Key={"courseId": course_id})
            return response.get("Item")
        except ClientError:
            return None

    def update_course(self, course_id, instructor_id, **kwargs):
        # update course info, only if instructor owns it
        try:
            # check if course exists and instructor owns it
            course = self.get_course(course_id)
            if not course:
                return False, "Course not found"

            # check if instructor is authorized
            instructor_ids = course.get("instructorIds", [])
            if isinstance(instructor_ids, str):
                instructor_ids = [instructor_ids]
            # also check single instructorId
            single_instructor_id = course.get("instructorId")

            if instructor_id not in instructor_ids and single_instructor_id != instructor_id:
                return False, "Unauthorized to update this course"

            # build update expression
            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}

            for key, value in kwargs.items():
                update_expression += f"#{key} = :{key}, "
                expression_attribute_names[f"#{key}"] = key
                expression_attribute_values[f":{key}"] = value

            # add updatedAt
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
        # admin can update any course without checking ownership
        try:
            # check if course exists
            course = self.get_course(course_id)
            if not course:
                return False, "Course not found"

            # build update expression
            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}

            for key, value in kwargs.items():
                if value is not None:
                    update_expression += f"#{key} = :{key}, "
                    expression_attribute_names[f"#{key}"] = key
                    expression_attribute_values[f":{key}"] = value

            # add updatedAt
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
        # delete course, only if instructor owns it
        try:
            # check if course exists and instructor owns it
            course = self.get_course(course_id)
            if not course:
                return False, "Course not found"

            # check if instructor is authorized
            instructor_ids = course.get("instructorIds", [])
            if isinstance(instructor_ids, str):
                instructor_ids = [instructor_ids]
            # also check single instructorId
            single_instructor_id = course.get("instructorId")

            if instructor_id not in instructor_ids and single_instructor_id != instructor_id:
                return False, "Unauthorized to delete this course"

            self.table.delete_item(Key={"courseId": course_id})
            return True, None

        except ClientError as error:
            return False, f"Error deleting course: {str(error)}"

    def admin_delete_course(self, course_id):
        # admin can delete any course
        try:
            # check if course exists
            course = self.get_course(course_id)
            if not course:
                return False, "Course not found"

            self.table.delete_item(Key={"courseId": course_id})
            return True, None

        except ClientError as error:
            return False, f"Error deleting course: {str(error)}"

    def list_courses(self, instructor_id=None, category=None, specialization_id=None):
        # get all courses, can filter by instructor, category, or specialization
        try:
            if instructor_id:
                # filter by instructor, need to check both instructorId and instructorIds
                # dynamodb cant check array membership in filter, so scan all and filter in python
                response = self.table.scan()
                items = response.get("Items", [])
                # filter courses where instructor matches
                filtered_items = []
                for item in items:
                    # check single instructorId
                    if item.get("instructorId") == instructor_id:
                        filtered_items.append(item)
                    # check instructorIds array
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
