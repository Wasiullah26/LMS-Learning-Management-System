import boto3
import bcrypt
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
from config import Config


class UserModel:
    # handles all user stuff in dynamodb

    def __init__(self):
        # setup dynamodb connection
        if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
            client_kwargs = {
                'region_name': Config.AWS_REGION,
                'aws_access_key_id': Config.AWS_ACCESS_KEY_ID,
                'aws_secret_access_key': Config.AWS_SECRET_ACCESS_KEY
            }
            # add session token if we have it (needed for learner lab)
            if Config.AWS_SESSION_TOKEN:
                client_kwargs['aws_session_token'] = Config.AWS_SESSION_TOKEN
            self.dynamodb = boto3.resource('dynamodb', **client_kwargs)
        else:
            self.dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)

        self.table = self.dynamodb.Table(Config.DYNAMODB_USERS_TABLE)

    def hash_password(self, password):
        # hash password with bcrypt
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password, hashed):
        # check if password matches the hash
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def create_user(self, email, password, role, name, specialization_id=None, course_ids=None):
        # creates a new user in the database
        try:
            # check if user already exists
            existing_user = self.get_user_by_email(email)
            if existing_user:
                return False, "User with this email already exists"

            # validate role stuff
            if role == 'student' and not specialization_id:
                return False, "Specialization ID is required for students"
            if role == 'instructor' and not specialization_id:
                return False, "Specialization ID is required for instructors"
            # course_ids can be empty for instructors when creating them, we can add courses later

            # create the user
            user_id = str(uuid.uuid4())
            hashed_password = self.hash_password(password)
            current_time = datetime.utcnow().isoformat()

            user_data = {
                'userId': user_id,
                'email': email,
                'password': hashed_password,
                'role': role,
                'name': name,
                'createdAt': current_time,
                'passwordChanged': False  # track if they changed their password
            }

            # add specialization and courses for students/instructors
            if role == 'student' and specialization_id:
                user_data['specializationId'] = specialization_id
            elif role == 'instructor' and specialization_id:
                user_data['specializationId'] = specialization_id
                # only add courseIds if provided
                if course_ids:
                    user_data['courseIds'] = course_ids if isinstance(course_ids, list) else [course_ids]
                else:
                    user_data['courseIds'] = []  # empty list, will add courses later

            self.table.put_item(Item=user_data)

            # dont return password in response
            user_data.pop('password')
            return True, user_data

        except ClientError as error:
            return False, f"Error creating user: {str(error)}"

    def get_user_by_id(self, user_id):
        # get user by their id
        try:
            response = self.table.get_item(Key={'userId': user_id})
            return response.get('Item')
        except ClientError:
            return None

    def get_user_by_email(self, email):
        # get user by email, uses scan so might be slow if we have lots of users
        try:
            response = self.table.scan(
                FilterExpression='email = :email',
                ExpressionAttributeValues={':email': email}
            )
            items = response.get('Items', [])
            return items[0] if items else None
        except ClientError:
            return None

    def authenticate_user(self, email, password):
        # check if email and password are correct
        user = self.get_user_by_email(email)
        if not user:
            return False, "Invalid email or password"

        if not self.verify_password(password, user['password']):
            return False, "Invalid email or password"

        # remove password from response
        user.pop('password')
        return True, user

    def update_user(self, user_id, **kwargs):
        # update user info, can update name, email, courseIds, etc
        try:
            # build the update expression for dynamodb
            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}

            for key, value in kwargs.items():
                if key == 'password':
                    value = self.hash_password(value)
                update_expression += f"#{key} = :{key}, "
                expression_attribute_names[f"#{key}"] = key
                expression_attribute_values[f":{key}"] = value

            # add updatedAt timestamp
            update_expression += "#updatedAt = :updatedAt"
            expression_attribute_names["#updatedAt"] = "updatedAt"
            expression_attribute_values[":updatedAt"] = datetime.utcnow().isoformat()

            self.table.update_item(
                Key={'userId': user_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )

            # get the updated user
            updated_user = self.get_user_by_id(user_id)
            if updated_user and 'password' in updated_user:
                updated_user.pop('password')

            return True, updated_user

        except ClientError as error:
            return False, f"Error updating user: {str(error)}"

    def delete_user(self, user_id):
        # delete a user
        try:
            self.table.delete_item(Key={'userId': user_id})
            return True, None
        except ClientError as error:
            return False, f"Error deleting user: {str(error)}"

    def list_users(self, role=None):
        # get all users, can filter by role if needed
        try:
            if role:
                # filter by role
                response = self.table.scan(
                    FilterExpression='#r = :role',
                    ExpressionAttributeNames={'#r': 'role'},
                    ExpressionAttributeValues={':role': role}
                )
            else:
                response = self.table.scan()

            users = response.get('Items', [])

            # handle pagination if we have lots of users
            while 'LastEvaluatedKey' in response:
                if role:
                    response = self.table.scan(
                        FilterExpression='#r = :role',
                        ExpressionAttributeNames={'#r': 'role'},
                        ExpressionAttributeValues={':role': role},
                        ExclusiveStartKey=response['LastEvaluatedKey']
                    )
                else:
                    response = self.table.scan(
                        ExclusiveStartKey=response['LastEvaluatedKey']
                    )
                users.extend(response.get('Items', []))

            # remove passwords from response
            for user in users:
                user.pop('password', None)

            return users
        except ClientError as error:
            return []

    def change_password(self, user_id, old_password, new_password):
        # user changes their own password
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "User not found"

            # check old password is correct
            if not self.verify_password(old_password, user['password']):
                return False, "Current password is incorrect"

            # update password
            hashed_password = self.hash_password(new_password)
            self.table.update_item(
                Key={'userId': user_id},
                UpdateExpression='SET #password = :password, #passwordChanged = :passwordChanged, #updatedAt = :updatedAt',
                ExpressionAttributeNames={
                    '#password': 'password',
                    '#passwordChanged': 'passwordChanged',
                    '#updatedAt': 'updatedAt'
                },
                ExpressionAttributeValues={
                    ':password': hashed_password,
                    ':passwordChanged': True,
                    ':updatedAt': datetime.utcnow().isoformat()
                }
            )

            return True, None

        except ClientError as error:
            return False, f"Error changing password: {str(error)}"

    def admin_change_password(self, user_id, new_password):
        # admin can change any users password without knowing old password
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "User not found"

            # just update the password
            hashed_password = self.hash_password(new_password)
            self.table.update_item(
                Key={'userId': user_id},
                UpdateExpression='SET #password = :password, #updatedAt = :updatedAt',
                ExpressionAttributeNames={
                    '#password': 'password',
                    '#updatedAt': 'updatedAt'
                },
                ExpressionAttributeValues={
                    ':password': hashed_password,
                    ':updatedAt': datetime.utcnow().isoformat()
                }
            )

            return True, None

        except ClientError as error:
            return False, f"Error changing password: {str(error)}"
