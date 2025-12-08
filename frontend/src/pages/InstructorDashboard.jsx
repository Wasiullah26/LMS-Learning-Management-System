import React from 'react';
import { Link } from 'react-router-dom';
import { useGetCoursesQuery } from '../services/apiSlice';
import { authService } from '../utils/auth';

const InstructorDashboard = () => {
  const user = authService.getUser();
  const userName = user?.name || 'Instructor';

  const { data, isLoading, error } = useGetCoursesQuery(
    { instructorId: user?.userId },
    { refetchOnMountOrArgChange: true }
  );

  const courses = data?.courses || [];

  if (isLoading) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-loading">
          <div className="spinner-large"></div>
          <p>Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-error">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <h3>Failed to load courses</h3>
          <p>Please try refreshing the page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {}
      <div className="dashboard-header" style={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
        <div className="dashboard-header-content">
          <div>
            <h1 className="dashboard-title">Welcome back, {userName}!</h1>
            <p className="dashboard-subtitle">Manage your courses and help students learn</p>
          </div>
          <div className="dashboard-header-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
        </div>
      </div>

      {}
      <div className="dashboard-section">
        <div className="dashboard-section-header">
          <h2>My Courses</h2>
          {courses.length > 0 && (
            <span className="enrollment-count">{courses.length} {courses.length === 1 ? 'course' : 'courses'}</span>
          )}
        </div>

        {courses.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">
              <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                <path d="M2 17L12 22L22 17"/>
                <path d="M2 12L12 17L22 12"/>
              </svg>
            </div>
            <h3>No courses assigned yet</h3>
            <p>Courses are assigned by administrators. If you believe you should have access to courses, please contact your administrator.</p>
          </div>
        ) : (
          <div className="enrollments-grid">
            {courses.map((course) => (
              <div key={course.courseId} className="enrollment-card">
                <div className="enrollment-card-header">
                  <div className="enrollment-card-icon" style={{ color: '#f5576c' }}>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                      <path d="M2 17L12 22L22 17"/>
                      <path d="M2 12L12 17L22 12"/>
                    </svg>
                  </div>
                  <h3 className="enrollment-card-title">{course.title}</h3>
                </div>

                <p className="enrollment-card-description">
                  {course.description || 'No description available.'}
                </p>

                <div className="enrollment-card-footer" style={{ display: 'flex', gap: '0.75rem' }}>
                  <Link
                    to={`/instructor/courses/${course.courseId}/edit`}
                    className="btn btn-secondary"
                    style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                  >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                    </svg>
                    <span>Manage</span>
                  </Link>
                  <Link
                    to={`/courses/${course.courseId}`}
                    className="btn btn-primary"
                    style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                  >
                    <span>View</span>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="9 18 15 12 9 6"/>
                    </svg>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default InstructorDashboard;

