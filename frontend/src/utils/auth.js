



const TOKEN_KEY = 'lms_token';
const USER_KEY = 'lms_user';

export const authService = {

  setAuth: (token, user) => {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },


  getToken: () => {
    return localStorage.getItem(TOKEN_KEY);
  },


  getUser: () => {
    const userStr = localStorage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  },


  isAuthenticated: () => {
    return !!localStorage.getItem(TOKEN_KEY);
  },


  isInstructor: () => {
    const user = authService.getUser();
    return user && user.role === 'instructor';
  },


  isStudent: () => {
    const user = authService.getUser();
    return user && user.role === 'student';
  },


  isAdmin: () => {
    const user = authService.getUser();
    return user && user.role === 'admin';
  },


  clearAuth: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
};

