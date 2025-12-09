# Mini Learning Management System (LMS)

A full-stack Learning Management System built with React, Flask, DynamoDB, and AWS S3.

## Project Structure

```
LMS/
├── backend/          # Flask REST API
├── frontend/         # React frontend application
└── README.md        # This file
```

## Features

- User Management: Registration, login, role-based access (students/instructors)
- Course Management: CRUD operations for courses
- Module Management: CRUD operations for course modules
- Enrollment System: Students can enroll in courses
- Progress Tracking: Track student progress through modules
- File Upload: Upload course materials to AWS S3

## Tech Stack

- **Frontend**: React
- **Backend**: Flask (Python)
- **Database**: AWS DynamoDB
- **Storage**: AWS S3
- **Authentication**: JWT tokens
- **Deployment**: AWS (Academy Learner Lab)

## Getting Started

### Prerequisites

- Python 3.7+
- Node.js and npm
- AWS Academy Learner Lab account
- AWS credentials

### Backend Setup

See [backend/README.md](backend/README.md) for detailed instructions.

Quick start:
1. Install dependencies: `pip install -r backend/requirements.txt`
2. Set up AWS resources: `cd backend/setup && python aws_setup.py`
3. Configure environment variables
4. Run: `python backend/app.py`

### Frontend Setup

See [frontend/README.md](frontend/README.md) for detailed instructions.

Quick start:
1. Install dependencies: `npm install`
2. Configure API endpoint
3. Run: `npm start`

## Project Status

- ✅ Backend API (Flask + DynamoDB)
- ✅ AWS Infrastructure Setup Scripts
- ✅ Authentication System
- ✅ CRUD Operations
- ⏳ Frontend (React) - In Progress

## License

This project is for educational purposes (NCI Cloud Computing Module).



