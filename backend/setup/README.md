# AWS Infrastructure Setup

This directory contains scripts to programmatically set up AWS resources for the LMS application.

## Prerequisites

1. AWS Academy Learner Lab credentials
2. Python 3.7+
3. boto3 library installed

## Setup Instructions

### 1. Install Dependencies

```bash
pip install boto3
```

Or if you have a requirements file:

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Set your AWS credentials as environment variables:

**Windows (PowerShell):**
```powershell
$env:AWS_ACCESS_KEY_ID="your-access-key-id"
$env:AWS_SECRET_ACCESS_KEY="your-secret-access-key"
$env:AWS_REGION="us-east-1"
$env:S3_BUCKET_NAME="lms-course-materials"  # Optional, has default
```

**Windows (Command Prompt):**
```cmd
set AWS_ACCESS_KEY_ID=your-access-key-id
set AWS_SECRET_ACCESS_KEY=your-secret-access-key
set AWS_REGION=us-east-1
set S3_BUCKET_NAME=lms-course-materials
```

**Linux/Mac:**
```bash
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_REGION="us-east-1"
export S3_BUCKET_NAME="lms-course-materials"
```

### 3. Run the Setup Script

```bash
python aws_setup.py
```

## What Gets Created

### DynamoDB Tables

1. **lms-users** - Stores user information (students and instructors)
   - Primary Key: `userId`

2. **lms-courses** - Stores course information
   - Primary Key: `courseId`

3. **lms-modules** - Stores module information within courses
   - Primary Key: `moduleId`
   - Sort Key: `courseId`

4. **lms-enrollments** - Tracks student enrollments in courses
   - Primary Key: `enrollmentId`
   - Sort Key: `studentId`

5. **lms-progress** - Tracks student progress through modules
   - Primary Key: `progressId`
   - Sort Key: `studentId`

### S3 Bucket

- **lms-course-materials** (or custom name) - Stores course materials (PDFs, videos, etc.)
  - CORS configured for web access
  - Ready for file uploads

## Notes

- The script is **idempotent** - you can run it multiple times safely
- It checks if resources exist before creating them
- All tables use **PAY_PER_REQUEST** billing mode (suitable for Academy Learner Lab)
- The S3 bucket name must be globally unique

## Troubleshooting

### Error: "Bucket already exists"
- The bucket name must be globally unique. Try a different name by setting `S3_BUCKET_NAME` environment variable.

### Error: "Access Denied"
- Check your AWS credentials
- Ensure your AWS Academy Learner Lab account has permissions to create DynamoDB tables and S3 buckets

### Error: "Region not supported"
- Make sure you're using a valid AWS region
- Academy Learner Lab typically uses `us-east-1`

