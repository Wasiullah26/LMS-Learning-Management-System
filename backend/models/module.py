"""
Module model for DynamoDB operations
"""

import boto3
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
from config import Config


class ModuleModel:
    """Model for module operations in DynamoDB"""

    def __init__(self):
        """Initialize DynamoDB client and table name"""
        if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
            client_kwargs = {
                "region_name": Config.AWS_REGION,
                "aws_access_key_id": Config.AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": Config.AWS_SECRET_ACCESS_KEY,
            }
            # Add session token if provided (required for temporary credentials)
            if Config.AWS_SESSION_TOKEN:
                client_kwargs["aws_session_token"] = Config.AWS_SESSION_TOKEN
            self.dynamodb = boto3.resource("dynamodb", **client_kwargs)
        else:
            self.dynamodb = boto3.resource("dynamodb", region_name=Config.AWS_REGION)

        self.table = self.dynamodb.Table(Config.DYNAMODB_MODULES_TABLE)

    def create_module(self, course_id, title, description, order, materials=None):
        """
        Create a new module

        Args:
            course_id: Course ID this module belongs to
            title: Module title
            description: Module description
            order: Module order/sequence number
            materials: Optional list of S3 URLs for materials

        Returns:
            Tuple (success, module_data or error_message)
        """
        try:
            module_id = str(uuid.uuid4())
            current_time = datetime.utcnow().isoformat()

            module_data = {
                "moduleId": module_id,
                "courseId": course_id,
                "title": title,
                "description": description,
                "order": order,
                "materials": materials or [],
                "createdAt": current_time,
            }

            self.table.put_item(Item=module_data)
            return True, module_data

        except ClientError as e:
            return False, f"Error creating module: {str(e)}"

    def get_module(self, module_id, course_id):
        """
        Get module by ID and course ID

        Args:
            module_id: Module ID
            course_id: Course ID

        Returns:
            Module data dictionary or None
        """
        try:
            response = self.table.get_item(Key={"moduleId": module_id, "courseId": course_id})
            return response.get("Item")
        except ClientError:
            return None

    def get_modules_by_course(self, course_id):
        """
        Get all modules for a course, sorted by order

        Args:
            course_id: Course ID

        Returns:
            List of module dictionaries sorted by order
        """
        try:
            response = self.table.query(
                IndexName="courseId-index",  # Note: You may need to create a GSI
                KeyConditionExpression="courseId = :courseId",
                ExpressionAttributeValues={":courseId": course_id},
            )
            modules = response.get("Items", [])
            # Sort by order
            modules.sort(key=lambda x: x.get("order", 0))
            return modules
        except ClientError:
            # Fallback to scan if GSI doesn't exist
            try:
                response = self.table.scan(
                    FilterExpression="courseId = :courseId", ExpressionAttributeValues={":courseId": course_id}
                )
                modules = response.get("Items", [])
                modules.sort(key=lambda x: x.get("order", 0))
                return modules
            except ClientError:
                return []

    def update_module(self, module_id, course_id, **kwargs):
        """
        Update module information

        Args:
            module_id: Module ID
            course_id: Course ID
            **kwargs: Fields to update (title, description, order, materials)

        Returns:
            Tuple (success, updated_module_data or error_message)
        """
        try:
            # Build update expression
            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}

            for key, value in kwargs.items():
                update_expression += f"#{key} = :{key}, "
                expression_attribute_names[f"#{key}"] = key
                expression_attribute_values[f":{key}"] = value

            update_expression = update_expression.rstrip(", ")

            self.table.update_item(
                Key={"moduleId": module_id, "courseId": course_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW",
            )

            updated_module = self.get_module(module_id, course_id)
            return True, updated_module

        except ClientError as e:
            return False, f"Error updating module: {str(e)}"

    def delete_module(self, module_id, course_id):
        """
        Delete module

        Args:
            module_id: Module ID
            course_id: Course ID

        Returns:
            Tuple (success, error_message)
        """
        try:
            self.table.delete_item(Key={"moduleId": module_id, "courseId": course_id})
            return True, None
        except ClientError as e:
            return False, f"Error deleting module: {str(e)}"

    def add_material(self, module_id, course_id, material_url):
        """
        Add material URL to module

        Args:
            module_id: Module ID
            course_id: Course ID
            material_url: S3 URL of the material

        Returns:
            Tuple (success, updated_module_data or error_message)
        """
        try:
            module = self.get_module(module_id, course_id)
            if not module:
                return False, "Module not found"

            materials = module.get("materials", [])
            if material_url not in materials:
                materials.append(material_url)

            return self.update_module(module_id, course_id, materials=materials)
        except Exception as e:
            return False, f"Error adding material: {str(e)}"
