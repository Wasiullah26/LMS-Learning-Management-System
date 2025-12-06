/**
 * Validation utility functions for form inputs
 */

// Email validation
export const validateEmail = (email) => {
  if (!email || email.trim() === '') {
    return { isValid: false, error: 'Email is required' };
  }
  
  const trimmedEmail = email.trim();
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  
  if (!emailRegex.test(trimmedEmail)) {
    return { isValid: false, error: 'Please enter a valid email address' };
  }
  
  // Optional: Check for specific domain
  // if (!trimmedEmail.endsWith('@ncirl.ie')) {
  //   return { isValid: false, error: 'Email must be from @ncirl.ie domain' };
  // }
  
  return { isValid: true, error: '' };
};

// Password validation
export const validatePassword = (password, options = {}) => {
  const {
    minLength = 8,
    maxLength = 128,
    requireUppercase = true,
    requireLowercase = true,
    requireNumber = true,
    requireSpecialChar = false
  } = options;

  if (!password) {
    return { isValid: false, error: 'Password is required' };
  }

  if (password.length < minLength) {
    return { isValid: false, error: `Password must be at least ${minLength} characters` };
  }

  if (password.length > maxLength) {
    return { isValid: false, error: `Password must be no more than ${maxLength} characters` };
  }

  if (requireUppercase && !/[A-Z]/.test(password)) {
    return { isValid: false, error: 'Password must contain at least one uppercase letter' };
  }

  if (requireLowercase && !/[a-z]/.test(password)) {
    return { isValid: false, error: 'Password must contain at least one lowercase letter' };
  }

  if (requireNumber && !/[0-9]/.test(password)) {
    return { isValid: false, error: 'Password must contain at least one number' };
  }

  if (requireSpecialChar && !/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    return { isValid: false, error: 'Password must contain at least one special character' };
  }

  return { isValid: true, error: '' };
};

// Password strength indicator
export const getPasswordStrength = (password) => {
  if (!password) return { strength: 0, label: '', color: '' };
  
  let strength = 0;
  
  if (password.length >= 8) strength++;
  if (password.length >= 12) strength++;
  if (/[a-z]/.test(password)) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/[0-9]/.test(password)) strength++;
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++;
  
  if (strength <= 2) {
    return { strength, label: 'Weak', color: '#e74c3c' };
  } else if (strength <= 4) {
    return { strength, label: 'Medium', color: '#f39c12' };
  } else {
    return { strength, label: 'Strong', color: '#27ae60' };
  }
};

