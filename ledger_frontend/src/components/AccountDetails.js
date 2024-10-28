import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios'; // Importing axios for the API call
import { v4 as uuidv4 } from 'uuid'; // For generating reference_number
import { FaSignOutAlt } from 'react-icons/fa'; // Importing the logout icon
import './AccountDetails.css'; // Import the CSS file for styling

/*
 * The AccountDetails component displays account information, handles user logout, and includes navigation options.
 * It retrieves data passed from another page and displays account details such as name, account URN, and balances.
 * It also provides a logout function that interacts with an API, handles errors, and navigates back to the login page.
 */
function AccountDetails() {
  const location = useLocation();
  const navigate = useNavigate();
  const { data } = location.state || {}; // Access the data passed from the FetchAccount page

  const [logoutMessage, setLogoutMessage] = useState(''); // State for displaying logout message
  const [isError, setIsError] = useState(false); // State for tracking error status

  // Checks if account data is available. If not, displays a message indicating that no account details are available.
  if (!data) {
    return <div>No account details available.</div>;
  }

  /*
   * handleLogout is an asynchronous function that handles the logout process.
   * It retrieves the user's token from localStorage and makes a POST request to the API for logging out.
   * If successful, it navigates the user to the login page; if there is an error, it displays an error message.
   */
  const handleLogout = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setLogoutMessage('No token found, redirecting to login.');
      setIsError(true);
      setTimeout(() => {
        navigate('/login', { replace: true });
      }, 2000);
      return;
    }

    const reference_number = uuidv4();

    try {
      // Making a POST request to the logout endpoint with authorization header
      const response = await axios.post(
        'http://127.0.0.1:8002/user/logout',
        { reference_number },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      // If the logout is successful, the user is redirected to the login page
      if (response.status === 200 && response.data.status === "SUCCESS") {
        setLogoutMessage('Successfully logged out the User.');
        setIsError(false);
        localStorage.removeItem('token');

        setTimeout(() => {
          navigate('/login', { replace: true });
        }, 2000);
      } else {
        throw new Error('Unexpected response format.');
      }
    } catch (error) {
      // Handles any errors that occur during the logout process
      console.error('Logout error:', error);
      setLogoutMessage('Logout failed. Please try again.');
      setIsError(true);

      setTimeout(() => {
        navigate('/login', { replace: true });
      }, 2000);
    }
  };

  return (
    <div className="account-details-container">
      {/* Header section displaying logo and title */}
      <div className="header-container">
        <img src="/fintrack-logo.png" alt="FinTrack Logo" className="logo" />
        <h2>Account Details</h2>
      </div>

      {/* Displays the account details such as name, URN, and balances */}
      <div className="account-details">
        <h3>Account Details:</h3>
        <p><strong>Name:</strong> {data.name}</p>
        <p><strong>Account URN:</strong> {data.account_urn}</p>
        <p><strong>Currency:</strong> {data.currency}</p>
        <h4>Balances:</h4>
        <p><strong>Total Balance:</strong> {data.balances.total_balance}</p>
        <p><strong>Total Credit Balance:</strong> {data.balances.total_credit_balance}</p>
        <p><strong>Total Debit Balance:</strong> {data.balances.total_debit_balance}</p>
      </div>

      {/* Displays the logout message, either success or error based on the logout process */}
      {logoutMessage && (
        <p className={`message ${isError ? 'error-message' : 'success-message'}`}>
          {logoutMessage}
        </p>
      )}

      {/* Navigation buttons for going back, home, and logging out */}
      <button className="back-button" onClick={() => navigate(-1)}>
        Back
      </button>

      <button className="home-button" onClick={() => navigate('/home')}>
        Back to Home
      </button>

      <button className="logout-button" onClick={handleLogout}>
        <FaSignOutAlt /> Logout
      </button>
    </div>
  );
}

export default AccountDetails;