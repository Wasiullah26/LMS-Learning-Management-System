"""
Seed script to populate database with admin user, specializations, courses, and instructors
Run this script to add initial data to the LMS
"""

import sys
import os

# Add parent directory to path to import models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user import UserModel
from models.specialization import SpecializationModel
from models.course import CourseModel
from models.module import ModuleModel
from config import Config
from predefined_data import (
    ADMIN_CONFIG,
    SPECIALIZATIONS_DATA,
    COURSES_BY_SPECIALIZATION,
    SAMPLE_MODULES
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_admin_user(user_model):
    """Create admin user if it doesn't exist"""
    print("\n=== Creating Admin User ===")
    
    # Check if admin already exists
    admin = user_model.get_user_by_email(ADMIN_CONFIG['email'])
    if admin:
        print(f"✓ Admin user already exists: {ADMIN_CONFIG['email']}")
        return admin['userId']
    
    # Create admin user
    success, result = user_model.create_user(
        email=ADMIN_CONFIG['email'],
        password=ADMIN_CONFIG['password'],
        role=ADMIN_CONFIG['role'],
        name=ADMIN_CONFIG['name']
    )
    
    if success:
        print(f"✓ Admin user created: {ADMIN_CONFIG['email']}")
        return result['userId']
    else:
        print(f"✗ Failed to create admin user: {result}")
        return None


def seed_specializations(specialization_model):
    """Seed specializations"""
    print("\n=== Seeding Specializations ===")
    specialization_map = {}
    
    for spec_data in SPECIALIZATIONS_DATA:
        # Check if specialization already exists
        existing = specialization_model.get_specialization_by_code(spec_data['code'])
        if existing:
            print(f"✓ Specialization already exists: {spec_data['name']}")
            specialization_map[spec_data['code']] = existing['specializationId']
            continue
        
        success, result = specialization_model.create_specialization(
            name=spec_data['name'],
            code=spec_data['code'],
            description=spec_data['description']
        )
        
        if success:
            print(f"✓ Created specialization: {spec_data['name']}")
            specialization_map[spec_data['code']] = result['specializationId']
        else:
            print(f"✗ Failed to create specialization {spec_data['name']}: {result}")
    
    return specialization_map


def get_or_create_instructor(user_model, name, email, specialization_id, course_ids, default_password='Instructor123!'):
    """Get existing instructor or create a new one"""
    existing = user_model.get_user_by_email(email)
    if existing:
        # Update existing instructor with new course if not already in courseIds
        if 'courseIds' in existing:
            existing_course_ids = existing.get('courseIds', [])
            if isinstance(existing_course_ids, str):
                existing_course_ids = [existing_course_ids]
            # Add new courses if not already present
            updated_course_ids = list(set(existing_course_ids + (course_ids if isinstance(course_ids, list) else [course_ids])))
            user_model.update_user(existing['userId'], courseIds=updated_course_ids)
        else:
            # Migrate from old courseId to courseIds
            old_course_id = existing.get('courseId')
            if old_course_id:
                updated_course_ids = [old_course_id] + (course_ids if isinstance(course_ids, list) else [course_ids])
                user_model.update_user(existing['userId'], courseIds=updated_course_ids)
        return existing['userId']
    
    success, result = user_model.create_user(
        email=email,
        password=default_password,
        role='instructor',
        name=name,
        specialization_id=specialization_id,
        course_ids=course_ids if isinstance(course_ids, list) else [course_ids]
    )
    
    if success:
        return result['userId']
    return None


def seed_courses_and_instructors(user_model, course_model, module_model, specialization_map):
    """Seed courses, instructors, and modules"""
    print("\n=== Seeding Courses and Instructors ===")
    
    for spec_code, courses_data in COURSES_BY_SPECIALIZATION.items():
        specialization_id = specialization_map.get(spec_code)
        if not specialization_id:
            print(f"✗ Specialization {spec_code} not found, skipping courses")
            continue
        
        print(f"\n--- Specialization: {spec_code} ---")
        
        for course_data in courses_data:
            # Check if course already exists
            all_courses = course_model.list_courses()
            existing_course = None
            for c in all_courses:
                if c.get('title') == course_data['title'] and c.get('specializationId') == specialization_id:
                    existing_course = c
                    break
            
            # Create or get instructor first (with empty course list initially)
            instructor_id = get_or_create_instructor(
                user_model,
                course_data['instructor_name'],
                course_data['instructor_email'],
                specialization_id,
                [],  # Start with empty course list
                default_password='Instructor123!'
            )
            
            if not instructor_id:
                print(f"✗ Failed to create instructor: {course_data['instructor_name']}")
                continue
            
            # Check if course already exists
            if existing_course:
                print(f"✓ Course already exists: {course_data['title']}")
                course_id = existing_course['courseId']
            else:
                # Create course with instructor
                success, course_result = course_model.create_course(
                    instructor_id=instructor_id,
                    title=course_data['title'],
                    description=course_data['description'],
                    category='General',
                    specialization_id=specialization_id
                )
                
                if not success:
                    print(f"✗ Failed to create course: {course_data['title']}")
                    continue
                
                course_id = course_result['courseId']
                print(f"✓ Created course: {course_data['title']}")
            
            # Update instructor with this course in their courseIds list
            instructor = user_model.get_user_by_id(instructor_id)
            if instructor:
                existing_course_ids = instructor.get('courseIds', [])
                if isinstance(existing_course_ids, str):
                    existing_course_ids = [existing_course_ids]
                if course_id not in existing_course_ids:
                    existing_course_ids.append(course_id)
                    user_model.update_user(instructor_id, courseIds=existing_course_ids)
            
            # Create modules for the course
            existing_modules = module_model.get_modules_by_course(course_id)
            if len(existing_modules) == 0:
                for module_data in SAMPLE_MODULES:
                    module_model.create_module(
                        course_id=course_id,
                        title=module_data['title'],
                        description=module_data['description'],
                        order=module_data['order']
                    )
                print(f"  ✓ Created {len(SAMPLE_MODULES)} modules for {course_data['title']}")


def main():
    """Main function to seed all data"""
    print("=" * 60)
    print("LMS Database Seeding Script")
    print("=" * 60)
    
    user_model = UserModel()
    specialization_model = SpecializationModel()
    course_model = CourseModel()
    module_model = ModuleModel()
    
    # Create admin user
    admin_id = create_admin_user(user_model)
    
    # Seed specializations
    specialization_map = seed_specializations(specialization_model)
    
    # Seed courses and instructors
    seed_courses_and_instructors(user_model, course_model, module_model, specialization_map)
    
    print("\n" + "=" * 60)
    print("Seeding completed!")
    print("=" * 60)
    print(f"\nAdmin credentials:")
    print(f"  Email: {ADMIN_CONFIG['email']}")
    print(f"  Password: {ADMIN_CONFIG['password']}")
    print(f"\nTotal specializations: {len(specialization_map)}")
    total_courses = sum(len(courses) for courses in COURSES_BY_SPECIALIZATION.values())
    print(f"Total courses: {total_courses}")


if __name__ == '__main__':
    main()
