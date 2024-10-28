import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid'; // For generating reference_number
import { FaSignOutAlt } from 'react-icons/fa'; // Importing the logout icon
import './Home.css'; // Import the CSS file for styling

/*
 * The Home component serves as the main dashboard where users can navigate to different sections
 * such as creating accounts, creating transactions, fetching account details, and fetching statements.
 * It also provides a logout functionality.
 */
function Home() {
  const [message, setMessage] = useState(''); // State to store response messages (success/error)
  const [isError, setIsError] = useState(false); // Tracks error state
  const navigate = useNavigate(); // Hook for programmatic navigation

  /*
   * useEffect hook checks if a token is present in local storage when the component mounts.
   * If no token is found, it redirects the user to the login page.
   */
  useEffect(() => {
    const token = localStorage.getItem('token');

    if (!token) {
      navigate('/login', { replace: true }); // Redirect to login if no token
    }
  }, [navigate]);

  /*
   * handleLogout function logs the user out by making an API call.
   * It removes the token from local storage and redirects the user to the login page on success.
   */
  const handleLogout = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setMessage('No token found, redirecting to login.');
      setIsError(true);
      navigate('/login', { replace: true });
      return;
    }

    const reference_number = uuidv4(); // Generate a UUID for reference_number

    try {
      const response = await axios.post(
        'http://127.0.0.1:8002/user/logout',
        { reference_number },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.status === 200 && response.data.status === "SUCCESS") {
        setIsError(false);
        localStorage.removeItem('token'); // Remove token from local storage
        setTimeout(() => {
          navigate('/login', { replace: true }); // Redirect to login page
        }, 2000);
      } else {
        throw new Error('Unexpected response format.');
      }
    } catch (error) {
      console.error('Logout error:', error);

      if (error.response && error.response.data && error.response.data.response_message) {
        setMessage(error.response.data.response_message);
        setIsError(true);
      } else if (error.message) {
        setMessage(`Logout failed: ${error.message}`);
        setIsError(true);
      } else {
        setMessage('Logout failed: An unexpected error occurred.');
        setIsError(true);
      }

      setTimeout(() => {
        navigate('/login', { replace: true }); // Redirect to login page on error
      }, 2000);
    }
  };

  return (
    <div className="home-container">
      {/* Header section with logo and welcome message */}
      <div className="header-container">
        <img src="/fintrack-logo.png" alt="FinTrack Logo" className="home-logo" />
        <h1>Welcome to FinTrack</h1>
        <p>Manage your accounts, transactions, and more.</p>
      </div>

      {/* Create buttons section for account and transaction creation */}
      <div className="create-buttons-group">
        <button className="action-button" onClick={() => navigate('/create-account')}>
          Create Account
        </button>
        <button className="action-button" onClick={() => navigate('/create-transaction')}>
          Create Transaction
        </button>
      </div>

      {/* Fetch buttons section for fetching account and statement details */}
      <div className="fetch-buttons-group">
        <button className="action-button" onClick={() => navigate('/fetch-account')}>
          Fetch Account
        </button>
        <button className="action-button" onClick={() => navigate('/fetch-statement')}>
          Fetch Statement
        </button>
      </div>

      {/* Display success or error message */}
      {message && (
        <p className={`message ${isError ? 'error-message' : 'success-message'}`}>
          {message}
        </p>
      )}

      {/* Logout button at the bottom */}
      <button className="logout-button-bottom" onClick={handleLogout}>
        <FaSignOutAlt /> Logout
      </button>
    </div>
  );
}

export default Home;
