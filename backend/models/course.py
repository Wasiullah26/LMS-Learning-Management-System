"""
Course model for DynamoDB operations
"""

import boto3
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
from config import Config


class CourseModel:
    """Model for course operations in DynamoDB"""
    
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
        
        self.table = self.dynamodb.Table(Config.DYNAMODB_COURSES_TABLE)
    
    def create_course(self, instructor_id, title, description, category=None, specialization_id=None, instructor_ids=None):
        """
        Create a new course
        
        Args:
            instructor_id: ID of the instructor creating the course (for backward compatibility)
            title: Course title
            description: Course description
            category: Optional course category
            specialization_id: Optional specialization ID
            instructor_ids: Optional list of instructor IDs (for multiple instructors)
        
        Returns:
            Tuple (success, course_data or error_message)
        """
        try:
            course_id = str(uuid.uuid4())
            current_time = datetime.utcnow().isoformat()
            
            course_data = {
                'courseId': course_id,
                'title': title,
                'description': description,
                'category': category or 'General',
                'createdAt': current_time,
                'updatedAt': current_time
            }
            
            # Support multiple instructors - use instructorIds if provided, otherwise use instructorId
            if instructor_ids and isinstance(instructor_ids, list):
                course_data['instructorIds'] = instructor_ids
                # Also set instructorId for backward compatibility (first instructor)
                if instructor_ids:
                    course_data['instructorId'] = instructor_ids[0]
            else:
                # Single instructor (backward compatibility)
                course_data['instructorId'] = instructor_id
                course_data['instructorIds'] = [instructor_id] if instructor_id else []
            
            if specialization_id:
                course_data['specializationId'] = specialization_id
            
            self.table.put_item(Item=course_data)
            return True, course_data
        
        except ClientError as e:
            return False, f"Error creating course: {str(e)}"
    
    def get_course(self, course_id):
        """
        Get course by ID
        
        Args:
            course_id: Course ID
        
        Returns:
            Course data dictionary or None
        """
        try:
            response = self.table.get_item(Key={'courseId': course_id})
            return response.get('Item')
        except ClientError:
            return None
    
    def update_course(self, course_id, instructor_id, **kwargs):
        """
        Update course information
        
        Args:
            course_id: Course ID
            instructor_id: Instructor ID (for authorization check)
            **kwargs: Fields to update (title, description, category)
        
        Returns:
            Tuple (success, updated_course_data or error_message)
        """
        try:
            # Verify course exists and belongs to instructor
            course = self.get_course(course_id)
            if not course:
                return False, "Course not found"
            
            # Check if instructor is authorized (supports both single instructorId and multiple instructorIds)
            instructor_ids = course.get('instructorIds', [])
            if isinstance(instructor_ids, str):
                instructor_ids = [instructor_ids]
            # Also check single instructorId for backward compatibility
            single_instructor_id = course.get('instructorId')
            
            if instructor_id not in instructor_ids and single_instructor_id != instructor_id:
                return False, "Unauthorized to update this course"
            
            # Build update expression
            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}
            
            for key, value in kwargs.items():
                update_expression += f"#{key} = :{key}, "
                expression_attribute_names[f"#{key}"] = key
                expression_attribute_values[f":{key}"] = value
            
            # Add updatedAt
            update_expression += "#updatedAt = :updatedAt"
            expression_attribute_names["#updatedAt"] = "updatedAt"
            expression_attribute_values[":updatedAt"] = datetime.utcnow().isoformat()
            
            self.table.update_item(
                Key={'courseId': course_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
            
            updated_course = self.get_course(course_id)
            return True, updated_course
        
        except ClientError as e:
            return False, f"Error updating course: {str(e)}"
    
    def admin_update_course(self, course_id, **kwargs):
        """
        Update course information (admin only - no authorization check)
        
        Args:
            course_id: Course ID
            **kwargs: Fields to update (title, description, category, specializationId)
        
        Returns:
            Tuple (success, updated_course_data or error_message)
        """
        try:
            # Verify course exists
            course = self.get_course(course_id)
            if not course:
                return False, "Course not found"
            
            # Build update expression
            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}
            
            for key, value in kwargs.items():
                if value is not None:
                    update_expression += f"#{key} = :{key}, "
                    expression_attribute_names[f"#{key}"] = key
                    expression_attribute_values[f":{key}"] = value
            
            # Add updatedAt
            update_expression += "#updatedAt = :updatedAt"
            expression_attribute_names["#updatedAt"] = "updatedAt"
            expression_attribute_values[":updatedAt"] = datetime.utcnow().isoformat()
            
            self.table.update_item(
                Key={'courseId': course_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
            
            updated_course = self.get_course(course_id)
            return True, updated_course
        
        except ClientError as e:
            return False, f"Error updating course: {str(e)}"
    
    def delete_course(self, course_id, instructor_id):
        """
        Delete course (instructor only - requires authorization check)
        
        Args:
            course_id: Course ID
            instructor_id: Instructor ID (for authorization check)
        
        Returns:
            Tuple (success, error_message)
        """
        try:
            # Verify course exists and belongs to instructor
            course = self.get_course(course_id)
            if not course:
                return False, "Course not found"
            
            # Check if instructor is authorized (supports both single instructorId and multiple instructorIds)
            instructor_ids = course.get('instructorIds', [])
            if isinstance(instructor_ids, str):
                instructor_ids = [instructor_ids]
            # Also check single instructorId for backward compatibility
            single_instructor_id = course.get('instructorId')
            
            if instructor_id not in instructor_ids and single_instructor_id != instructor_id:
                return False, "Unauthorized to delete this course"
            
            self.table.delete_item(Key={'courseId': course_id})
            return True, None
        
        except ClientError as e:
            return False, f"Error deleting course: {str(e)}"
    
    def admin_delete_course(self, course_id):
        """
        Delete course (admin only - no authorization check)
        
        Args:
            course_id: Course ID
        
        Returns:
            Tuple (success, error_message)
        """
        try:
            # Verify course exists
            course = self.get_course(course_id)
            if not course:
                return False, "Course not found"
            
            self.table.delete_item(Key={'courseId': course_id})
            return True, None
        
        except ClientError as e:
            return False, f"Error deleting course: {str(e)}"
    
    def list_courses(self, instructor_id=None, category=None, specialization_id=None):
        """
        List all courses, optionally filtered by instructor, category, or specialization
        
        Args:
            instructor_id: Optional instructor ID filter (checks both instructorId and instructorIds)
            category: Optional category filter
            specialization_id: Optional specialization ID filter
        
        Returns:
            List of course dictionaries
        """
        try:
            if instructor_id:
                # Filter by instructor - check both instructorId (single) and instructorIds (array)
                # DynamoDB doesn't support checking array membership directly in FilterExpression,
                # so we'll scan all and filter in Python
                response = self.table.scan()
                items = response.get('Items', [])
                # Filter courses where instructor is in instructorIds array or matches instructorId
                filtered_items = []
                for item in items:
                    # Check single instructorId
                    if item.get('instructorId') == instructor_id:
                        filtered_items.append(item)
                    # Check instructorIds array
                    elif 'instructorIds' in item:
                        instructor_ids = item.get('instructorIds', [])
                        if isinstance(instructor_ids, str):
                            instructor_ids = [instructor_ids]
                        if instructor_id in instructor_ids:
                            filtered_items.append(item)
                return filtered_items
            elif specialization_id:
                response = self.table.scan(
                    FilterExpression='#specializationId = :specializationId',
                    ExpressionAttributeNames={'#specializationId': 'specializationId'},
                    ExpressionAttributeValues={':specializationId': specialization_id}
                )
            elif category:
                response = self.table.scan(
                    FilterExpression='category = :category',
                    ExpressionAttributeValues={':category': category}
                )
            else:
                response = self.table.scan()
            
            return response.get('Items', [])
        except ClientError:
            return []

