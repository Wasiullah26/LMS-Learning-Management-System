import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { authService } from './utils/auth';
import { toast } from './utils/toast';


import Login from './pages/Login';
import Register from './pages/Register';
import StudentDashboard from './pages/StudentDashboard';
import InstructorDashboard from './pages/InstructorDashboard';
import CourseList from './pages/CourseList';
import CourseDetail from './pages/CourseDetail';
import CourseViewer from './pages/CourseViewer';
import InstructorCourseManage from './pages/InstructorCourseManage';
import AdminDashboard from './pages/AdminDashboard';
import AdminAddStudent from './pages/AdminAddStudent';
import AdminAddInstructor from './pages/AdminAddInstructor';
import AdminManageSpecializations from './pages/AdminManageSpecializations';
import AdminManageUsers from './pages/AdminManageUsers';
import ChangePassword from './pages/ChangePassword';


import Navbar from './components/Navbar';
import ToastContainer from './components/ToastContainer';


const ProtectedRoute = ({ children, requireInstructor = false, requireAdmin = false }) => {
  if (!authService.isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && !authService.isAdmin()) {
    return <Navigate to="/dashboard" replace />;
  }

  if (requireInstructor && !authService.isInstructor()) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

function AppContent() {
  const location = useLocation();
  const [toasts, setToasts] = useState([]);
  const showNavbar = location.pathname !== '/login' && location.pathname !== '/register';

  useEffect(() => {
    const unsubscribe = toast.subscribe((newToast) => {
      setToasts((prev) => [...prev, newToast]);
    });
    return unsubscribe;
  }, []);

  const removeToast = (id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  };

  return (
    <div className="App">
      {showNavbar && <Navbar />}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
        <main className={location.pathname === '/login' || location.pathname === '/register' ? '' : 'main-content'}>
          <Routes>
            {}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  {authService.isAdmin() ? (
                    <AdminDashboard />
                  ) : authService.isInstructor() ? (
                    <InstructorDashboard />
                  ) : (
                    <StudentDashboard />
                  )}
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/dashboard"
              element={
                <ProtectedRoute requireAdmin={true}>
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/add-student"
              element={
                <ProtectedRoute requireAdmin={true}>
                  <AdminAddStudent />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/add-instructor"
              element={
                <ProtectedRoute requireAdmin={true}>
                  <AdminAddInstructor />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/specializations"
              element={
                <ProtectedRoute requireAdmin={true}>
                  <AdminManageSpecializations />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/users"
              element={
                <ProtectedRoute requireAdmin={true}>
                  <AdminManageUsers />
                </ProtectedRoute>
              }
            />
            <Route
              path="/change-password"
              element={
                <ProtectedRoute>
                  <ChangePassword />
                </ProtectedRoute>
              }
            />
            <Route
              path="/courses"
              element={
                <ProtectedRoute>
                  <CourseList />
                </ProtectedRoute>
              }
            />
            <Route
              path="/courses/:id"
              element={
                <ProtectedRoute>
                  <CourseDetail />
                </ProtectedRoute>
              }
            />
            <Route
              path="/courses/:id/learn"
              element={
                <ProtectedRoute>
                  <CourseViewer />
                </ProtectedRoute>
              }
            />
            <Route
              path="/instructor/courses"
              element={
                <ProtectedRoute requireInstructor={true}>
                  <InstructorCourseManage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/instructor/courses/new"
              element={
                <ProtectedRoute requireInstructor={true}>
                  <InstructorCourseManage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/instructor/courses/:id/edit"
              element={
                <ProtectedRoute requireInstructor={true}>
                  <InstructorCourseManage />
                </ProtectedRoute>
              }
            />

            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>
      </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;