// Name validation
export const validateName = (name, options = {}) => {
  const { minLength = 2, maxLength = 100, fieldName = 'Name' } = options;

  if (!name || name.trim() === '') {
    return { isValid: false, error: `${fieldName} is required` };
  }

  const trimmedName = name.trim();

  if (trimmedName.length < minLength) {
    return { isValid: false, error: `${fieldName} must be at least ${minLength} characters` };
  }

  if (trimmedName.length > maxLength) {
    return { isValid: false, error: `${fieldName} must be no more than ${maxLength} characters` };
  }

  // Allow letters, spaces, hyphens, apostrophes
  const nameRegex = /^[a-zA-Z\s'-]+$/;
  if (!nameRegex.test(trimmedName)) {
    return { isValid: false, error: `${fieldName} can only contain letters, spaces, hyphens, and apostrophes` };
  }

  // Check for leading/trailing spaces (shouldn't happen after trim, but just in case)
  if (name !== trimmedName) {
    return { isValid: false, error: `${fieldName} cannot have leading or trailing spaces` };
  }

  return { isValid: true, error: '', value: trimmedName };
};

// Title validation
export const validateTitle = (title, options = {}) => {
  const { minLength = 3, maxLength = 200, fieldName = 'Title' } = options;

  if (!title || title.trim() === '') {
    return { isValid: false, error: `${fieldName} is required` };
  }

  const trimmedTitle = title.trim();

  if (trimmedTitle.length < minLength) {
    return { isValid: false, error: `${fieldName} must be at least ${minLength} characters` };
  }

  if (trimmedTitle.length > maxLength) {
    return { isValid: false, error: `${fieldName} must be no more than ${maxLength} characters` };
  }

  return { isValid: true, error: '', value: trimmedTitle };
};

// Description validation
export const validateDescription = (description, options = {}) => {
  const { minLength = 10, maxLength = 2000, fieldName = 'Description' } = options;

  if (!description || description.trim() === '') {
    return { isValid: false, error: `${fieldName} is required` };
  }

  const trimmedDescription = description.trim();

  if (trimmedDescription.length < minLength) {
    return { isValid: false, error: `${fieldName} must be at least ${minLength} characters` };
  }

  if (trimmedDescription.length > maxLength) {
    return { isValid: false, error: `${fieldName} must be no more than ${maxLength} characters` };
  }

  return { isValid: true, error: '', value: trimmedDescription };
};

// Module description validation (shorter)
export const validateModuleDescription = (description) => {
  return validateDescription(description, { minLength: 10, maxLength: 1000, fieldName: 'Module description' });
};

// Specialization code validation
export const validateSpecializationCode = (code) => {
  if (!code || code.trim() === '') {
    return { isValid: false, error: 'Specialization code is required' };
  }

  const trimmedCode = code.trim().toUpperCase();

  if (trimmedCode.length < 2) {
    return { isValid: false, error: 'Code must be at least 2 characters' };
  }

  if (trimmedCode.length > 20) {
    return { isValid: false, error: 'Code must be no more than 20 characters' };
  }

  // Alphanumeric and hyphens only
  const codeRegex = /^[A-Z0-9-]+$/;
  if (!codeRegex.test(trimmedCode)) {
    return { isValid: false, error: 'Code can only contain uppercase letters, numbers, and hyphens' };
  }

  return { isValid: true, error: '', value: trimmedCode };
};

// Number validation (for order)
export const validateNumber = (value, options = {}) => {
  const { min = 1, max = 999, fieldName = 'Number', required = true } = options;

  if (required && (!value || value === '')) {
    return { isValid: false, error: `${fieldName} is required` };
  }

  if (!required && (!value || value === '')) {
    return { isValid: true, error: '', value: null };
  }

  const numValue = parseInt(value, 10);

  if (isNaN(numValue)) {
    return { isValid: false, error: `${fieldName} must be a valid number` };
  }

  if (numValue < min) {
    return { isValid: false, error: `${fieldName} must be at least ${min}` };
  }

  if (numValue > max) {
    return { isValid: false, error: `${fieldName} must be no more than ${max}` };
  }

  return { isValid: true, error: '', value: numValue };
};

// Password match validation
export const validatePasswordMatch = (password, confirmPassword) => {
  if (!confirmPassword) {
    return { isValid: false, error: 'Please confirm your password' };
  }

  if (password !== confirmPassword) {
    return { isValid: false, error: 'Passwords do not match' };
  }

  return { isValid: true, error: '' };
};

// Check if password is different from old password
export const validatePasswordChange = (oldPassword, newPassword) => {
  if (oldPassword === newPassword) {
    return { isValid: false, error: 'New password must be different from current password' };
  }

  return { isValid: true, error: '' };
};

// Category validation
export const validateCategory = (category) => {
  if (!category || category.trim() === '') {
    return { isValid: true, error: '', value: '' }; // Optional field
  }

  const trimmedCategory = category.trim();

  if (trimmedCategory.length > 50) {
    return { isValid: false, error: 'Category must be no more than 50 characters' };
  }

  return { isValid: true, error: '', value: trimmedCategory };
};

// Select/dropdown validation
export const validateSelect = (value, fieldName = 'Selection') => {
  if (!value || value === '') {
    return { isValid: false, error: `Please select a ${fieldName.toLowerCase()}` };
  }

  return { isValid: true, error: '' };
};

// Checkbox group validation (at least one selected)
export const validateCheckboxGroup = (selectedItems, fieldName = 'item') => {
  if (!selectedItems || selectedItems.length === 0) {
    return { isValid: false, error: `Please select at least one ${fieldName}` };
  }

  return { isValid: true, error: '' };
};

