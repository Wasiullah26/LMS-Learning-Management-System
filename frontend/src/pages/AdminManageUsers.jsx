import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGetUsersQuery } from '../services/apiSlice';
import { toast } from '../utils/toast';

const AdminManageUsers = () => {
  const navigate = useNavigate();
  const [filter, setFilter] = useState('all');

  const params = filter !== 'all' ? { role: filter } : {};
  const { data, isLoading, error } = useGetUsersQuery(params);

  const allUsers = data?.users || [];

  if (error) {
    toast.error('Failed to load users');
  }



  const admins = allUsers.filter(u => u.role === 'admin');
  const instructors = allUsers.filter(u => u.role === 'instructor');
  const students = allUsers.filter(u => u.role === 'student');

  const renderTable = (users, title, showSpecialization = true, showCourses = false) => {
    if (users.length === 0) {
    return (
      <div className="users-table-container">
        <div className="users-table-header">
          <h2>{title}</h2>
        </div>
        <div style={{ padding: '3rem', textAlign: 'center' }}>
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ color: '#bdc3c7', marginBottom: '1rem' }}>
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          <p style={{ color: '#7f8c8d', fontSize: '1.1rem' }}>
            No {title.toLowerCase()} found
          </p>
        </div>
      </div>
    );
    }

    return (
      <div className="users-table-container">
        <div className="users-table-header">
          <h2>
            {title}
            <span className="users-count-badge">{users.length}</span>
          </h2>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="users-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                {showSpecialization && <th>Specialization</th>}
                {showCourses && <th>Courses</th>}
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.userId}>
                  <td>{user.name}</td>
                  <td>{user.email}</td>
                  {showSpecialization && (
                    <td>{user.specializationName || '-'}</td>
                  )}
                  {showCourses && (
                    <td>
                      {user.courseTitles && user.courseTitles.length > 0 ? (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                          {user.courseTitles.map((title, idx) => (
                            <span key={idx} className="course-badge">
                              {title}
                            </span>
                          ))}
                        </div>
                      ) : (
                        '-'
                      )}
                    </td>
                  )}
                  <td>{new Date(user.createdAt).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-loading">
          <div className="spinner-large"></div>
          <p>Loading users...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <button onClick={() => navigate(-1)} className="back-button">←</button>
        <div className="page-header-content" style={{ flex: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 className="page-title">All Users</h1>
            <p className="page-subtitle">View and manage all users in the system</p>
          </div>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="form-group"
            style={{
              padding: '0.75rem 1rem',
              fontSize: '1rem',
              borderRadius: '8px',
              border: '2px solid #e0e0e0',
              background: 'white',
              cursor: 'pointer',
              minWidth: '180px'
            }}
          >
            <option value="all">All Users</option>
            <option value="student">Students</option>
            <option value="instructor">Instructors</option>
            <option value="admin">Admins</option>
          </select>
        </div>
      </div>

      {filter === 'all' ? (
        <>
          {renderTable(admins, 'Admins', false, false)}
          {renderTable(instructors, 'Faculties (Instructors)', true, true)}
          {renderTable(students, 'Students', true, false)}
        </>
      ) : filter === 'instructor' ? (
        renderTable(instructors, 'Faculties (Instructors)', true, true)
      ) : filter === 'student' ? (
        renderTable(students, 'Students', true, false)
      ) : filter === 'admin' ? (
        renderTable(admins, 'Admins', false, false)
      ) : null}
    </div>
  );
};

export default AdminManageUsers;
