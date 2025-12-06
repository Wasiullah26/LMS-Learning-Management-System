# LMS Frontend

React frontend application for the Learning Management System.

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment Variables

Create a `.env` file in the frontend directory:

```
VITE_API_URL=http://localhost:5000/api
```

### 3. Run the Application

```bash
npm start
# or
npm run dev
```

The application will be available at `http://localhost:3000`

## Features

- User Authentication (Login/Register)
- Student Dashboard
- Instructor Dashboard
- Course Browsing
- Course Enrollment
- Module Viewing
- Progress Tracking
- Course Management (Instructors)

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable components
│   ├── pages/          # Page components
│   ├── services/       # API service calls
│   ├── utils/          # Utility functions
│   ├── App.jsx         # Main app component
│   └── App.css         # Styles
├── public/             # Static files
└── package.json        # Dependencies
```

## Available Scripts

- `npm start` or `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Technologies

- React 18
- React Router 6
- Axios
- Vite

