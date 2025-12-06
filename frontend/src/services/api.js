/**
 * API service for making HTTP requests
 */

import axios from 'axios';
import { authService } from '../utils/auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = authService.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle 401 errors (unauthorized)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      authService.clearAuth();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  changePassword: (data) => api.post('/auth/change-password', data)
};

// Users API
export const usersAPI = {
  list: (params) => api.get('/users', { params }),
  get: (id) => api.get(`/users/${id}`),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`)
};

// Courses API
export const coursesAPI = {
  list: (params) => api.get('/courses', { params }),
  get: (id) => api.get(`/courses/${id}`),
  create: (data) => api.post('/courses', data),
  update: (id, data) => api.put(`/courses/${id}`, data),
  delete: (id) => api.delete(`/courses/${id}`)
};

// Modules API
export const modulesAPI = {
  list: (courseId) => api.get(`/modules/courses/${courseId}/modules`),
  get: (id, courseId) => api.get(`/modules/${id}`, { params: { courseId } }),
  create: (courseId, data) => api.post(`/modules/courses/${courseId}/modules`, data),
  update: (id, data) => api.put(`/modules/${id}`, data),
  delete: (id, courseId) => api.delete(`/modules/${id}`, { params: { courseId } })
};

// Enrollments API
export const enrollmentsAPI = {
  create: (data) => api.post('/enrollments', data),
  list: (params) => api.get('/enrollments', { params }),
  delete: (id) => api.delete(`/enrollments/${id}`)
};

// Progress API
export const progressAPI = {
  create: (data) => api.post('/progress', data),
  list: (params) => api.get('/progress', { params }),
  markComplete: (data) => api.post('/progress/complete', data),
  getStats: (courseId) => api.get('/progress/stats', { params: { courseId } })
};

// Upload API
export const uploadAPI = {
  upload: (file, folderPath = '') => {
    const formData = new FormData();
    formData.append('file', file);
    if (folderPath) {
      formData.append('folderPath', folderPath);
    }
    return api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }
};

// Admin API
export const adminAPI = {
  addStudent: (data) => api.post('/admin/students', data),
  addInstructor: (data) => api.post('/admin/instructors', data),
  listSpecializations: () => api.get('/admin/specializations'),
  createSpecialization: (data) => api.post('/admin/specializations', data),
  updateSpecialization: (id, data) => api.put(`/admin/specializations/${id}`, data),
  deleteSpecialization: (id) => api.delete(`/admin/specializations/${id}`),
  getCoursesBySpecialization: (specializationId) => api.get(`/admin/specializations/${specializationId}/courses`),
  createCourse: (data) => api.post('/admin/courses', data),
  updateCourseInstructor: (courseId, instructorId) => api.put(`/admin/courses/${courseId}/instructor`, { instructorId }),
  seedCourses: () => api.post('/admin/seed-courses'),
  listUsers: (params) => api.get('/admin/users', { params }),
  changeUserPassword: (userId, data) => api.put(`/admin/users/${userId}/password`, data)
};

export default api;

