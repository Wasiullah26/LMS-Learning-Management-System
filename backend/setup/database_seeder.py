from models.user import UserModel
from models.specialization import SpecializationModel
from models.course import CourseModel
from models.module import ModuleModel
from predefined_data import ADMIN_CONFIG, SPECIALIZATIONS_DATA, COURSES_BY_SPECIALIZATION, SAMPLE_MODULES


class DatabaseSeeder:
    # this class handles seeding the database with initial data

    def __init__(self):
        self.user_model = UserModel()
        self.specialization_model = SpecializationModel()
        self.course_model = CourseModel()
        self.module_model = ModuleModel()
        self.stats = {
            "admin_created": False,
            "specializations_created": 0,
            "instructors_created": 0,
            "courses_created": 0,
            "modules_created": 0,
            "errors": [],
        }

    def seed_all(self, silent=False):
        # seeds all the data - admin, specializations, courses, instructors, modules
        # if silent is true it wont print much stuff
        try:
            self._seed_admin(silent)
            specialization_map = self._seed_specializations(silent)
            self._fix_courses_missing_specialization(specialization_map, silent)

            if specialization_map:
                self._seed_courses_and_instructors(specialization_map, silent)

            if not silent:
                self._print_summary()

            return self.stats

        except Exception as e:
            error_msg = f"Error during seeding: {str(e)}"
            self.stats["errors"].append(error_msg)
            if not silent:
                print(f"⚠ {error_msg}")
            import traceback

            traceback.print_exc()
            return self.stats

    def _seed_admin(self, silent=False):
        # creates admin user if it doesnt exist
        if not silent:
            print("Checking admin user...")

        admin = self.user_model.get_user_by_email(ADMIN_CONFIG["email"])
        if admin:
            if not silent:
                print(f"✓ Admin user already exists: {ADMIN_CONFIG['email']}")
            return

        success, result = self.user_model.create_user(
            email=ADMIN_CONFIG["email"],
            password=ADMIN_CONFIG["password"],
            role=ADMIN_CONFIG["role"],
            name=ADMIN_CONFIG["name"],
        )

        if success:
            self.stats["admin_created"] = True
            if not silent:
                print(f"✓ Admin user created: {ADMIN_CONFIG['email']}")
        else:
            error_msg = f"Failed to create admin user: {result}"
            self.stats["errors"].append(error_msg)
            if not silent:
                print(f"⚠ {error_msg}")

    def _seed_specializations(self, silent=False):
        # creates specializations if they dont exist
        if not silent:
            print("Checking specializations...")

        specialization_map = {}

        for spec_data in SPECIALIZATIONS_DATA:
            existing = self.specialization_model.get_specialization_by_code(spec_data["code"])
            if existing:
                specialization_map[spec_data["code"]] = existing["specializationId"]
            else:
                if not silent:
                    print(f"  Creating specialization: {spec_data['name']}")

                success, result = self.specialization_model.create_specialization(
                    name=spec_data["name"], code=spec_data["code"], description=spec_data["description"]
                )

                if success:
                    specialization_map[spec_data["code"]] = result["specializationId"]
                    self.stats["specializations_created"] += 1
                    if not silent:
                        print(f"  ✓ Created specialization: {spec_data['name']}")
                else:
                    error_msg = f"Failed to create specialization {spec_data['name']}: {result}"
                    self.stats["errors"].append(error_msg)
                    if not silent:
                        print(f"  ✗ {error_msg}")

        return specialization_map

    def _fix_courses_missing_specialization(self, specialization_map, silent=False):
        # fixes courses that dont have specializationId set
        existing_courses = self.course_model.list_courses()
        courses_without_spec = [c for c in existing_courses if "specializationId" not in c]

        if not courses_without_spec:
            return

        if not silent:
            print(f"⚠ Found {len(courses_without_spec)} courses without specializationId, updating...")

        # map course titles to their specializations
        course_title_to_spec = {}
        for spec_code, courses_data in COURSES_BY_SPECIALIZATION.items():
            specialization_id = specialization_map.get(spec_code)
            if specialization_id:
                for course_data in courses_data:
                    course_title_to_spec[course_data["title"]] = specialization_id

        for course in courses_without_spec:
            course_title = course.get("title")
            if course_title in course_title_to_spec:
                specialization_id = course_title_to_spec[course_title]
                success, result = self.course_model.admin_update_course(
                    course["courseId"], specializationId=specialization_id
                )
                if success and not silent:
                    print(f"  ✓ Updated course '{course_title}' with specializationId")
                elif not success:
                    error_msg = f"Failed to update course '{course_title}': {result}"
                    self.stats["errors"].append(error_msg)

    def _seed_courses_and_instructors(self, specialization_map, silent=False):
        # creates courses, instructors, and modules for each specialization
        if not silent:
            print("Checking specializations and courses...")

        for spec_code, courses_data in COURSES_BY_SPECIALIZATION.items():
            specialization_id = specialization_map.get(spec_code)
            if not specialization_id:
                continue

            for course_data in courses_data:
                # first make sure instructor exists
                instructor = self.user_model.get_user_by_email(course_data["instructor_email"])
                if not instructor:
                    success, result = self.user_model.create_user(
                        email=course_data["instructor_email"],
                        password="Instructor123!",
                        role="instructor",
                        name=course_data["instructor_name"],
                        specialization_id=specialization_id,
                        course_ids=[],
                    )

                    if success:
                        instructor_id = result["userId"]
                        self.stats["instructors_created"] += 1
                    else:
                        error_msg = f"Failed to create instructor {course_data['instructor_name']}: {result}"
                        self.stats["errors"].append(error_msg)
                        continue
                else:
                    instructor_id = instructor["userId"]

                # check if course already exists
                all_courses = self.course_model.list_courses()
                existing_course = None
                for c in all_courses:
                    if c.get("title") == course_data["title"] and c.get("specializationId") == specialization_id:
                        existing_course = c
                        break

                if existing_course:
                    course_id = existing_course["courseId"]

                    # make sure instructor is linked to the course
                    instructor_obj = self.user_model.get_user_by_id(instructor_id)
                    if instructor_obj:
                        existing_course_ids = instructor_obj.get("courseIds", [])
                        if isinstance(existing_course_ids, str):
                            existing_course_ids = [existing_course_ids]
                        if course_id not in existing_course_ids:
                            existing_course_ids.append(course_id)
                            self.user_model.update_user(instructor_id, courseIds=existing_course_ids)
                else:
                    # create the course
                    success, course_result = self.course_model.create_course(
                        instructor_id=instructor_id,
                        title=course_data["title"],
                        description=course_data["description"],
                        category="General",
                        specialization_id=specialization_id,
                    )

                    if success:
                        course_id = course_result["courseId"]
                        self.stats["courses_created"] += 1

                        # link instructor to course
                        instructor_obj = self.user_model.get_user_by_id(instructor_id)
                        if instructor_obj:
                            existing_course_ids = instructor_obj.get("courseIds", [])
                            if isinstance(existing_course_ids, str):
                                existing_course_ids = [existing_course_ids]
                            if course_id not in existing_course_ids:
                                existing_course_ids.append(course_id)
                                self.user_model.update_user(instructor_id, courseIds=existing_course_ids)

                        # create modules for the course
                        modules_created = 0
                        for module_data in SAMPLE_MODULES:
                            self.module_model.create_module(
                                course_id=course_id,
                                title=module_data["title"],
                                description=module_data["description"],
                                order=module_data["order"],
                            )
                            modules_created += 1

                        self.stats["modules_created"] += modules_created
                    else:
                        error_msg = f"Failed to create course {course_data['title']}: {course_result}"
                        self.stats["errors"].append(error_msg)

        if not silent:
            if self.stats["courses_created"] == 0 and self.stats["instructors_created"] == 0:
                print("✓ All specializations exist with their courses")
            else:
                print(
                    f"✓ Seeding completed: {self.stats['courses_created']} courses, {self.stats['instructors_created']} instructors created"
                )

    def _print_summary(self):
        # prints what was created
        print("\n" + "=" * 60)
        print("Seeding Summary:")
        print(f"  Admin created: {'Yes' if self.stats['admin_created'] else 'Already existed'}")
        print(f"  Specializations created: {self.stats['specializations_created']}")
        print(f"  Instructors created: {self.stats['instructors_created']}")
        print(f"  Courses created: {self.stats['courses_created']}")
        print(f"  Modules created: {self.stats['modules_created']}")
        if self.stats["errors"]:
            print(f"  Errors: {len(self.stats['errors'])}")
            for error in self.stats["errors"]:
                print(f"    - {error}")
        print("=" * 60 + "\n")


def seed_database(silent=False):
    # helper function to seed database, just call this when you need to seed
    seeder = DatabaseSeeder()
    return seeder.seed_all(silent=silent)
