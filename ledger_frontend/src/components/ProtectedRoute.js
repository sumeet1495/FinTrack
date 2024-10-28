// src/components/ProtectedRoute.js
import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  // checking if the user is authenticated (e.g. by checking a token in localStorage)
  const isAuthenticated = !!localStorage.getItem('token'); //  token in localStorage after login

  // if the user is not authenticated, redirect to the login page
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // if the user is authenticated, allow access to the protected route
  return children;
};

export default ProtectedRoute;
