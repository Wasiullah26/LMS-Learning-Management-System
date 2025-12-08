import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useGetCourseQuery, useGetEnrollmentsQuery, useCreateEnrollmentMutation } from '../services/apiSlice';
import { authService } from '../utils/auth';
import { toast } from '../utils/toast';

const CourseDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const user = authService.getUser();

  const { data: courseData, isLoading, error } = useGetCourseQuery(
    id,
    { refetchOnMountOrArgChange: true }
  );

  const { data: enrollmentsData } = useGetEnrollmentsQuery(
    { userId: user?.userId },
    {
      skip: !authService.isStudent(),
      refetchOnMountOrArgChange: true
    }
  );
  const [createEnrollment, { isLoading: enrolling }] = useCreateEnrollmentMutation();

  const course = courseData?.course;
  const enrollments = enrollmentsData?.enrollments || [];
  const enrolled = enrollments.some(e => e.courseId === id);

  const handleEnroll = async () => {
    if (!authService.isStudent()) {
      navigate('/login');
      return;
    }

    try {
      await createEnrollment({ courseId: id }).unwrap();
      toast.success('Successfully enrolled in course!');
    } catch (err) {
      toast.error(err.data?.error || 'Failed to enroll');
    }
  };

  if (isLoading) {
    return (
      <div className="course-detail-wrapper">
        <div className="course-detail-loading">
          <div className="spinner-large"></div>
          <p>Loading course details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="course-detail-wrapper">
        <div className="course-detail-error">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <h3>Failed to load course</h3>
          <p>Please try refreshing the page.</p>
          <button onClick={() => window.location.reload()} className="btn btn-primary" style={{ marginTop: '1rem' }}>
            Refresh Page
          </button>
        </div>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="course-detail-wrapper">
        <div className="course-detail-error">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <h3>Course not found</h3>
          <p>The course you&apos;re looking for doesn&apos;t exist.</p>
          <button onClick={() => navigate('/courses')} className="btn btn-primary" style={{ marginTop: '1rem' }}>
            Browse Courses
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="course-detail-wrapper">
      {}
      <div className="course-detail-hero">
        <button onClick={() => navigate(-1)} className="course-detail-back-btn">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
          <span>Back</span>
        </button>
        <div className="course-detail-hero-content">
          {course.category && (
            <span className="course-detail-category">{course.category}</span>
          )}
          <h1 className="course-detail-title">{course.title}</h1>
          <div className="course-detail-meta">
            <div className="course-detail-meta-item">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                <path d="M2 17L12 22L22 17"/>
                <path d="M2 12L12 17L22 12"/>
              </svg>
              <span>{course.modules?.length || 0} Modules</span>
            </div>
          </div>
        </div>
      </div>

      {}
      <div className="course-detail-container">
        <div className="course-detail-layout">
          {}
          <div className="course-detail-content">
            {}
            <div className="course-detail-card">
              <div className="course-detail-card-header">
                <div className="course-detail-card-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                  </svg>
                </div>
                <h2>About This Course</h2>
              </div>
              <div className="course-detail-card-body">
                <p className="course-detail-description">
                  {course.description || 'No description available for this course.'}
                </p>
              </div>
            </div>

            {}
            <div className="course-detail-card" style={{ marginTop: '2rem' }}>
              <div className="course-detail-card-header">
                <div className="course-detail-card-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                    <path d="M2 17L12 22L22 17"/>
                    <path d="M2 12L12 17L22 12"/>
                  </svg>
                </div>
                <h2>Course Modules</h2>
                <span className="course-detail-module-count">{course.modules?.length || 0}</span>
              </div>
              <div className="course-detail-card-body">
                {course.modules && course.modules.length > 0 ? (
                  <div className="course-detail-modules">
                    {course.modules.map((module, index) => (
                      <div key={module.moduleId} className="course-detail-module">
                        <div className="course-detail-module-number">
                          <span>{index + 1}</span>
                        </div>
                        <div className="course-detail-module-content">
                          <h3>{module.title}</h3>
                          {module.description && (
                            <p>{module.description}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="course-detail-empty">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                      <path d="M2 17L12 22L22 17"/>
                      <path d="M2 12L12 17L22 12"/>
                    </svg>
                    <p>No modules available yet.</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {}
          {authService.isStudent() && (
            <div className="course-detail-sidebar">
              <div className="course-detail-enrollment-card">
                {enrolled ? (
                  <>
                    <div className="course-detail-enrollment-status">
                      <div className="course-detail-status-badge enrolled">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <polyline points="20 6 9 17 4 12"/>
                        </svg>
                        <span>Enrolled</span>
                      </div>
                    </div>
                    <p className="course-detail-enrollment-text">
                      You&apos;re enrolled in this course. Start learning now!
                    </p>
                    <Link to={`/courses/${id}/learn`} className="course-detail-enroll-btn primary">
                      <span>Continue Learning</span>
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="9 18 15 12 9 6"/>
                      </svg>
                    </Link>
                  </>
                ) : (
                  <>
                    <div className="course-detail-enrollment-header">
                      <h3>Enroll Now</h3>
                      <p>Get access to all course materials and start learning today.</p>
                    </div>
                    <button
                      onClick={handleEnroll}
                      className="course-detail-enroll-btn primary"
                      disabled={enrolling}
                    >
                      {enrolling ? (
                        <>
                          <div className="spinner-small"></div>
                          <span>Enrolling...</span>
                        </>
                      ) : (
                        <>
                          <span>Enroll in Course</span>
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <polyline points="9 18 15 12 9 6"/>
                          </svg>
                        </>
                      )}
                    </button>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CourseDetail;
