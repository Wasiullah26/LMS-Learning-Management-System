import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  useGetSpecializationsQuery,
  useGetCoursesBySpecializationQuery,
  useAddInstructorMutation
} from '../services/apiSlice';
import { toast } from '../utils/toast';
import {
  validateName,
  validateEmail,
  validatePassword,
  validateSelect,
  validateCheckboxGroup,
  getPasswordStrength
} from '../utils/validation';

const AdminAddInstructor = () => {
  const navigate = useNavigate();
  const { data: specializationsData, isLoading: loadingSpecs } = useGetSpecializationsQuery();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    specializationId: '',
    courseIds: []
  });

  const [errors, setErrors] = useState({
    name: '',
    email: '',
    password: '',
    specializationId: '',
    courseIds: ''
  });

  const [touched, setTouched] = useState({
    name: false,
    email: false,
    password: false,
    specializationId: false,
    courseIds: false
  });

  const { data: coursesData, isLoading: loadingCourses } = useGetCoursesBySpecializationQuery(
    formData.specializationId,
    { skip: !formData.specializationId }
  );
  const [addInstructor, { isLoading }] = useAddInstructorMutation();

  const specializations = specializationsData?.specializations || [];
  const courses = coursesData?.courses || [];

  React.useEffect(() => {
    if (!formData.specializationId) {
      setFormData(prev => ({ ...prev, courseIds: [] }));
      setErrors(prev => ({ ...prev, courseIds: '' }));
    }
  }, [formData.specializationId]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });

    if (touched[name]) {
      validateField(name, value);
    }
  };

  const validateField = (name, value) => {
    let validation;

    switch (name) {
      case 'name':
        validation = validateName(value, { fieldName: 'Name' });
        setErrors(prev => ({ ...prev, name: validation.error }));
        if (validation.isValid && validation.value) {
          setFormData(prev => ({ ...prev, name: validation.value }));
        }
        break;
      case 'email':
        validation = validateEmail(value);
        setErrors(prev => ({ ...prev, email: validation.error }));
        break;
      case 'password':
        validation = validatePassword(value);
        setErrors(prev => ({ ...prev, password: validation.error }));
        break;
      case 'specializationId':
        validation = validateSelect(value, 'specialization');
        setErrors(prev => ({ ...prev, specializationId: validation.error }));
        break;
      default:
        break;
    }
  };

  const handleBlur = (e) => {
    const { name, value } = e.target;
    setTouched(prev => ({ ...prev, [name]: true }));
    validateField(name, value);
  };

  const handleCourseToggle = (courseId, checked) => {
    let newCourseIds;
    if (checked) {
      newCourseIds = [...formData.courseIds, courseId];
    } else {
      newCourseIds = formData.courseIds.filter(id => id !== courseId);
    }

    setFormData(prev => ({ ...prev, courseIds: newCourseIds }));

    if (touched.courseIds) {
      const validation = validateCheckboxGroup(newCourseIds, 'course');
      setErrors(prev => ({ ...prev, courseIds: validation.error }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const allTouched = {
      name: true,
      email: true,
      password: true,
      specializationId: true,
      courseIds: true
    };
    setTouched(allTouched);

    const nameValidation = validateName(formData.name, { fieldName: 'Name' });
    const emailValidation = validateEmail(formData.email);
    const passwordValidation = validatePassword(formData.password);
    const specializationValidation = validateSelect(formData.specializationId, 'specialization');
    const coursesValidation = validateCheckboxGroup(formData.courseIds, 'course');

    const newErrors = {
      name: nameValidation.error,
      email: emailValidation.error,
      password: passwordValidation.error,
      specializationId: specializationValidation.error,
      courseIds: coursesValidation.error
    };

    setErrors(newErrors);

    if (!nameValidation.isValid || !emailValidation.isValid ||
        !passwordValidation.isValid || !specializationValidation.isValid ||
        !coursesValidation.isValid) {
      return;
    }

    try {
      await addInstructor({
        name: nameValidation.value || formData.name.trim(),
        email: formData.email.trim(),
        password: formData.password,
        specializationId: formData.specializationId,
        courseIds: formData.courseIds
      }).unwrap();
      toast.success('Instructor created successfully!');
      navigate('/admin/dashboard');
    } catch (err) {
      toast.error(err.data?.error || 'Failed to create instructor');
    }
  };

  const passwordStrength = getPasswordStrength(formData.password);

  if (loadingSpecs) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-loading">
          <div className="spinner-large"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="page-header">
        <button onClick={() => navigate(-1)} className="back-button">←</button>
        <div className="page-header-content">
          <h1 className="page-title">Add Instructor</h1>
          <p className="page-subtitle">Create a new instructor account and assign them to courses</p>
        </div>
      </div>

      <div className="form-page-container">
        <div className="form-card">
          <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Name *</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              onBlur={handleBlur}
              className={touched.name && errors.name ? 'input-error' : ''}
              required
            />
            {touched.name && errors.name && (
              <span className="error-message">{errors.name}</span>
            )}
          </div>
          <div className="form-group">
            <label>Email *</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              onBlur={handleBlur}
              className={touched.email && errors.email ? 'input-error' : ''}
              required
            />
            {touched.email && errors.email && (
              <span className="error-message">{errors.email}</span>
            )}
          </div>
          <div className="form-group">
            <label>Password *</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              onBlur={handleBlur}
              className={touched.password && errors.password ? 'input-error' : ''}
              required
              minLength="8"
            />
            {formData.password && (
              <div className="password-strength" style={{ marginTop: '0.5rem' }}>
                <div className="password-strength-bar">
                  <div
                    className="password-strength-fill"
                    style={{
                      width: `${(passwordStrength.strength / 6) * 100}%`,
                      backgroundColor: passwordStrength.color
                    }}
                  ></div>
                </div>
                <span style={{ fontSize: '0.85rem', color: passwordStrength.color, fontWeight: '500' }}>
                  {passwordStrength.label}
                </span>
              </div>
            )}
            {touched.password && errors.password && (
              <span className="error-message">{errors.password}</span>
            )}
            {!touched.password && (
              <small style={{ color: '#666' }}>
                Must be at least 8 characters with uppercase, lowercase, and number
              </small>
            )}
          </div>
          <div className="form-group">
            <label>Specialization *</label>
            <select
              name="specializationId"
              value={formData.specializationId}
              onChange={handleChange}
              onBlur={handleBlur}
              className={touched.specializationId && errors.specializationId ? 'input-error' : ''}
              required
            >
              <option value="">Select a specialization</option>
              {specializations.map((spec) => (
                <option key={spec.specializationId} value={spec.specializationId}>
                  {spec.name}
                </option>
              ))}
            </select>
            {touched.specializationId && errors.specializationId && (
              <span className="error-message">{errors.specializationId}</span>
            )}
          </div>
          {formData.specializationId && (
            <div className="form-group">
              <label>Courses * (Select multiple)</label>
              {loadingCourses ? (
                <p>Loading courses...</p>
              ) : courses.length > 0 ? (
                <>
                  <div
                    className={touched.courseIds && errors.courseIds ? 'checkbox-group-error' : ''}
                    style={{
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      padding: '1rem',
                      maxHeight: '300px',
                      overflowY: 'auto',
                      backgroundColor: '#f9f9f9'
                    }}
                  >
                    {courses.map((course) => (
                      <label
                        key={course.courseId}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          padding: '0.75rem',
                          marginBottom: '0.5rem',
                          backgroundColor: 'white',
                          borderRadius: '4px',
                          border: '1px solid #eee',
                          cursor: 'pointer',
                          transition: 'background-color 0.2s'
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f0f0f0'}
                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
                      >
                        <input
                          type="checkbox"
                          checked={formData.courseIds.includes(course.courseId)}
                          onChange={(e) => {
                            handleCourseToggle(course.courseId, e.target.checked);
                            setTouched(prev => ({ ...prev, courseIds: true }));
                          }}
                          style={{ marginRight: '0.75rem', width: '18px', height: '18px', cursor: 'pointer' }}
                        />
                        <div style={{ flex: 1 }}>
                          <strong>{course.title}</strong>
                          {course.description && (
                            <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', color: '#666' }}>
                              {course.description}
                            </p>
                          )}
                        </div>
                      </label>
                    ))}
                  </div>
                  {touched.courseIds && errors.courseIds && (
                    <span className="error-message">{errors.courseIds}</span>
                  )}
                  {formData.courseIds.length > 0 && (
                    <p style={{ marginTop: '0.75rem', color: '#27ae60', fontSize: '0.9rem', fontWeight: '500' }}>
                      {formData.courseIds.length} course(s) selected
                    </p>
                  )}
                </>
              ) : (
                <p style={{ color: '#666', padding: '1rem', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
                  No courses available for this specialization
                </p>
              )}
            </div>
          )}
          <div className="form-actions">
            <button type="submit" className="btn btn-primary btn-large" disabled={isLoading}>
              {isLoading ? (
                <>
                  <div className="spinner-small"></div>
                  <span>Creating...</span>
                </>
              ) : (
                <>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                  </svg>
                  <span>Create Instructor</span>
                </>
              )}
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-large"
              onClick={() => navigate('/admin/dashboard')}
            >
              Cancel
            </button>
          </div>
        </form>
        </div>
      </div>
    </div>
  );
};

export default AdminAddInstructor;
