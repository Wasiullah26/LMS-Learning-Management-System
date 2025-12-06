import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../utils/auth';

const Navbar = () => {
  const navigate = useNavigate();
  const isAuthenticated = authService.isAuthenticated();
  const user = authService.getUser();
  const isAdmin = authService.isAdmin();

  const handleLogout = () => {
    authService.clearAuth();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>
          LMS
        </Link>
      </div>
      <div className="navbar-links">
        {isAuthenticated ? (
          <>
            <Link to="/dashboard">Dashboard</Link>
            {!isAdmin && <Link to="/courses">My Courses</Link>}
            <Link to="/change-password">Change Password</Link>
            <span style={{ color: 'white' }}>Welcome, {user?.name}</span>
            <button onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;

