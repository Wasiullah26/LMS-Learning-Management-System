"""
Specialization model for DynamoDB operations
"""

import boto3
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
from config import Config


class SpecializationModel:
    """Model for specialization operations in DynamoDB"""

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

        self.table = self.dynamodb.Table(Config.DYNAMODB_SPECIALIZATIONS_TABLE)

    def create_specialization(self, name, code, description=None):
        """
        Create a new specialization

        Args:
            name: Specialization name (e.g., "MSc in Data Analytics")
            code: Specialization code (e.g., "MSC-DA")
            description: Optional description

        Returns:
            Tuple (success, specialization_data or error_message)
        """
        try:
            # Check if specialization with same code already exists
            existing = self.get_specialization_by_code(code)
            if existing:
                return False, "Specialization with this code already exists"

            specialization_id = str(uuid.uuid4())
            current_time = datetime.utcnow().isoformat()

            specialization_data = {
                "specializationId": specialization_id,
                "name": name,
                "code": code,
                "description": description or "",
                "createdAt": current_time,
            }

            self.table.put_item(Item=specialization_data)
            return True, specialization_data

        except ClientError as e:
            return False, f"Error creating specialization: {str(e)}"

    def get_specialization(self, specialization_id):
        """
        Get specialization by ID

        Args:
            specialization_id: Specialization ID

        Returns:
            Specialization data dictionary or None
        """
        try:
            response = self.table.get_item(Key={"specializationId": specialization_id})
            return response.get("Item")
        except ClientError:
            return None

    def get_specialization_by_code(self, code):
        """
        Get specialization by code

        Args:
            code: Specialization code

        Returns:
            Specialization data dictionary or None
        """
        try:
            response = self.table.scan(FilterExpression="code = :code", ExpressionAttributeValues={":code": code})
            items = response.get("Items", [])
            return items[0] if items else None
        except ClientError:
            return None

    def list_specializations(self):
        """
        List all specializations

        Returns:
            List of specialization dictionaries
        """
        try:
            response = self.table.scan()
            return response.get("Items", [])
        except ClientError:
            return []

    def update_specialization(self, specialization_id, **kwargs):
        """
        Update specialization

        Args:
            specialization_id: Specialization ID
            **kwargs: Fields to update

        Returns:
            Tuple (success, error_message)
        """
        try:
            update_expression_parts = []
            expression_attribute_values = {}
            expression_attribute_names = {}

            for key, value in kwargs.items():
                if value is not None:
                    update_expression_parts.append(f"#{key} = :{key}")
                    expression_attribute_names[f"#{key}"] = key
                    expression_attribute_values[f":{key}"] = value

            if not update_expression_parts:
                return False, "No fields to update"

            update_expression_parts.append("#updatedAt = :updatedAt")
            expression_attribute_names["#updatedAt"] = "updatedAt"
            expression_attribute_values[":updatedAt"] = datetime.utcnow().isoformat()

            update_expression = "SET " + ", ".join(update_expression_parts)

            self.table.update_item(
                Key={"specializationId": specialization_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
            )
            return True, None

        except ClientError as e:
            return False, f"Error updating specialization: {str(e)}"

    def delete_specialization(self, specialization_id):
        """
        Delete specialization

        Args:
            specialization_id: Specialization ID

        Returns:
            Tuple (success, error_message)
        """
        try:
            self.table.delete_item(Key={"specializationId": specialization_id})
            return True, None
        except ClientError as e:
            return False, f"Error deleting specialization: {str(e)}"
