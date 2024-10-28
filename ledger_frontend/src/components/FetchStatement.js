import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid'; // For generating reference_number
import { FaSignOutAlt } from 'react-icons/fa'; // Importing the logout icon
import DatePicker from 'react-datepicker'; // Importing the DatePicker component
import 'react-datepicker/dist/react-datepicker.css'; // Importing CSS for DatePicker
import './FetchStatement.css'; // Import the CSS file for styling

/*
 * The FetchStatement component allows users to select an account, pick a date range,
 * provide consent, and fetch a financial statement. It also manages user logout functionality.
 */
function FetchStatement() {
  const [accounts, setAccounts] = useState([]); // Store fetched accounts
  const [accountURN, setAccountURN] = useState(''); // For selected account
  const [responseMessage, setResponseMessage] = useState(''); 
  const [isError, setIsError] = useState(false); 
  const [consent, setConsent] = useState(false); // Consent checkbox state
  const [purpose, setPurpose] = useState(''); // Stores the purpose of the request
  const [fromDate, setFromDate] = useState(null); // From date for statement range
  const [toDate, setToDate] = useState(null); // To date for statement range
  const [isFetchDisabled, setIsFetchDisabled] = useState(false); 
  const navigate = useNavigate(); // Hook for programmatic navigation

  /*
   * useEffect hook to fetch the user's accounts when the component mounts.
   * Retrieves token from local storage and makes an API call to get accounts.
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
          setAccounts(response.data.data.accounts); // Set accounts in state
        }
      } catch (error) {
        setResponseMessage('Failed to fetch accounts.');
        setIsError(true);
      }
    };

    fetchAccounts();
  }, [navigate]);

  /*
   * handleLogout function logs the user out by making an API call.
   * Removes the token from local storage and navigates to the login page upon success.
   */
  const handleLogout = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setResponseMessage('No token found, redirecting to login.');
      setIsError(true);
      navigate('/login');
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
        setResponseMessage(response.data.response_message);
        setIsError(false);

        // Display the message for 2 seconds before redirecting
        setTimeout(() => {
          localStorage.removeItem('token'); // Remove token from local storage
          navigate('/login'); // Navigate to login page
        }, 2000);
      } else {
        throw new Error('Unexpected response format.');
      }
    } catch (error) {
      setResponseMessage('Logout failed. Please try again.');
      setIsError(true);
    }
  };

  /*
   * handleSubmit function manages form submission for fetching statements.
   * Validates user input, sends the request to fetch the statement, and handles the response.
   */
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!consent) {
      setResponseMessage('Please provide consent to fetch the statement.');
      setIsError(true);
      return;
    }

    // Validate date range
    if (toDate && fromDate && toDate < fromDate) {
      setResponseMessage('To Date should not be earlier than From Date.');
      setIsError(true);
      setIsFetchDisabled(true); // Disable the fetch button after an error
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
      const response = await axios({
        method: 'post',
        url: 'http://127.0.0.1:8002/apis/fetch/statement',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`, // Add the token in Authorization header
        },
        data: {
          reference_number,
          purpose: purpose || 'viewing the statement', // Use default if empty
          account_urn: accountURN,
          consent,
        },
      });

      if (response.status === 200) {
        const inclusiveToDate = new Date(toDate);
        inclusiveToDate.setDate(inclusiveToDate.getDate() + 1); // Ensure 'To Date' includes the full day

        // Navigate to the statement details page with the fetched data
        navigate('/statement-details', {
          state: { data: response.data.data, fromDate, toDate: inclusiveToDate },
        });
      }
    } catch (error) {
      if (error.response && error.response.data) {
        setResponseMessage(error.response.data.response_message || 'Statement fetching failed.');
      } else {
        setResponseMessage('An unexpected error occurred.');
      }
      setIsError(true);
      setIsFetchDisabled(true); // Disable the fetch button after an error
    }
  };

  return (
    <div className="fetch-statement-container">
      {/* Header section with logo and title */}
      <div className="header-container">
        <img src="/fintrack-logo.png" alt="FinTrack Logo" className="logo" />
        <h2>Fetch Statement</h2>
      </div>

      {/* Form for selecting an account, date range, and providing consent */}
      <form onSubmit={handleSubmit}>
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
          placeholder="Purpose (e.g., viewing the statement)"
          value={purpose}
          onChange={(e) => setPurpose(e.target.value)}
          required
        />

        {/* Date range selection */}
        <div className="date-container">
          <DatePicker
            selected={fromDate}
            onChange={(date) => setFromDate(date)}
            dateFormat="yyyy-MM-dd"
            placeholderText="From Date"
            maxDate={new Date()} // Disable future dates
            required
            className="date-picker-input"
          />

          <DatePicker
            selected={toDate}
            onChange={(date) => setToDate(date)}
            dateFormat="yyyy-MM-dd"
            placeholderText="To Date"
            maxDate={new Date()} // Disable future dates
            required
            className="date-picker-input"
          />
        </div>

        {/* Consent checkbox */}
        <div className="consent-container">
          <input
            type="checkbox"
            id="consent"
            checked={consent}
            onChange={() => setConsent(!consent)}
          />
          <label htmlFor="consent">I consent to the fetching of this statement.</label>
        </div>

        {/* Display success or error message */}
        {responseMessage && (
          <p className={`response-message ${isError ? 'error-message' : 'success-message'}`}>
            {responseMessage}
          </p>
        )}

        {/* Fetch statement button */}
        <button type="submit" className={consent ? "fetch-statement-btn active" : "fetch-statement-btn disabled"} disabled={!consent || isFetchDisabled}>
          Fetch Statement
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

export default FetchStatement;
