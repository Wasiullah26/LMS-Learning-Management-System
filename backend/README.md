# LMS Backend API

Flask-based REST API for the Learning Management System.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up AWS Resources

Before running the application, set up DynamoDB tables and S3 bucket:

```bash
cd setup
python aws_setup.py
```

Make sure you have set the following environment variables:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (default: us-east-1)
- `S3_BUCKET_NAME` (optional, has default)

### 3. Configure Environment Variables

Create a `.env` file in the backend directory (or set environment variables):

```
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
S3_BUCKET_NAME=lms-course-materials
JWT_SECRET_KEY=your-jwt-secret-key
CORS_ORIGINS=http://localhost:3000
```

### 4. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Users
- `GET /api/users` - List users (instructor only)
- `GET /api/users/<id>` - Get user by ID
- `PUT /api/users/<id>` - Update user
- `DELETE /api/users/<id>` - Delete user (instructor only)

### Courses
- `GET /api/courses` - List all courses
- `GET /api/courses/<id>` - Get course details with modules
- `POST /api/courses` - Create course (instructor only)
- `PUT /api/courses/<id>` - Update course (instructor only)
- `DELETE /api/courses/<id>` - Delete course (instructor only)

### Modules
- `GET /api/modules/courses/<courseId>/modules` - List modules in course
- `GET /api/modules/<id>?courseId=<courseId>` - Get module details
- `POST /api/modules/courses/<courseId>/modules` - Create module (instructor only)
- `PUT /api/modules/<id>` - Update module (instructor only)
- `DELETE /api/modules/<id>?courseId=<courseId>` - Delete module (instructor only)

### Enrollments
- `POST /api/enrollments` - Enroll in course (student only)
- `GET /api/enrollments` - Get enrollments
- `DELETE /api/enrollments/<id>` - Unenroll from course (student only)

### Progress
- `POST /api/progress` - Update progress (student only)
- `GET /api/progress` - Get progress
- `POST /api/progress/complete` - Mark module as completed (student only)
- `GET /api/progress/stats?courseId=<courseId>` - Get completion statistics

### File Upload
- `POST /api/upload` - Upload file to S3 (instructor only)

## Authentication

Most endpoints require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your-token>
```

## Testing

You can test the API using tools like:
- Postman
- cURL
- HTTPie
- Your React frontend

Example cURL request:

```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234","role":"student","name":"Test User"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234"}'
```

