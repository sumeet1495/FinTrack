// Importing required dependencies and components
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login'; // Login component
import Register from './components/Register'; // Register component
import Home from './components/Home'; // Home component
import CreateAccount from './components/CreateAccount'; // CreateAccount component
import CreateTransaction from './components/CreateTransaction'; // CreateTransaction component
import FetchAccount from './components/FetchAccount'; // FetchAccount component
import AccountDetails from './components/AccountDetails'; // AccountDetails component
import FetchStatement from './components/FetchStatement'; // FetchStatement component
import StatementDetails from './components/StatementDetails'; // StatementDetails component
import ViewReport from './components/ViewReport'; // Import the ViewReport component
import ProtectedRoute from './components/ProtectedRoute'; // ProtectedRoute component for route protection

/*
 * App component defines the routing structure of the application.
 * It uses React Router to specify different paths and their corresponding components.
 * Certain routes are protected, requiring authentication to access.
 */
function App() {
  return (
    <Router>
      <Routes>
        {/* Redirect the root path to the Register page */}
        <Route path="/" element={<Navigate to="/register" />} />

        {/* Register page route */}
        <Route path="/register" element={<Register />} />

        {/* Login page route */}
        <Route path="/login" element={<Login />} />

        {/* Protected route for Home component */}
        <Route
          path="/home"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />

        {/* Protected route for CreateAccount component */}
        <Route
          path="/create-account"
          element={
            <ProtectedRoute>
              <CreateAccount />
            </ProtectedRoute>
          }
        />

        {/* Protected route for CreateTransaction component */}
        <Route
          path="/create-transaction"
          element={
            <ProtectedRoute>
              <CreateTransaction />
            </ProtectedRoute>
          }
        />

        {/* Protected route for FetchAccount component */}
        <Route
          path="/fetch-account"
          element={
            <ProtectedRoute>
              <FetchAccount />
            </ProtectedRoute>
          }
        />

        {/* Protected route for AccountDetails component */}
        <Route
          path="/account-details"
          element={
            <ProtectedRoute>
              <AccountDetails />
            </ProtectedRoute>
          }
        />

        {/* Protected route for FetchStatement component */}
        <Route
          path="/fetch-statement"
          element={
            <ProtectedRoute>
              <FetchStatement />
            </ProtectedRoute>
          }
        />

        {/* Protected route for StatementDetails component */}
        <Route
          path="/statement-details"
          element={
            <ProtectedRoute>
              <StatementDetails />
            </ProtectedRoute>
          }
        />

        {/* Protected route for ViewReport component */}
        <Route
          path="/view-report"
          element={
            <ProtectedRoute>
              <ViewReport />
            </ProtectedRoute>
          }
        />

        {/* Fallback route to handle undefined paths redirecting to Register */}
        <Route path="*" element={<Navigate to="/register" />} />
      </Routes>
    </Router>
  );
}

export default App; // Exporting the App component as the default export
