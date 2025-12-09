/**
 * Authentication utilities
 */

const TOKEN_KEY = 'lms_token';
const USER_KEY = 'lms_user';

export const authService = {
  // Save token and user to localStorage
  setAuth: (token, user) => {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  // Get token from localStorage
  getToken: () => {
    return localStorage.getItem(TOKEN_KEY);
  },

  // Get user from localStorage
  getUser: () => {
    const userStr = localStorage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem(TOKEN_KEY);
  },

  // Check if user is instructor
  isInstructor: () => {
    const user = authService.getUser();
    return user && user.role === 'instructor';
  },

  // Check if user is student
  isStudent: () => {
    const user = authService.getUser();
    return user && user.role === 'student';
  },

  // Check if user is admin
  isAdmin: () => {
    const user = authService.getUser();
    return user && user.role === 'admin';
  },

  // Clear authentication data
  clearAuth: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
};

