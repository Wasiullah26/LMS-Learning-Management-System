/**
 * RTK Query API slice for all API endpoints
 */

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { authService } from '../utils/auth';

// Use relative path since Flask serves both frontend and API
// This works for both development (with proxy) and production (same origin)
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const baseQuery = fetchBaseQuery({
  baseUrl: API_BASE_URL,
  prepareHeaders: (headers) => {
    const token = authService.getToken();
    if (token) {
      headers.set('authorization', `Bearer ${token}`);
    }
    headers.set('Content-Type', 'application/json');
    return headers;
  },
});

const baseQueryWithReauth = async (args, api, extraOptions) => {
  let result = await baseQuery(args, api, extraOptions);
  if (result.error && result.error.status === 401) {
    // Don't redirect if this is a login request - let the login component handle the error
    const url = typeof args === 'string' ? args : args.url || '';
    const isLoginRequest = url.includes('/auth/login');
    
    if (!isLoginRequest) {
      authService.clearAuth();
      window.location.href = '/login';
    }
  }
  return result;
};

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['User', 'Course', 'Module', 'Enrollment', 'Progress', 'Specialization', 'Admin'],
  endpoints: (builder) => ({
    // Auth endpoints
    login: builder.mutation({
      query: (credentials) => ({
        url: '/auth/login',
        method: 'POST',
        body: credentials,
      }),
    }),
    register: builder.mutation({
      query: (data) => ({
        url: '/auth/register',
        method: 'POST',
        body: data,
      }),
    }),
    changePassword: builder.mutation({
      query: (data) => ({
        url: '/auth/change-password',
        method: 'POST',
        body: data,
      }),
    }),

    // Courses endpoints
    getCourses: builder.query({
      query: (params = {}) => ({
        url: '/courses',
        params,
      }),
      providesTags: (result, _error, arg) => {
        // Make cache key user-specific by including user ID or instructor ID in tags
        const userId = authService.getUser()?.userId;
        const instructorId = arg?.instructorId;
        const cacheKey = instructorId ? `instructor-${instructorId}` : userId ? `user-${userId}` : 'all';
        return [
          { type: 'Course', id: cacheKey },
          ...(result?.courses || []).map(c => ({ 
            type: 'Course', 
            id: `${cacheKey}-${c.courseId}` 
          }))
        ];
      },
      // Don't keep unused data to prevent cross-user cache issues
      keepUnusedDataFor: 0,
    }),
    getCourse: builder.query({
      query: (id) => `/courses/${id}`,
      providesTags: (result, error, id) => [{ type: 'Course', id }],
    }),
    createCourse: builder.mutation({
      query: (data) => ({
        url: '/courses',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Course'],
    }),
    updateCourse: builder.mutation({
      query: ({ id, ...data }) => ({
        url: `/courses/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Course', id }],
    }),
    deleteCourse: builder.mutation({
      query: (id) => ({
        url: `/courses/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Course'],
    }),
    adminDeleteCourse: builder.mutation({
      query: (courseId) => ({
        url: `/admin/courses/${courseId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Course', 'Specialization'],
    }),

    // Modules endpoints
    getModules: builder.query({
      query: (courseId) => `/modules/courses/${courseId}/modules`,
      providesTags: (result, error, courseId) => [{ type: 'Module', id: courseId }],
    }),
    getModule: builder.query({
      query: ({ id, courseId }) => ({
        url: `/modules/${id}`,
        params: { courseId },
      }),
      providesTags: (result, error, { id }) => [{ type: 'Module', id }],
    }),
    createModule: builder.mutation({
      query: ({ courseId, ...data }) => ({
        url: `/modules/courses/${courseId}/modules`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: (result, error, { courseId }) => [{ type: 'Module', id: courseId }],
    }),
    updateModule: builder.mutation({
      query: ({ id, ...data }) => ({
        url: `/modules/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Module', id }],
    }),
    deleteModule: builder.mutation({
      query: ({ id, courseId }) => ({
        url: `/modules/${id}`,
        method: 'DELETE',
        params: { courseId },
      }),
      invalidatesTags: (result, error, { courseId }) => [{ type: 'Module', id: courseId }],
    }),

    // Enrollments endpoints
    createEnrollment: builder.mutation({
      query: (data) => ({
        url: '/enrollments',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Enrollment', 'Course'],
    }),
    getEnrollments: builder.query({
      query: (params = {}) => ({
        url: '/enrollments',
        params,
      }),
      providesTags: (result) => {
        // Make cache key user-specific by including user ID in tags
        const userId = authService.getUser()?.userId;
        return [
          { type: 'Enrollment', id: 'LIST' },
          ...(result?.enrollments || []).map(e => ({ 
            type: 'Enrollment', 
            id: `${userId}-${e.enrollmentId}` 
          }))
        ];
      },
      // Don't keep unused data to prevent cross-user cache issues
      keepUnusedDataFor: 0,
    }),
    deleteEnrollment: builder.mutation({
      query: (id) => ({
        url: `/enrollments/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Enrollment'],
    }),

    // Progress endpoints
    createProgress: builder.mutation({
      query: (data) => ({
        url: '/progress',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Progress'],
    }),
    getProgress: builder.query({
      query: (params = {}) => ({
        url: '/progress',
        params,
      }),
      providesTags: (result, _error, arg) => {
        // Make cache key user-specific by including user ID in tags
        const userId = authService.getUser()?.userId;
        const courseId = arg?.courseId || 'ALL';
        return [
          { type: 'Progress', id: `${userId}-${courseId}` },
          ...(result?.progress || []).map(p => ({ 
            type: 'Progress', 
            id: `${userId}-${p.progressId}` 
          }))
        ];
      },
      // Don't keep unused data to prevent cross-user cache issues
      keepUnusedDataFor: 0,
    }),
    markProgressComplete: builder.mutation({
      query: (data) => ({
        url: '/progress/complete',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Progress'],
    }),
    getProgressStats: builder.query({
      query: (courseId) => ({
        url: '/progress/stats',
        params: { courseId },
      }),
      providesTags: ['Progress'],
    }),

    // Upload endpoint
    uploadFile: builder.mutation({
      query: ({ file, folderPath = '' }) => {
        const formData = new FormData();
        formData.append('file', file);
        if (folderPath) {
          formData.append('folderPath', folderPath);
        }
        return {
          url: '/upload',
          method: 'POST',
          body: formData,
        };
      },
    }),

    // Admin endpoints
    addStudent: builder.mutation({
      query: (data) => ({
        url: '/admin/students',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['User', 'Admin'],
    }),
    addInstructor: builder.mutation({
      query: (data) => ({
        url: '/admin/instructors',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['User', 'Admin', 'Course'],
    }),
    getSpecializations: builder.query({
      query: () => '/admin/specializations',
      providesTags: ['Specialization'],
    }),
    createSpecialization: builder.mutation({
      query: (data) => ({
        url: '/admin/specializations',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Specialization'],
    }),
    updateSpecialization: builder.mutation({
      query: ({ id, ...data }) => ({
        url: `/admin/specializations/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['Specialization'],
    }),
    deleteSpecialization: builder.mutation({
      query: (id) => ({
        url: `/admin/specializations/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Specialization'],
    }),
    getCoursesBySpecialization: builder.query({
      query: (specializationId) => `/admin/specializations/${specializationId}/courses`,
      providesTags: (result, error, specializationId) => [{ type: 'Course', id: specializationId }],
    }),
    adminCreateCourse: builder.mutation({
      query: (data) => ({
        url: '/admin/courses',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Course', 'Specialization'],
    }),
    updateCourseInstructor: builder.mutation({
      query: ({ courseId, instructorId }) => ({
        url: `/admin/courses/${courseId}/instructor`,
        method: 'PUT',
        body: { instructorId },
      }),
      invalidatesTags: ['Course', 'User', 'Admin'],
    }),
    seedCourses: builder.mutation({
      query: () => ({
        url: '/admin/seed-courses',
        method: 'POST',
      }),
      invalidatesTags: ['Course', 'User', 'Specialization'],
    }),
    getUsers: builder.query({
      query: (params = {}) => ({
        url: '/admin/users',
        params,
      }),
      providesTags: ['User', 'Admin'],
    }),
    changeUserPassword: builder.mutation({
      query: ({ userId, ...data }) => ({
        url: `/admin/users/${userId}/password`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['User'],
    }),
  }),
});

export const {
  useLoginMutation,
  useRegisterMutation,
  useChangePasswordMutation,
  useGetCoursesQuery,
  useGetCourseQuery,
  useCreateCourseMutation,
  useUpdateCourseMutation,
  useDeleteCourseMutation,
  useGetModulesQuery,
  useGetModuleQuery,
  useCreateModuleMutation,
  useUpdateModuleMutation,
  useDeleteModuleMutation,
  useCreateEnrollmentMutation,
  useGetEnrollmentsQuery,
  useDeleteEnrollmentMutation,
  useCreateProgressMutation,
  useGetProgressQuery,
  useMarkProgressCompleteMutation,
  useGetProgressStatsQuery,
  useUploadFileMutation,
  useAddStudentMutation,
  useAddInstructorMutation,
  useGetSpecializationsQuery,
  useCreateSpecializationMutation,
  useUpdateSpecializationMutation,
  useDeleteSpecializationMutation,
  useGetCoursesBySpecializationQuery,
  useAdminCreateCourseMutation,
  useAdminDeleteCourseMutation,
  useUpdateCourseInstructorMutation,
  useSeedCoursesMutation,
  useGetUsersQuery,
  useChangeUserPasswordMutation,
} = apiSlice;

