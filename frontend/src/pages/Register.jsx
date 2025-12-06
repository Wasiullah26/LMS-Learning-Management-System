import React from 'react';
import { Link } from 'react-router-dom';

const Register = () => {
  return (
    <div className="form-container">
      <h2>Registration</h2>
      <div className="alert alert-error" style={{ marginBottom: '1rem' }}>
        <strong>Registration is disabled</strong>
        <p style={{ marginTop: '0.5rem', marginBottom: '0' }}>
          User accounts must be created by an administrator. Please contact your administrator to create an account.
        </p>
      </div>
      <p style={{ textAlign: 'center', marginTop: '1rem' }}>
        Already have an account? <Link to="/login">Login here</Link>
      </p>
    </div>
  );
};

export default Register;

