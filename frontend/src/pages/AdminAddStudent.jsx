import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGetSpecializationsQuery, useAddStudentMutation } from '../services/apiSlice';
import { toast } from '../utils/toast';
import { 
  validateName, 
  validateEmail, 
  validatePassword, 
  validateSelect,
  getPasswordStrength 
} from '../utils/validation';

const AdminAddStudent = () => {
  const navigate = useNavigate();
  const { data: specializationsData, isLoading: loadingSpecs } = useGetSpecializationsQuery();
  const [addStudent, { isLoading }] = useAddStudentMutation();
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    specializationId: ''
  });

  const [errors, setErrors] = useState({
    name: '',
    email: '',
    password: '',
    specializationId: ''
  });

  const [touched, setTouched] = useState({
    name: false,
    email: false,
    password: false,
    specializationId: false
  });

  const specializations = specializationsData?.specializations || [];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });

    // Real-time validation after first blur
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

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Mark all fields as touched
    const allTouched = {
      name: true,
      email: true,
      password: true,
      specializationId: true
    };
    setTouched(allTouched);

    // Validate all fields
    const nameValidation = validateName(formData.name, { fieldName: 'Name' });
    const emailValidation = validateEmail(formData.email);
    const passwordValidation = validatePassword(formData.password);
    const specializationValidation = validateSelect(formData.specializationId, 'specialization');

    const newErrors = {
      name: nameValidation.error,
      email: emailValidation.error,
      password: passwordValidation.error,
      specializationId: specializationValidation.error
    };

    setErrors(newErrors);

    if (!nameValidation.isValid || !emailValidation.isValid || 
        !passwordValidation.isValid || !specializationValidation.isValid) {
      return;
    }

    try {
      await addStudent({
        name: nameValidation.value || formData.name.trim(),
        email: formData.email.trim(),
        password: formData.password,
        specializationId: formData.specializationId
      }).unwrap();
      toast.success('Student created successfully!');
      navigate('/admin/dashboard');
    } catch (err) {
      toast.error(err.data?.error || 'Failed to create student');
    }
  };

  const passwordStrength = getPasswordStrength(formData.password);

  if (loadingSpecs) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="dashboard-container">
      <div className="page-header">
        <button onClick={() => navigate(-1)} className="back-button">←</button>
        <div className="page-header-content">
          <h1 className="page-title">Add Student</h1>
          <p className="page-subtitle">Create a new student account and assign them to a specialization</p>
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
                      <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                      <circle cx="8.5" cy="7" r="4"/>
                      <line x1="20" y1="8" x2="20" y2="14"/>
                      <line x1="23" y1="11" x2="17" y2="11"/>
                    </svg>
                    <span>Create Student</span>
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

export default AdminAddStudent;
