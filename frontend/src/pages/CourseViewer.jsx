import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useGetCourseQuery, useGetProgressQuery, useMarkProgressCompleteMutation } from '../services/apiSlice';
import { authService } from '../utils/auth';
import { toast } from '../utils/toast';

const CourseViewer = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const user = authService.getUser();
  // Force refetch on mount to ensure fresh data
  const { data: courseData, isLoading, error } = useGetCourseQuery(
    id,
    { refetchOnMountOrArgChange: true }
  );
  // Include user ID and force refetch to make progress user-specific
  const { data: progressData } = useGetProgressQuery(
    { courseId: id, userId: user?.userId },
    { 
      skip: !authService.isStudent(),
      refetchOnMountOrArgChange: true
    }
  );
  const [markComplete] = useMarkProgressCompleteMutation();
  
  const course = courseData?.course;
  const [currentModule, setCurrentModule] = useState(null);

  useEffect(() => {
    if (course?.modules && course.modules.length > 0) {
      setCurrentModule(course.modules[0]);
    }
  }, [course]);

  const progressList = progressData?.progress || [];
  const completedModules = new Set(
    progressList
      .filter(p => p.status === 'completed')
      .map(p => p.moduleId)
  );

  const handleMarkComplete = async () => {
    if (!currentModule) return;
    try {
      await markComplete({
        moduleId: currentModule.moduleId,
        courseId: id
      }).unwrap();
      toast.success('Module marked as completed!');
    } catch (err) {
      toast.error(err.data?.error || 'Failed to mark as complete');
    }
  };

  const isModuleCompleted = (moduleId) => {
    return completedModules.has(moduleId);
  };

  if (isLoading) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-loading">
          <div className="spinner-large"></div>
          <p>Loading course content...</p>
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
          <h3>Failed to load course</h3>
          <p>Please try refreshing the page.</p>
        </div>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-error">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <h3>Course not found</h3>
          <p>The course you're looking for doesn't exist.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Header */}
      <div className="page-header">
        <button onClick={() => navigate(-1)} className="back-button">
          ←
        </button>
        <div className="page-header-content">
          <h1 className="page-title">{course.title}</h1>
          <span className="page-badge">Learning Mode</span>
        </div>
      </div>

      <div className="course-viewer-layout">
        {/* Modules Sidebar */}
        <div className="course-viewer-sidebar">
          <div className="card-modern">
            <div className="card-modern-header">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                <path d="M2 17L12 22L22 17"/>
                <path d="M2 12L12 17L22 12"/>
              </svg>
              <h3>Modules</h3>
            </div>
            {course.modules && course.modules.length > 0 ? (
              <div className="modules-sidebar-list">
                {course.modules.map((module, index) => (
                  <div
                    key={module.moduleId}
                    onClick={() => setCurrentModule(module)}
                    className={`module-sidebar-item ${currentModule?.moduleId === module.moduleId ? 'active' : ''}`}
                  >
                    <div className="module-sidebar-number">{index + 1}</div>
                    <div className="module-sidebar-content">
                      <h4>{module.title}</h4>
                      {isModuleCompleted(module.moduleId) && (
                        <span className="module-completed-badge">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <polyline points="20 6 9 17 4 12"/>
                          </svg>
                          Completed
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: '#7f8c8d', padding: '1rem 0' }}>No modules available.</p>
            )}
          </div>
        </div>

        {/* Content Area */}
        <div className="course-viewer-content">
          {currentModule ? (
            <div className="card-modern">
              <div className="module-content-header">
                <div>
                  <h2>{currentModule.title}</h2>
                  {currentModule.description && (
                    <p className="module-description">{currentModule.description}</p>
                  )}
                </div>
                {isModuleCompleted(currentModule.moduleId) && (
                  <div className="module-status-badge completed">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                    <span>Completed</span>
                  </div>
                )}
              </div>

              {currentModule.materials && currentModule.materials.length > 0 && (
                <div className="module-materials" style={{ marginTop: '2rem' }}>
                  <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <polyline points="14 2 14 8 20 8"/>
                    </svg>
                    Course Materials
                  </h3>
                  <div className="materials-list">
                    {currentModule.materials.map((material, index) => (
                      <a
                        key={index}
                        href={material}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="material-item"
                      >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                          <polyline points="14 2 14 8 20 8"/>
                        </svg>
                        <span>Material {index + 1}</span>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <polyline points="9 18 15 12 9 6"/>
                        </svg>
                      </a>
                    ))}
                  </div>
                </div>
              )}

              {authService.isStudent() && (
                <div className="module-actions" style={{ marginTop: '2rem', paddingTop: '2rem', borderTop: '1px solid #eee' }}>
                  {isModuleCompleted(currentModule.moduleId) ? (
                    <div className="completion-message">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="20 6 9 17 4 12"/>
                      </svg>
                      <div>
                        <h4>Module Completed!</h4>
                        <p>Great job! You've completed this module.</p>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={handleMarkComplete}
                      className="btn btn-success btn-large"
                      style={{ width: '100%' }}
                    >
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="20 6 9 17 4 12"/>
                      </svg>
                      <span>Mark as Complete</span>
                    </button>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="card-modern">
              <div className="empty-module-state">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                  <path d="M2 17L12 22L22 17"/>
                  <path d="M2 12L12 17L22 12"/>
                </svg>
                <h3>Select a module</h3>
                <p>Choose a module from the sidebar to start learning</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CourseViewer;

