import boto3
import bcrypt
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
from config import Config


class UserModel:

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

        self.table = self.dynamodb.Table(Config.DYNAMODB_USERS_TABLE)

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, password, hashed):
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    def create_user(self, email, password, role, name, specialization_id=None, course_ids=None):
        try:
            existing_user = self.get_user_by_email(email)
            if existing_user:
                return False, "User with this email already exists"

            if role == "student" and not specialization_id:
                return False, "Specialization ID is required for students"
            if role == "instructor" and not specialization_id:
                return False, "Specialization ID is required for instructors"

            user_id = str(uuid.uuid4())
            hashed_password = self.hash_password(password)
            current_time = datetime.utcnow().isoformat()

            user_data = {
                "userId": user_id,
                "email": email,
                "password": hashed_password,
                "role": role,
                "name": name,
                "createdAt": current_time,
                "passwordChanged": False,
            }

            if role == "student" and specialization_id:
                user_data["specializationId"] = specialization_id
            elif role == "instructor" and specialization_id:
                user_data["specializationId"] = specialization_id
                if course_ids:
                    user_data["courseIds"] = course_ids if isinstance(course_ids, list) else [course_ids]
                else:
                    user_data["courseIds"] = []

            self.table.put_item(Item=user_data)

            user_data.pop("password")
            return True, user_data

        except ClientError as error:
            return False, f"Error creating user: {str(error)}"

    def get_user_by_id(self, user_id):
        try:
            response = self.table.get_item(Key={"userId": user_id})
            return response.get("Item")
        except ClientError:
            return None

    def get_user_by_email(self, email):
        try:
            response = self.table.scan(FilterExpression="email = :email", ExpressionAttributeValues={":email": email})
            items = response.get("Items", [])
            return items[0] if items else None
        except ClientError:
            return None

    def authenticate_user(self, email, password):
        user = self.get_user_by_email(email)
        if not user:
            return False, "Invalid email or password"

        if not self.verify_password(password, user["password"]):
            return False, "Invalid email or password"

        user.pop("password")
        return True, user

    def update_user(self, user_id, **kwargs):
        try:
            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}

            for key, value in kwargs.items():
                if key == "password":
                    value = self.hash_password(value)
                update_expression += f"#{key} = :{key}, "
                expression_attribute_names[f"#{key}"] = key
                expression_attribute_values[f":{key}"] = value

            update_expression += "#updatedAt = :updatedAt"
            expression_attribute_names["#updatedAt"] = "updatedAt"
            expression_attribute_values[":updatedAt"] = datetime.utcnow().isoformat()

            self.table.update_item(
                Key={"userId": user_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW",
            )

            updated_user = self.get_user_by_id(user_id)
            if updated_user and "password" in updated_user:
                updated_user.pop("password")

            return True, updated_user

        except ClientError as error:
            return False, f"Error updating user: {str(error)}"

    def delete_user(self, user_id):
        try:
            self.table.delete_item(Key={"userId": user_id})
            return True, None
        except ClientError as error:
            return False, f"Error deleting user: {str(error)}"

    def list_users(self, role=None):
        try:
            if role:
                response = self.table.scan(
                    FilterExpression="#r = :role",
                    ExpressionAttributeNames={"#r": "role"},
                    ExpressionAttributeValues={":role": role},
                )
            else:
                response = self.table.scan()

            users = response.get("Items", [])

            while "LastEvaluatedKey" in response:
                if role:
                    response = self.table.scan(
                        FilterExpression="#r = :role",
                        ExpressionAttributeNames={"#r": "role"},
                        ExpressionAttributeValues={":role": role},
                        ExclusiveStartKey=response["LastEvaluatedKey"],
                    )
                else:
                    response = self.table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
                users.extend(response.get("Items", []))

            for user in users:
                user.pop("password", None)

            return users
        except ClientError:
            return []

    def change_password(self, user_id, old_password, new_password):
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "User not found"

            if not self.verify_password(old_password, user["password"]):
                return False, "Current password is incorrect"

            hashed_password = self.hash_password(new_password)
            self.table.update_item(
                Key={"userId": user_id},
                UpdateExpression="SET #password = :password, #passwordChanged = :passwordChanged, #updatedAt = :updatedAt",
                ExpressionAttributeNames={
                    "#password": "password",
                    "#passwordChanged": "passwordChanged",
                    "#updatedAt": "updatedAt",
                },
                ExpressionAttributeValues={
                    ":password": hashed_password,
                    ":passwordChanged": True,
                    ":updatedAt": datetime.utcnow().isoformat(),
                },
            )

            return True, None

        except ClientError as error:
            return False, f"Error changing password: {str(error)}"

    def admin_change_password(self, user_id, new_password):
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "User not found"

            hashed_password = self.hash_password(new_password)
            self.table.update_item(
                Key={"userId": user_id},
                UpdateExpression="SET #password = :password, #updatedAt = :updatedAt",
                ExpressionAttributeNames={"#password": "password", "#updatedAt": "updatedAt"},
                ExpressionAttributeValues={":password": hashed_password, ":updatedAt": datetime.utcnow().isoformat()},
            )

            return True, None

        except ClientError as error:
            return False, f"Error changing password: {str(error)}"
