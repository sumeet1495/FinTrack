import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid'; // For generating reference_number
import { FaSignOutAlt } from 'react-icons/fa'; // Importing the logout icon
import './CreateAccount.css'; // Import the CSS file for styling

/*
 * The CreateAccount component handles the form for creating a new account.
 * It manages form input states, submits account details to an API, and handles logout functionality.
 */
function CreateAccount() {
  const [accountName, setAccountName] = useState(''); // State for account name input
  const [purpose, setPurpose] = useState(''); // State for purpose input
  const [currencyCode, setCurrencyCode] = useState('NZD'); // Default value is 'NZD'
  const [consent, setConsent] = useState(false); // State for managing user consent checkbox
  const [responseMessage, setResponseMessage] = useState(''); // State for API response messages
  const [isError, setIsError] = useState(false); // State for error handling in the UI
  const navigate = useNavigate(); // Used for navigation

  // Array of currency options to be displayed in the dropdown
  const currencies = [
    { name: 'United States Dollar', code: 'USD' },
    { name: 'Euro', code: 'EUR' },
    { name: 'British Pound Sterling', code: 'GBP' },
    { name: 'Indian Rupee', code: 'INR' },
    { name: 'Japanese Yen', code: 'JPY' },
    { name: 'Australian Dollar', code: 'AUD' },
    { name: 'New Zealand Dollar', code: 'NZD' },
    { name: 'Canadian Dollar', code: 'CAD' },
  ];

  /*
   * handleAccountNameChange ensures that only alphabetic characters and spaces are accepted
   * for the account name input.
   */
  const handleAccountNameChange = (e) => {
    const input = e.target.value;
    const regex = /^[A-Za-z\s]*$/; // Regex to allow only alphabetic characters and spaces
    if (regex.test(input)) {
      setAccountName(input); // Only update state if input is valid
    }
  };

  /*
   * handleSubmit submits the form data for creating a new account.
   * It includes consent validation, API call for account creation, and error handling.
   */
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!consent) {
      setResponseMessage('Please provide consent to create the account.');
      setIsError(true);
      return;
    }

    const reference_number = uuidv4(); // Generate a UUID for reference_number
    const token = localStorage.getItem('token'); // Get the token from local storage

    if (!token) {
      setResponseMessage('Authentication error: No token found. Please log in again.');
      setIsError(true);
      navigate('/login'); // Redirect to login if no token
      return;
    }

    try {
      // Make a POST request to the API for account creation
      const response = await axios.post(
        'http://127.0.0.1:8002/apis/create/account',
        {
          reference_number,
          account_name: accountName,
          purpose,
          currency_code: currencyCode, // Use the selected currency code
          consent,
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`, // Add the token in Authorization header
          },
        }
      );

      // Handle success response
      if (response.status === 200) {
        setResponseMessage('Account created successfully! Redirecting to home...');
        setIsError(false);
        setTimeout(() => {
          navigate('/home'); // Redirect to home page after success
        }, 2000);
      }
    } catch (error) {
      // Handle error response
      if (error.response && error.response.data) {
        setResponseMessage(error.response.data.response_message || 'Account creation failed.');
      } else {
        setResponseMessage('An unexpected error occurred.');
      }
      setIsError(true);
    }
  };

  /*
   * handleLogout handles user logout by calling the logout API endpoint
   * and managing the state and navigation upon success or error.
   */
  const handleLogout = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setResponseMessage('No token found, redirecting to login.');
      setIsError(true);
      navigate('/login', { replace: true });
      return;
    }

    const reference_number = uuidv4(); // Generate UUID for logout request

    try {
      // Make a POST request to the API to log the user out
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

      // Handle successful logout
      if (response.status === 200 && response.data.status === "SUCCESS") {
        setResponseMessage(response.data.response_message);
        setIsError(false);
        localStorage.removeItem('token'); // Remove token from local storage

        setTimeout(() => {
          navigate('/login', { replace: true });
        }, 2000);
      } else {
        throw new Error('Unexpected response format.');
      }
    } catch (error) {
      // Handle error during logout
      console.error('Logout error:', error);

      if (error.response && error.response.data && error.response.data.response_message) {
        setResponseMessage(error.response.data.response_message);
        setIsError(true);
      } else if (error.message) {
        setResponseMessage(`Logout failed: ${error.message}`);
        setIsError(true);
      } else {
        setResponseMessage('Logout failed: An unexpected error occurred.');
        setIsError(true);
      }

      setTimeout(() => {
        navigate('/login', { replace: true });
      }, 2000);
    }
  };

  return (
    <div className="create-account-container">
      {/* Header section with logo and title */}
      <div className="header-container">
        <img src="/fintrack-logo.png" alt="FinTrack Logo" className="logo" />
        <h2>Create Account</h2>
      </div>

      {/* Form for account creation */}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Account Name"
          value={accountName}
          onChange={handleAccountNameChange}
          required
        />
        <input
          type="text"
          placeholder="Purpose (e.g., Funds Transfer)"
          value={purpose}
          onChange={(e) => setPurpose(e.target.value)}
          required
        />

        {/* Currency selection dropdown */}
        <select className="currency-select" value={currencyCode} onChange={(e) => setCurrencyCode(e.target.value)} required>
          {currencies.map((currency) => (
            <option key={currency.code} value={currency.code}>
              {currency.name} ({currency.code})
            </option>
          ))}
        </select>

        {/* Consent checkbox */}
        <div className="consent-container">
          <input
            type="checkbox"
            id="consent"
            checked={consent}
            onChange={() => setConsent(!consent)}
          />
          <label htmlFor="consent">I consent to the creation of this account.</label>
        </div>

        {/* Display response message */}
        {responseMessage && (
          <p className={`response-message ${isError ? 'error-message' : 'success-message'}`}>
            {responseMessage}
          </p>
        )}

        {/* Create account button, enabled only if consent is given */}
        <button type="submit" className={consent ? "create-account-btn active" : "create-account-btn disabled"} disabled={!consent}>
          Create Account
        </button>
      </form>

      {/* Navigation buttons for going back to home and logging out */}
      <button className="home-button" onClick={() => navigate('/home')}>
        Back to Home
      </button>

      <button className="logout-button" onClick={handleLogout}>
        <FaSignOutAlt /> Logout
      </button>
    </div>
  );
}

export default CreateAccount;
