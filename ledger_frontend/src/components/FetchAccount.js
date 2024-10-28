import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid'; // For generating reference_number
import { FaSignOutAlt } from 'react-icons/fa'; // Import the logout icon
import './FetchAccount.css'; // Import the CSS file for styling

/*
 * The FetchAccount component allows users to select an account and fetch its details.
 * It handles fetching the user's accounts, managing consent, handling form submission,
 * and navigating to the AccountDetails page upon success.
 */
function FetchAccount() {
  const [accounts, setAccounts] = useState([]); // Store fetched accounts
  const [accountURN, setAccountURN] = useState(''); // For selected account
  const [responseMessage, setResponseMessage] = useState('');
  const [isError, setIsError] = useState(false);
  const [consent, setConsent] = useState(false);
  const [purpose, setPurpose] = useState(''); // Purpose starts as empty string
  const navigate = useNavigate();

  /*
   * useEffect hook to fetch the list of user's accounts when the component mounts.
   * It retrieves the token from local storage and makes an API call to fetch accounts.
   */
  useEffect(() => {
    const fetchAccounts = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setResponseMessage('Authentication error: No token found. Please log in again.');
        setIsError(true);
        navigate('/login');
        return;
      }

      try {
        const response = await axios({
          method: 'get',
          url: 'http://127.0.0.1:8002/apis/fetch/usr-account',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`, // Add the token in Authorization header
          },
        });

        if (response.status === 200 && response.data.data) {
          setAccounts(response.data.data.accounts);
        }
      } catch (error) {
        setResponseMessage('Failed to fetch accounts.');
        setIsError(true);
      }
    };

    fetchAccounts();
  }, [navigate]);

  /*
   * handleSubmit function to handle form submission.
   * It validates consent, constructs the request data, and makes an API call to fetch account details.
   * On success, it navigates to the AccountDetails page.
   */
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!consent) {
      setResponseMessage('Please provide consent to fetch the account.');
      setIsError(true);
      return;
    }

    const reference_number = uuidv4(); // Generate a UUID for reference_number
    const token = localStorage.getItem('token');
    if (!token) {
      setResponseMessage('Authentication error: No token found. Please log in again.');
      setIsError(true);
      navigate('/login');
      return;
    }

    try {
      const response = await axios({
        method: 'post',
        url: 'http://127.0.0.1:8002/apis/fetch/account',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        data: {
          reference_number,
          purpose: purpose || 'viewing the account details', // Use default if empty
          account_urn: accountURN, // Use account URN from dropdown
          consent,
        },
      });

      if (response.status === 200) {
        navigate('/account-details', { state: { data: response.data.data } });
      }
    } catch (error) {
      if (error.response && error.response.data) {
        setResponseMessage(error.response.data.response_message || 'Account fetching failed.');
      } else {
        setResponseMessage('An unexpected error occurred.');
      }
      setIsError(true);
    }
  };

  /*
   * handleLogout function to log the user out.
   * It makes an API call to the logout endpoint and handles success or error responses.
   * On successful logout, it redirects the user to the login page.
   */
  const handleLogout = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setResponseMessage('No token found, redirecting to login.');
      setIsError(true);
      navigate('/login', { replace: true });
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

      if (response.status === 200 && response.data.status === "SUCCESS") {
        setResponseMessage(response.data.response_message);
        setIsError(false);
        localStorage.removeItem('token');

        setTimeout(() => {
          navigate('/login', { replace: true });
        }, 2000);
      } else {
        throw new Error('Unexpected response format.');
      }
    } catch (error) {
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
    <div className="fetch-account-container">
      {/* Header section with logo and title */}
      <div className="header-container">
        <img src="/fintrack-logo.png" alt="FinTrack Logo" className="logo" />
        <h2>Fetch Account</h2>
      </div>

      {/* Form for selecting an account and providing consent */}
      <form onSubmit={handleSubmit}>
        {/* Dropdown for selecting an account */}
        <select
          value={accountURN}
          onChange={(e) => setAccountURN(e.target.value)}
          required
        >
          <option value="" disabled>Select an Account</option>
          {accounts.map((account) => (
            <option key={account.account_urn} value={account.account_urn}>
              {account.name} ({account.account_urn})
            </option>
          ))}
        </select>

        <input
          type="text"
          placeholder="Purpose (e.g., viewing the account details)"
          value={purpose}
          onChange={(e) => setPurpose(e.target.value)}
          required
        />

        {/* Consent checkbox */}
        <div className="consent-container">
          <input
            type="checkbox"
            id="consent"
            checked={consent}
            onChange={() => setConsent(!consent)}
          />
          <label htmlFor="consent">I consent to the fetching of this account.</label>
        </div>

        {/* Display response message */}
        {responseMessage && (
          <p className={`response-message ${isError ? 'error-message' : 'success-message'}`}>
            {responseMessage}
          </p>
        )}

        {/* Submit button, disabled if consent is not given */}
        <button
          type="submit"
          className={consent ? "fetch-account-btn active" : "fetch-account-btn disabled"}
          disabled={!consent}
        >
          Fetch Account
        </button>
      </form>

      {/* Navigation buttons for home and logout */}
      <button className="home-button" onClick={() => navigate('/home')}>
        Back to Home
      </button>

      <button className="logout-button" onClick={handleLogout}>
        <FaSignOutAlt /> Logout
      </button>
    </div>
  );
}

export default FetchAccount;
