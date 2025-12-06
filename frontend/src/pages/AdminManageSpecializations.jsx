import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  useGetSpecializationsQuery,
  useGetCoursesBySpecializationQuery,
  useGetUsersQuery,
  useCreateSpecializationMutation,
  useUpdateSpecializationMutation,
  useDeleteSpecializationMutation,
  useAdminCreateCourseMutation,
  useUpdateCourseInstructorMutation,
  useAdminDeleteCourseMutation
} from '../services/apiSlice';
import { toast } from '../utils/toast';
import ConfirmModal from '../components/ConfirmModal';
import { 
  validateTitle, 
  validateDescription, 
  validateSpecializationCode 
} from '../utils/validation';

const AdminManageSpecializations = () => {
  const navigate = useNavigate();
  const formRef = useRef(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    description: ''
  });
  const [formErrors, setFormErrors] = useState({
    name: '',
    code: '',
    description: ''
  });
  const [formTouched, setFormTouched] = useState({
    name: false,
    code: false,
    description: false
  });
  const [courseFormData, setCourseFormData] = useState({
    title: '',
    description: '',
    instructorId: ''
  });
  const [courseFormErrors, setCourseFormErrors] = useState({
    title: '',
    description: ''
  });
  const [courseFormTouched, setCourseFormTouched] = useState({
    title: false,
    description: false
  });
  const [showDeleteCourseModal, setShowDeleteCourseModal] = useState(false);
  const [courseToDelete, setCourseToDelete] = useState(null);
  const [showDeleteSpecModal, setShowDeleteSpecModal] = useState(false);
  const [specToDelete, setSpecToDelete] = useState(null);

  const { data: specializationsData, isLoading, refetch: refetchSpecializations } = useGetSpecializationsQuery();
  const { data: coursesData, isLoading: loadingCourses, refetch: refetchCourses } = useGetCoursesBySpecializationQuery(
    editingId,
    { skip: !editingId }
  );
  const { data: instructorsData, isLoading: loadingInstructors } = useGetUsersQuery({ role: 'instructor' });
  
  const [createSpecialization] = useCreateSpecializationMutation();
  const [updateSpecialization] = useUpdateSpecializationMutation();
  const [deleteSpecialization] = useDeleteSpecializationMutation();
  const [createCourse] = useAdminCreateCourseMutation();
  const [updateCourseInstructor] = useUpdateCourseInstructorMutation();
  const [deleteCourse] = useAdminDeleteCourseMutation();

  const specializations = specializationsData?.specializations || [];
  
  // Memoize instructors and courses data to prevent unnecessary re-renders
  const instructors = useMemo(() => instructorsData?.users || [], [instructorsData?.users]);
  const coursesDataRaw = useMemo(() => coursesData?.courses || [], [coursesData?.courses]);
  
  // Enrich courses with instructor names
  const courses = useMemo(() => {
    return coursesDataRaw.map((course) => {
      if (course.instructorId && instructors.length > 0) {
        const instructor = instructors.find(u => u.userId === course.instructorId);
        return {
          ...course,
          instructorName: instructor ? instructor.name : 'Unknown',
          instructorEmail: instructor ? instructor.email : ''
        };
      }
      return { ...course, instructorName: 'No instructor', instructorEmail: '' };
    });
  }, [coursesDataRaw, instructors]);

  useEffect(() => {
    if (editingId && showAddForm) {
      // Scroll to form when editing
      setTimeout(() => {
        if (formRef.current) {
          formRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);
    }
  }, [editingId, showAddForm]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });

    // Real-time validation after first blur
    if (formTouched[name]) {
      validateFormField(name, value);
    }
  };

  const validateFormField = (name, value) => {
    let validation;
    
    switch (name) {
      case 'name':
        validation = validateTitle(value, { fieldName: 'Specialization name', minLength: 3, maxLength: 100 });
        setFormErrors(prev => ({ ...prev, name: validation.error }));
        if (validation.isValid && validation.value) {
          setFormData(prev => ({ ...prev, name: validation.value }));
        }
        break;
      case 'code':
        validation = validateSpecializationCode(value);
        setFormErrors(prev => ({ ...prev, code: validation.error }));
        if (validation.isValid && validation.value) {
          setFormData(prev => ({ ...prev, code: validation.value }));
        }
        break;
      case 'description':
        validation = validateDescription(value, { fieldName: 'Description', minLength: 10, maxLength: 500 });
        setFormErrors(prev => ({ ...prev, description: validation.error }));
        if (validation.isValid && validation.value) {
          setFormData(prev => ({ ...prev, description: validation.value }));
        }
        break;
      default:
        break;
    }
  };

  const handleFormBlur = (e) => {
    const { name, value } = e.target;
    setFormTouched(prev => ({ ...prev, [name]: true }));
    validateFormField(name, value);
  };

  const handleCourseChange = (e) => {
    const { name, value } = e.target;
    setCourseFormData({
      ...courseFormData,
      [name]: value
    });

    // Real-time validation after first blur
    if (courseFormTouched[name]) {
      validateCourseFormField(name, value);
    }
  };

  const validateCourseFormField = (name, value) => {
    let validation;
    
    switch (name) {
      case 'title':
        validation = validateTitle(value, { fieldName: 'Course title' });
        setCourseFormErrors(prev => ({ ...prev, title: validation.error }));
        if (validation.isValid && validation.value) {
          setCourseFormData(prev => ({ ...prev, title: validation.value }));
        }
        break;
      case 'description':
        validation = validateDescription(value, { fieldName: 'Description' });
        setCourseFormErrors(prev => ({ ...prev, description: validation.error }));
        if (validation.isValid && validation.value) {
          setCourseFormData(prev => ({ ...prev, description: validation.value }));
        }
        break;
      default:
        break;
    }
  };

  const handleCourseFormBlur = (e) => {
    const { name, value } = e.target;
    setCourseFormTouched(prev => ({ ...prev, [name]: true }));
    validateCourseFormField(name, value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Mark all fields as touched
    const allTouched = {
      name: true,
      code: true,
      description: true
    };
    setFormTouched(allTouched);

    // Validate all fields
    const nameValidation = validateTitle(formData.name, { fieldName: 'Specialization name', minLength: 3, maxLength: 100 });
    const codeValidation = validateSpecializationCode(formData.code);
    const descriptionValidation = validateDescription(formData.description, { fieldName: 'Description', minLength: 10, maxLength: 500 });

    const newErrors = {
      name: nameValidation.error,
      code: codeValidation.error,
      description: descriptionValidation.error
    };

    setFormErrors(newErrors);

    if (!nameValidation.isValid || !codeValidation.isValid || !descriptionValidation.isValid) {
      return;
    }

    try {
      const specData = {
        name: nameValidation.value || formData.name.trim(),
        code: codeValidation.value || formData.code.trim().toUpperCase(),
        description: descriptionValidation.value || formData.description.trim()
      };

      if (editingId) {
        await updateSpecialization({ id: editingId, ...specData }).unwrap();
        toast.success('Specialization updated successfully!');
      } else {
        await createSpecialization(specData).unwrap();
        toast.success('Specialization created successfully!');
      }
      resetForm();
      refetchSpecializations();
    } catch (err) {
      toast.error(err.data?.error || 'Failed to save specialization');
    }
  };

  const handleAddCourse = async (e) => {
    e.preventDefault();
    if (!editingId) {
      toast.error('Please save the specialization first');
      return;
    }

    // Mark all course fields as touched
    const allTouched = {
      title: true,
      description: true
    };
    setCourseFormTouched(allTouched);

    // Validate all course fields
    const titleValidation = validateTitle(courseFormData.title, { fieldName: 'Course title' });
    const descriptionValidation = validateDescription(courseFormData.description, { fieldName: 'Description' });

    const newErrors = {
      title: titleValidation.error,
      description: descriptionValidation.error
    };

    setCourseFormErrors(newErrors);

    if (!titleValidation.isValid || !descriptionValidation.isValid) {
      return;
    }

    try {
      await createCourse({
        title: titleValidation.value || courseFormData.title.trim(),
        description: descriptionValidation.value || courseFormData.description.trim(),
        instructorId: courseFormData.instructorId || undefined,
        specializationId: editingId,
        category: 'General'
      }).unwrap();
      toast.success('Course added successfully!');
      setCourseFormData({ title: '', description: '', instructorId: '' });
      setCourseFormErrors({ title: '', description: '' });
      setCourseFormTouched({ title: false, description: false });
      refetchCourses();
    } catch (err) {
      toast.error(err.data?.error || 'Failed to add course');
    }
  };

  const handleChangeInstructor = async (courseId, newInstructorId) => {
    if (!newInstructorId) {
      toast.error('Please select an instructor');
      return;
    }
    try {
      await updateCourseInstructor({ courseId, instructorId: newInstructorId }).unwrap();
      toast.success('Instructor changed successfully!');
      refetchCourses();
    } catch (err) {
      toast.error(err.data?.error || 'Failed to change instructor');
    }
  };

  const handleDeleteCourseClick = (courseId) => {
    setCourseToDelete(courseId);
    setShowDeleteCourseModal(true);
  };

  const handleDeleteCourse = async () => {
    if (!courseToDelete) return;
    try {
      await deleteCourse(courseToDelete).unwrap();
      toast.success('Course deleted successfully!');
      refetchCourses();
      setCourseToDelete(null);
    } catch (err) {
      toast.error(err.data?.error || 'Failed to delete course');
    }
  };

  const handleEdit = (spec) => {
    setEditingId(spec.specializationId);
    setFormData({
      name: spec.name,
      code: spec.code,
      description: spec.description || ''
    });
    setShowAddForm(true);
  };

  const handleDeleteClick = (id) => {
    setSpecToDelete(id);
    setShowDeleteSpecModal(true);
  };

  const handleDelete = async () => {
    if (!specToDelete) return;
    try {
      await deleteSpecialization(specToDelete).unwrap();
      toast.success('Specialization deleted successfully!');
      refetchSpecializations();
      setSpecToDelete(null);
    } catch (err) {
      toast.error(err.data?.error || 'Failed to delete specialization');
    }
  };

  const resetForm = () => {
    setFormData({ name: '', code: '', description: '' });
    setFormErrors({ name: '', code: '', description: '' });
    setFormTouched({ name: false, code: false, description: false });
    setCourseFormData({ title: '', description: '', instructorId: '' });
    setCourseFormErrors({ title: '', description: '' });
    setCourseFormTouched({ title: false, description: false });
    setEditingId(null);
    setShowAddForm(false);
  };

  const handleAddClick = () => {
    resetForm();
    setShowAddForm(true);
    setTimeout(() => {
      if (formRef.current) {
        formRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 100);
  };

  if (isLoading) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-loading">
          <div className="spinner-large"></div>
          <p>Loading specializations...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="page-header">
        <button onClick={() => navigate(-1)} className="back-button">←</button>
        <div className="page-header-content" style={{ flex: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 className="page-title">Manage Specializations</h1>
            <p className="page-subtitle">Create and manage specializations and their courses</p>
          </div>
          <button
            className="btn btn-primary btn-large"
            onClick={handleAddClick}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            <span>Add Specialization</span>
          </button>
        </div>
      </div>

      {showAddForm && (
        <div ref={formRef} className="form-card" style={{ marginBottom: '2rem' }}>
          <div className="card-modern-header">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
              <path d="M2 17L12 22L22 17"/>
              <path d="M2 12L12 17L22 12"/>
            </svg>
            <h2>{editingId ? 'Edit' : 'Add'} Specialization</h2>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Name *</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                onBlur={handleFormBlur}
                className={formTouched.name && formErrors.name ? 'input-error' : ''}
                required
              />
              {formTouched.name && formErrors.name && (
                <span className="error-message">{formErrors.name}</span>
              )}
            </div>
            <div className="form-group">
              <label>Code *</label>
              <input
                type="text"
                name="code"
                value={formData.code}
                onChange={handleChange}
                onBlur={handleFormBlur}
                className={formTouched.code && formErrors.code ? 'input-error' : ''}
                required
                style={{ textTransform: 'uppercase' }}
                disabled={editingId !== null}
              />
              {formTouched.code && formErrors.code && (
                <span className="error-message">{formErrors.code}</span>
              )}
              {!formTouched.code && (
                <small style={{ color: '#666' }}>Uppercase letters, numbers, and hyphens only (e.g., MSC-DA)</small>
              )}
            </div>
            <div className="form-group">
              <label>Description *</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                onBlur={handleFormBlur}
                className={formTouched.description && formErrors.description ? 'input-error' : ''}
                rows="3"
                required
              />
              {formTouched.description && formErrors.description && (
                <span className="error-message">{formErrors.description}</span>
              )}
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary btn-large">
                {editingId ? (
                  <>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                      <polyline points="17 21 17 13 7 13 7 21"/>
                      <polyline points="7 3 7 8 15 8"/>
                    </svg>
                    <span>Update Specialization</span>
                  </>
                ) : (
                  <>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <line x1="12" y1="5" x2="12" y2="19"/>
                      <line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                    <span>Create Specialization</span>
                  </>
                )}
              </button>
              <button type="button" className="btn btn-secondary btn-large" onClick={resetForm}>
                Cancel
              </button>
            </div>
          </form>

          {editingId && (
            <div style={{ marginTop: '2rem', paddingTop: '2rem', borderTop: '2px solid #ecf0f1' }}>
              <div className="card-modern-header" style={{ marginBottom: '1.5rem' }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                  <path d="M2 17L12 22L22 17"/>
                  <path d="M2 12L12 17L22 12"/>
                </svg>
                <h3>Manage Courses</h3>
              </div>
              {loadingCourses ? (
                <p>Loading courses...</p>
              ) : (
                <>
                  <div style={{ marginBottom: '2rem', padding: '1.5rem', background: '#f8f9fa', borderRadius: '8px', border: '1px solid #e9ecef' }}>
                    <h4 style={{ marginTop: 0, marginBottom: '1rem', color: '#2c3e50', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <line x1="12" y1="5" x2="12" y2="19"/>
                        <line x1="5" y1="12" x2="19" y2="12"/>
                      </svg>
                      Add New Course
                    </h4>
                    <form onSubmit={handleAddCourse}>
                      <div style={{ display: 'grid', gridTemplateColumns: '2fr 2fr 2fr 1fr', gap: '1rem', alignItems: 'start' }}>
                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label>Course Title *</label>
                          <input
                            type="text"
                            name="title"
                            value={courseFormData.title}
                            onChange={handleCourseChange}
                            onBlur={handleCourseFormBlur}
                            className={courseFormTouched.title && courseFormErrors.title ? 'input-error' : ''}
                            required
                          />
                          {courseFormTouched.title && courseFormErrors.title && (
                            <span className="error-message" style={{ fontSize: '0.8rem', display: 'block', marginTop: '0.25rem' }}>{courseFormErrors.title}</span>
                          )}
                        </div>
                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label>Description *</label>
                          <input
                            type="text"
                            name="description"
                            value={courseFormData.description}
                            onChange={handleCourseChange}
                            onBlur={handleCourseFormBlur}
                            className={courseFormTouched.description && courseFormErrors.description ? 'input-error' : ''}
                            required
                          />
                          {courseFormTouched.description && courseFormErrors.description && (
                            <span className="error-message" style={{ fontSize: '0.8rem', display: 'block', marginTop: '0.25rem' }}>{courseFormErrors.description}</span>
                          )}
                        </div>
                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label>Instructor {instructors.length === 0 && '(Optional)'}</label>
                          <select
                            name="instructorId"
                            value={courseFormData.instructorId}
                            onChange={handleCourseChange}
                            disabled={loadingInstructors}
                            style={{ width: '100%' }}
                          >
                            <option value="">{loadingInstructors ? 'Loading...' : instructors.length === 0 ? 'No instructors available' : 'Select instructor (optional)'}</option>
                            {instructors.map((instructor) => (
                              <option key={instructor.userId} value={instructor.userId}>
                                {instructor.name} ({instructor.email})
                              </option>
                            ))}
                          </select>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'flex-start', paddingTop: '1.5rem' }}>
                          <button type="submit" className="btn btn-primary" style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <line x1="12" y1="5" x2="12" y2="19"/>
                              <line x1="5" y1="12" x2="19" y2="12"/>
                            </svg>
                            <span>Add Course</span>
                          </button>
                        </div>
                      </div>
                      {instructors.length === 0 && !loadingInstructors && (
                        <div style={{ marginTop: '0.5rem' }}>
                          <small style={{ color: '#666', fontStyle: 'italic' }}>
                            Note: Course will be created without an instructor. You can assign one later.
                          </small>
                        </div>
                      )}
                    </form>
                  </div>
                  <div>
                    <h4 style={{ marginBottom: '1rem', color: '#2c3e50', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                        <path d="M2 17L12 22L22 17"/>
                        <path d="M2 12L12 17L22 12"/>
                      </svg>
                      Existing Courses
                      <span style={{ fontSize: '0.9rem', fontWeight: 'normal', color: '#7f8c8d', marginLeft: '0.5rem' }}>
                        ({courses.length})
                      </span>
                    </h4>
                    {courses.length > 0 ? (
                      <div style={{ display: 'grid', gap: '1rem' }}>
                        {courses.map((course) => (
                          <div
                            key={course.courseId}
                            className="card-modern"
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              padding: '1.25rem',
                              gap: '1rem',
                              marginBottom: 0
                            }}
                          >
                            <div style={{ flex: 1 }}>
                              <h4 style={{ margin: '0 0 0.5rem 0', color: '#2c3e50', fontSize: '1.1rem' }}>
                                {course.title}
                              </h4>
                              {course.description && (
                                <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.95rem', color: '#7f8c8d' }}>
                                  {course.description}
                                </p>
                              )}
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', color: '#95a5a6' }}>
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                                  <circle cx="9" cy="7" r="4"/>
                                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                                  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                                </svg>
                                <span>{course.instructorName || 'No instructor assigned'}</span>
                              </div>
                            </div>
                            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexShrink: 0 }}>
                              <select
                                value={course.instructorId || ''}
                                onChange={(e) => handleChangeInstructor(course.courseId, e.target.value)}
                                disabled={loadingInstructors}
                                className="form-group"
                                style={{
                                  padding: '0.5rem 0.75rem',
                                  fontSize: '0.875rem',
                                  borderRadius: '6px',
                                  border: '2px solid #e0e0e0',
                                  minWidth: '220px',
                                  cursor: loadingInstructors ? 'not-allowed' : 'pointer'
                                }}
                              >
                                <option value="">{loadingInstructors ? 'Loading...' : 'Change instructor...'}</option>
                                {instructors.map((instructor) => (
                                  <option key={instructor.userId} value={instructor.userId}>
                                    {instructor.name} ({instructor.email})
                                  </option>
                                ))}
                              </select>
                              <button
                                className="btn btn-danger"
                                style={{ 
                                  padding: '0.5rem 1rem', 
                                  fontSize: '0.875rem',
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '0.5rem'
                                }}
                                onClick={() => handleDeleteCourseClick(course.courseId)}
                              >
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                  <polyline points="3 6 5 6 21 6"/>
                                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                                </svg>
                                <span>Delete</span>
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div style={{ padding: '3rem', textAlign: 'center', background: '#f8f9fa', borderRadius: '8px', border: '1px dashed #dee2e6' }}>
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ color: '#bdc3c7', marginBottom: '1rem' }}>
                          <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                          <path d="M2 17L12 22L22 17"/>
                          <path d="M2 12L12 17L22 12"/>
                        </svg>
                        <p style={{ color: '#7f8c8d', fontSize: '1rem', margin: 0 }}>No courses for this specialization yet.</p>
                        <p style={{ color: '#95a5a6', fontSize: '0.875rem', margin: '0.5rem 0 0 0' }}>Add a course using the form above.</p>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      )}

      {!showAddForm && (
        <div className="dashboard-section">
          <div className="dashboard-section-header">
            <h2>All Specializations</h2>
            <span className="enrollment-count">{specializations.length} {specializations.length === 1 ? 'specialization' : 'specializations'}</span>
          </div>

          {specializations.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">
                <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                  <path d="M2 17L12 22L22 17"/>
                  <path d="M2 12L12 17L22 12"/>
                </svg>
              </div>
              <h3>No specializations yet</h3>
              <p>Create your first specialization to get started</p>
              <button onClick={handleAddClick} className="btn btn-primary btn-large" style={{ marginTop: '1rem' }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="12" y1="5" x2="12" y2="19"/>
                  <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
                Add Specialization
              </button>
            </div>
          ) : (
            <div className="enrollments-grid">
              {specializations.map((spec) => (
                <div key={spec.specializationId} className="enrollment-card">
                  <div className="enrollment-card-header">
                    <div className="enrollment-card-icon" style={{ color: '#e67e22' }}>
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                        <path d="M2 17L12 22L22 17"/>
                        <path d="M2 12L12 17L22 12"/>
                      </svg>
                    </div>
                    <h3 className="enrollment-card-title">{spec.name}</h3>
                  </div>
                  <div style={{ marginBottom: '1rem' }}>
                    <span className="page-badge" style={{ marginLeft: 0 }}>{spec.code}</span>
                  </div>
                  {spec.description && (
                    <p className="enrollment-card-description">{spec.description}</p>
                  )}
                  <div className="enrollment-card-footer" style={{ display: 'flex', gap: '0.75rem' }}>
                    <button
                      className="btn btn-secondary"
                      onClick={() => handleEdit(spec)}
                      style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                    >
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                      </svg>
                      <span>Edit</span>
                    </button>
                    <button
                      className="btn btn-danger"
                      onClick={() => handleDeleteClick(spec.specializationId)}
                      style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                    >
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="3 6 5 6 21 6"/>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                      </svg>
                      <span>Delete</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <ConfirmModal
        isOpen={showDeleteCourseModal}
        onClose={() => {
          setShowDeleteCourseModal(false);
          setCourseToDelete(null);
        }}
        onConfirm={handleDeleteCourse}
        title="Delete Course"
        message="Are you sure you want to delete this course? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        type="danger"
      />

      <ConfirmModal
        isOpen={showDeleteSpecModal}
        onClose={() => {
          setShowDeleteSpecModal(false);
          setSpecToDelete(null);
        }}
        onConfirm={handleDelete}
        title="Delete Specialization"
        message="Are you sure you want to delete this specialization? This will also delete all courses within it. This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        type="danger"
      />
    </div>
  );
};

export default AdminManageSpecializations;
