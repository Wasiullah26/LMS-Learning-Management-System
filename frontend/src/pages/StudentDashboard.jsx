import React, { useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useGetEnrollmentsQuery, useGetCourseQuery, useGetProgressQuery } from '../services/apiSlice';
import { authService } from '../utils/auth';

const StudentDashboard = () => {
  const user = authService.getUser();
  // Force refetch on mount and include user ID to make cache user-specific
  const { data: enrollmentsData, isLoading, error } = useGetEnrollmentsQuery(
    { userId: user?.userId },
    { refetchOnMountOrArgChange: true }
  );
  const enrollments = enrollmentsData?.enrollments || [];
  const userName = user?.name || 'Student';

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
          <h3>Failed to load enrollments</h3>
          <p>Please try refreshing the page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Welcome Header */}
      <div className="dashboard-header">
        <div className="dashboard-header-content">
          <div>
            <h1 className="dashboard-title">Welcome back, {userName}!</h1>
            <p className="dashboard-subtitle">Continue your learning journey</p>
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

      {/* My Enrollments Section */}
      <div className="dashboard-section">
        <div className="dashboard-section-header">
          <h2>My Enrollments</h2>
          {enrollments.length > 0 && (
            <span className="enrollment-count">{enrollments.length} {enrollments.length === 1 ? 'course' : 'courses'}</span>
          )}
        </div>

        {enrollments.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">
              <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                <path d="M2 17L12 22L22 17"/>
                <path d="M2 12L12 17L22 12"/>
              </svg>
            </div>
            <h3>No enrollments yet</h3>
            <p>Start your learning journey by exploring our available courses</p>
            <Link to="/courses" className="btn btn-primary btn-large">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8"/>
                <path d="m21 21-4.35-4.35"/>
              </svg>
              Browse Courses
            </Link>
          </div>
        ) : (
          <div className="enrollments-grid">
            {enrollments.map((enrollment) => (
              <EnrollmentCard key={enrollment.enrollmentId} enrollment={enrollment} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const EnrollmentCard = ({ enrollment }) => {
  const user = authService.getUser();
  // Force refetch on mount to ensure fresh data
  const { data: courseData, isLoading: courseLoading } = useGetCourseQuery(
    enrollment.courseId,
    { refetchOnMountOrArgChange: true }
  );
  // Include user ID and force refetch to make progress user-specific
  const { data: progressData } = useGetProgressQuery(
    { courseId: enrollment.courseId, userId: user?.userId },
    { refetchOnMountOrArgChange: true }
  );
  
  const course = courseData?.course;
  const progressList = progressData?.progress || [];
  
  const progress = useMemo(() => {
    if (!course?.modules) return { percentage: 0 };
    const totalModules = course.modules.length;
    const completedModules = progressList.filter(p => p.status === 'completed').length;
    return {
      completed: completedModules,
      total: totalModules,
      percentage: totalModules > 0 ? Math.round((completedModules / totalModules) * 100) : 0
    };
  }, [course, progressList]);

  if (courseLoading) {
    return <div className="card">Loading course...</div>;
  }

  return (
    <div className="enrollment-card">
      <div className="enrollment-card-header">
        <div className="enrollment-card-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
            <path d="M2 17L12 22L22 17"/>
            <path d="M2 12L12 17L22 12"/>
          </svg>
        </div>
        <h3 className="enrollment-card-title">
          {course ? course.title : `Course ID: ${enrollment.courseId}`}
        </h3>
      </div>
      
      {course && (
        <p className="enrollment-card-description">
          {course.description}
        </p>
      )}

      <div className="enrollment-card-info">
        <div className="enrollment-info-item">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
            <line x1="16" y1="2" x2="16" y2="6"/>
            <line x1="8" y1="2" x2="8" y2="6"/>
            <line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          <span>Enrolled {new Date(enrollment.enrolledAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
        </div>
        {course && (
          <div className="enrollment-info-item progress-item">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
            <span>Progress: {progress.percentage}%</span>
            <div className="progress-bar">
              <div 
                className="progress-bar-fill" 
                style={{ width: `${progress.percentage}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>

      <div className="enrollment-card-footer">
        <Link
          to={`/courses/${enrollment.courseId}`}
          className="btn btn-primary btn-block"
        >
          {course ? (
            <>
              <span>Continue Learning</span>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </>
          ) : (
            'View Course'
          )}
        </Link>
      </div>
    </div>
  );
};

export default StudentDashboard;
