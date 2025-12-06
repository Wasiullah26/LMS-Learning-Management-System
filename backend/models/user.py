"""
User model for DynamoDB operations
"""

import boto3
import bcrypt
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
from config import Config


class UserModel:
    """Model for user operations in DynamoDB"""
    
    def __init__(self):
        """Initialize DynamoDB client and table name"""
        if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
            client_kwargs = {
                'region_name': Config.AWS_REGION,
                'aws_access_key_id': Config.AWS_ACCESS_KEY_ID,
                'aws_secret_access_key': Config.AWS_SECRET_ACCESS_KEY
            }
            # Add session token if provided (required for temporary credentials)
            if Config.AWS_SESSION_TOKEN:
                client_kwargs['aws_session_token'] = Config.AWS_SESSION_TOKEN
            self.dynamodb = boto3.resource('dynamodb', **client_kwargs)
        else:
            self.dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
        
        self.table = self.dynamodb.Table(Config.DYNAMODB_USERS_TABLE)
    
    def hash_password(self, password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password, hashed):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_user(self, email, password, role, name, specialization_id=None, course_ids=None):
        """
        Create a new user
        
        Args:
            email: User email
            password: Plain text password
            role: User role (student/instructor/admin)
            name: User name
            specialization_id: Optional specialization ID (for students/instructors)
            course_ids: Optional list of course IDs (for instructors)
        
        Returns:
            Tuple (success, user_data or error_message)
        """
        try:
            # Check if user already exists
            existing_user = self.get_user_by_email(email)
            if existing_user:
                return False, "User with this email already exists"
            
            # Validate role-specific requirements
            if role == 'student' and not specialization_id:
                return False, "Specialization ID is required for students"
            if role == 'instructor' and not specialization_id:
                return False, "Specialization ID is required for instructors"
            # Note: course_ids can be empty for instructors during initial creation (e.g., seeding)
            # Courses can be assigned later via update_user
            
            # Create user
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
                'passwordChanged': False  # Track if user has changed password
            }
            
            # Add specialization and courses for students/instructors
            if role == 'student' and specialization_id:
                user_data['specializationId'] = specialization_id
            elif role == 'instructor' and specialization_id:
                user_data['specializationId'] = specialization_id
                # Only add courseIds if provided (can be empty list for initial creation)
                if course_ids:
                    user_data['courseIds'] = course_ids if isinstance(course_ids, list) else [course_ids]
                else:
                    user_data['courseIds'] = []  # Empty list, will be populated later
            
            self.table.put_item(Item=user_data)
            
            # Remove password from response
            user_data.pop('password')
            return True, user_data
        
        except ClientError as e:
            return False, f"Error creating user: {str(e)}"
    
    def get_user_by_id(self, user_id):
        """
        Get user by user ID
        
        Args:
            user_id: User ID
        
        Returns:
            User data dictionary or None
        """
        try:
            response = self.table.get_item(Key={'userId': user_id})
            return response.get('Item')
        except ClientError:
            return None
    
    def get_user_by_email(self, email):
        """
        Get user by email (requires scan - consider adding GSI in production)
        
        Args:
            email: User email
        
        Returns:
            User data dictionary or None
        """
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
        """
        Authenticate user with email and password
        
        Args:
            email: User email
            password: Plain text password
        
        Returns:
            Tuple (success, user_data or error_message)
        """
        user = self.get_user_by_email(email)
        if not user:
            return False, "Invalid email or password"
        
        if not self.verify_password(password, user['password']):
            return False, "Invalid email or password"
        
        # Remove password from response
        user.pop('password')
        return True, user
    
    def update_user(self, user_id, **kwargs):
        """
        Update user information
        
        Args:
            user_id: User ID
            **kwargs: Fields to update (name, email, etc.)
        
        Returns:
            Tuple (success, updated_user_data or error_message)
        """
        try:
            # Build update expression
            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}
            
            for key, value in kwargs.items():
                if key == 'password':
                    value = self.hash_password(value)
                update_expression += f"#{key} = :{key}, "
                expression_attribute_names[f"#{key}"] = key
                expression_attribute_values[f":{key}"] = value
            
            # Add updatedAt
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
            
            # Get updated user
            updated_user = self.get_user_by_id(user_id)
            if updated_user and 'password' in updated_user:
                updated_user.pop('password')
            
            return True, updated_user
        
        except ClientError as e:
            return False, f"Error updating user: {str(e)}"
    
    def delete_user(self, user_id):
        """
        Delete user
        
        Args:
            user_id: User ID
        
        Returns:
            Tuple (success, error_message)
        """
        try:
            self.table.delete_item(Key={'userId': user_id})
            return True, None
        except ClientError as e:
            return False, f"Error deleting user: {str(e)}"
    
    def list_users(self, role=None):
        """
        List all users, optionally filtered by role
        
        Args:
            role: Optional role filter
        
        Returns:
            List of user dictionaries
        """
        try:
            if role:
                # Use scan with FilterExpression for role filtering
                # Note: 'role' is not a reserved word, but using ExpressionAttributeNames is good practice
                response = self.table.scan(
                    FilterExpression='#r = :role',
                    ExpressionAttributeNames={'#r': 'role'},
                    ExpressionAttributeValues={':role': role}
                )
            else:
                response = self.table.scan()
            
            users = response.get('Items', [])
            
            # Handle pagination if needed (DynamoDB scan returns max 1MB)
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
            
            # Remove passwords from response
            for user in users:
                user.pop('password', None)
            
            return users
        except ClientError as e:
            return []
    
    def change_password(self, user_id, old_password, new_password):
        """
        Change user password
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
        
        Returns:
            Tuple (success, error_message)
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "User not found"
            
            # Verify old password
            if not self.verify_password(old_password, user['password']):
                return False, "Current password is incorrect"
            
            # Update password
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
        
        except ClientError as e:
            return False, f"Error changing password: {str(e)}"
    
    def admin_change_password(self, user_id, new_password):
        """
        Admin changes user password (without old password verification)
        
        Args:
            user_id: User ID
            new_password: New password
        
        Returns:
            Tuple (success, error_message)
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "User not found"
            
            # Update password
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
        
        except ClientError as e:
            return False, f"Error changing password: {str(e)}"

