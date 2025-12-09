import React from 'react';
import { Link } from 'react-router-dom';
import { useGetCoursesQuery } from '../services/apiSlice';
import { authService } from '../utils/auth';

const CourseList = () => {
  const user = authService.getUser();
  // For instructors, filter by their instructorId
  const params = user?.role === 'instructor' ? { instructorId: user.userId } : {};
  // Force refetch on mount to ensure fresh data
  const { data, isLoading, error } = useGetCoursesQuery(
    params,
    { refetchOnMountOrArgChange: true }
  );

  const courses = data?.courses || [];

  if (isLoading) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-loading">
          <div className="spinner-large"></div>
          <p>Loading courses...</p>
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
      {/* Header */}
      <div className="dashboard-header" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
        <div className="dashboard-header-content">
          <div>
            <h1 className="dashboard-title">My Courses</h1>
            <p className="dashboard-subtitle">Explore and enroll in courses to start learning</p>
          </div>
          <div className="dashboard-header-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
              <path d="M2 17L12 22L22 17"/>
              <path d="M2 12L12 17L22 12"/>
            </svg>
          </div>
        </div>
      </div>

      {/* Courses Section */}
      <div className="dashboard-section">
        {courses.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">
              <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                <path d="M2 17L12 22L22 17"/>
                <path d="M2 12L12 17L22 12"/>
              </svg>
            </div>
            <h3>No courses available</h3>
            <p>There are no courses available at the moment. Please check back later.</p>
          </div>
        ) : (
          <>
            <div className="dashboard-section-header">
              <h2>Available Courses</h2>
              <span className="enrollment-count">{courses.length} {courses.length === 1 ? 'course' : 'courses'}</span>
            </div>
            <div className="enrollments-grid">
              {courses.map((course) => (
                <div key={course.courseId} className="enrollment-card">
                  <div className="enrollment-card-header">
                    <div className="enrollment-card-icon">
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
                  <div className="enrollment-card-footer">
                    <Link
                      to={`/courses/${course.courseId}`}
                      className="btn btn-primary btn-block"
                    >
                      <span>View Details</span>
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="9 18 15 12 9 6"/>
                      </svg>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default CourseList;

