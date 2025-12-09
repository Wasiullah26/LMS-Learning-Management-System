import React from 'react';
import { Link } from 'react-router-dom';
import { authService } from '../utils/auth';

const AdminDashboard = () => {
  const userName = authService.getUser()?.name || 'Admin';

  const adminCards = [
    {
      title: 'Add Student',
      description: 'Create a new student account and assign them to a specialization.',
      link: '/admin/add-student',
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
        </svg>
      ),
      color: '#3498db'
    },
    {
      title: 'Add Instructor',
      description: 'Create a new instructor account and assign them to courses.',
      link: '/admin/add-instructor',
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
        </svg>
      ),
      color: '#9b59b6'
    },
    {
      title: 'Manage Specializations',
      description: 'View, create, edit, and delete specializations and their courses.',
      link: '/admin/specializations',
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
          <path d="M2 17L12 22L22 17"/>
          <path d="M2 12L12 17L22 12"/>
        </svg>
      ),
      color: '#e67e22'
    },
    {
      title: 'All Users',
      description: 'View and manage all users in the system.',
      link: '/admin/users',
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
        </svg>
      ),
      color: '#27ae60'
    }
  ];

  return (
    <div className="dashboard-container">
      {/* Welcome Header */}
      <div className="dashboard-header" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
        <div className="dashboard-header-content">
          <div>
            <h1 className="dashboard-title">Admin Dashboard</h1>
            <p className="dashboard-subtitle">Welcome, {userName}! Manage your learning management system</p>
          </div>
          <div className="dashboard-header-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
          </div>
        </div>
      </div>

      {/* Admin Actions */}
      <div className="dashboard-section">
        <h2 style={{ marginBottom: '1.5rem', fontSize: '1.5rem', fontWeight: '600', color: '#2c3e50' }}>
          Quick Actions
        </h2>
        <div className="admin-cards-grid">
          {adminCards.map((card, index) => (
            <Link
              key={index}
              to={card.link}
              className="admin-card"
              style={{ textDecoration: 'none', color: 'inherit' }}
            >
              <div className="admin-card-icon" style={{ backgroundColor: `${card.color}15`, color: card.color }}>
                {card.icon}
              </div>
              <h3 className="admin-card-title">{card.title}</h3>
              <p className="admin-card-description">{card.description}</p>
              <div className="admin-card-arrow">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="9 18 15 12 9 6"/>
                </svg>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;

