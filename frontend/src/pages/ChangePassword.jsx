import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChangePasswordMutation } from '../services/apiSlice';
import { toast } from '../utils/toast';
import { 
  validatePassword, 
  validatePasswordMatch, 
  validatePasswordChange,
  getPasswordStrength 
} from '../utils/validation';

const ChangePassword = () => {
  const navigate = useNavigate();
  const [changePassword, { isLoading }] = useChangePasswordMutation();
  const [formData, setFormData] = useState({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const [errors, setErrors] = useState({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const [touched, setTouched] = useState({
    oldPassword: false,
    newPassword: false,
    confirmPassword: false
  });

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

    // Special handling for confirm password - check match in real-time
    if (name === 'newPassword' && touched.confirmPassword && formData.confirmPassword) {
      const matchValidation = validatePasswordMatch(value, formData.confirmPassword);
      setErrors(prev => ({ ...prev, confirmPassword: matchValidation.error }));
    }

    if (name === 'confirmPassword' && touched.confirmPassword) {
      const matchValidation = validatePasswordMatch(formData.newPassword, value);
      setErrors(prev => ({ ...prev, confirmPassword: matchValidation.error }));
    }
  };

  const validateField = (name, value) => {
    let validation;
    
    switch (name) {
      case 'oldPassword':
        if (!value || value.trim() === '') {
          setErrors(prev => ({ ...prev, oldPassword: 'Current password is required' }));
        } else {
          setErrors(prev => ({ ...prev, oldPassword: '' }));
        }
        break;
      case 'newPassword':
        validation = validatePassword(value);
        setErrors(prev => ({ ...prev, newPassword: validation.error }));
        
        // Also check if it's different from old password
        if (validation.isValid && formData.oldPassword) {
          const changeValidation = validatePasswordChange(formData.oldPassword, value);
          if (!changeValidation.isValid) {
            setErrors(prev => ({ ...prev, newPassword: changeValidation.error }));
          }
        }
        
        // Check confirm password match if it's been touched
        if (touched.confirmPassword && formData.confirmPassword) {
          const matchValidation = validatePasswordMatch(value, formData.confirmPassword);
          setErrors(prev => ({ ...prev, confirmPassword: matchValidation.error }));
        }
        break;
      case 'confirmPassword':
        validation = validatePasswordMatch(formData.newPassword, value);
        setErrors(prev => ({ ...prev, confirmPassword: validation.error }));
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
      oldPassword: true,
      newPassword: true,
      confirmPassword: true
    };
    setTouched(allTouched);

    // Validate all fields
    const oldPasswordError = !formData.oldPassword || formData.oldPassword.trim() === '' 
      ? 'Current password is required' 
      : '';
    
    const newPasswordValidation = validatePassword(formData.newPassword);
    const confirmPasswordValidation = validatePasswordMatch(formData.newPassword, formData.confirmPassword);
    
    // Check if new password is different from old
    const passwordChangeValidation = validatePasswordChange(formData.oldPassword, formData.newPassword);
    
    const newPasswordError = newPasswordValidation.isValid 
      ? passwordChangeValidation.error 
      : newPasswordValidation.error;

    const newErrors = {
      oldPassword: oldPasswordError,
      newPassword: newPasswordError,
      confirmPassword: confirmPasswordValidation.error
    };

    setErrors(newErrors);

    if (oldPasswordError || newPasswordError || confirmPasswordValidation.error) {
      return;
    }

    try {
      await changePassword({
        oldPassword: formData.oldPassword,
        newPassword: formData.newPassword
      }).unwrap();
      toast.success('Password changed successfully!');
      navigate('/dashboard');
    } catch (err) {
      toast.error(err.data?.error || 'Failed to change password');
    }
  };

  const passwordStrength = getPasswordStrength(formData.newPassword);
  const passwordsMatch = formData.newPassword && formData.confirmPassword && 
                         formData.newPassword === formData.confirmPassword && 
                         !errors.confirmPassword;

  return (
    <div className="dashboard-container">
      <div className="page-header">
        <button onClick={() => navigate('/dashboard')} className="back-button">←</button>
        <div className="page-header-content">
          <h1 className="page-title">Change Password</h1>
          <p className="page-subtitle">Update your account password</p>
        </div>
      </div>

      <div className="form-page-container">
        <div className="form-card">
          <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Current Password *</label>
            <input
              type="password"
              name="oldPassword"
              value={formData.oldPassword}
              onChange={handleChange}
              onBlur={handleBlur}
              className={touched.oldPassword && errors.oldPassword ? 'input-error' : ''}
              required
            />
            {touched.oldPassword && errors.oldPassword && (
              <span className="error-message">{errors.oldPassword}</span>
            )}
          </div>
          <div className="form-group">
            <label>New Password *</label>
            <input
              type="password"
              name="newPassword"
              value={formData.newPassword}
              onChange={handleChange}
              onBlur={handleBlur}
              className={touched.newPassword && errors.newPassword ? 'input-error' : ''}
              required
              minLength="8"
            />
            {formData.newPassword && (
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
            {touched.newPassword && errors.newPassword && (
              <span className="error-message">{errors.newPassword}</span>
            )}
            {!touched.newPassword && (
              <small style={{ color: '#666' }}>
                Must be at least 8 characters with uppercase, lowercase, and number
              </small>
            )}
          </div>
          <div className="form-group">
            <label>Confirm New Password *</label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              onBlur={handleBlur}
              className={touched.confirmPassword && errors.confirmPassword ? 'input-error' : ''}
              required
              minLength="8"
            />
            {touched.confirmPassword && passwordsMatch && (
              <span className="success-message" style={{ color: '#27ae60', fontSize: '0.875rem', marginTop: '0.25rem' }}>
                ✓ Passwords match
              </span>
            )}
            {touched.confirmPassword && errors.confirmPassword && (
              <span className="error-message">{errors.confirmPassword}</span>
            )}
          </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary btn-large" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <div className="spinner-small"></div>
                    <span>Changing...</span>
                  </>
                ) : (
                  <>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                      <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                    </svg>
                    <span>Change Password</span>
                  </>
                )}
              </button>
              <button
                type="button"
                className="btn btn-secondary btn-large"
                onClick={() => navigate('/dashboard')}
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

export default ChangePassword;
