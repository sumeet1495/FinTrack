import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid'; // For generating reference_number
import { FaSignOutAlt } from 'react-icons/fa'; // Importing the logout icon
import './CreateTransaction.css'; // Import the CSS file for styling

/*
 * CreateTransaction component allows users to create a new transaction by selecting payer/payee accounts,
 * entering an amount, providing consent, and handling form submission with API interaction.
 */
function CreateTransaction() {
  const [purpose, setPurpose] = useState(''); // Purpose of the transaction
  const [payerAccount, setPayerAccount] = useState(''); // Selected payer account
  const [payeeAccount, setPayeeAccount] = useState(''); // Selected payee account
  const [amount, setAmount] = useState(''); // Transaction amount
  const [consent, setConsent] = useState(false); // Checkbox for consent
  const [responseMessage, setResponseMessage] = useState(''); // Message displayed on form submission
  const [isError, setIsError] = useState(false); // Tracks error state
  const [accounts, setAccounts] = useState([]); // User's account list
  const [isSubmitting, setIsSubmitting] = useState(false); // Disable submit after first attempt
  const navigate = useNavigate(); // Hook for programmatic navigation

  /*
   * Fetches the user's accounts from the API and sets the accounts state.
   * Redirects to login page if no token is found.
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
            'Authorization': `Bearer ${token}`,
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
   * Handles the submission of the transaction form.
   * Validates the user's consent and sends the transaction data to the API.
   */
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!consent) {
      setResponseMessage('Please provide consent to create the transaction.');
      setIsError(true);
      return;
    }

    setIsSubmitting(true); // Disable submit button after the first attempt

    const reference_number = uuidv4(); // Generate a UUID for reference_number
    const token = localStorage.getItem('token'); // Get the token from local storage

    if (!token) {
      setResponseMessage('Authentication error: No token found. Please log in again.');
      setIsError(true);
      navigate('/login'); // Redirect to login if no token
      return;
    }

    try {
      const response = await axios.post(
        'http://127.0.0.1:8002/apis/create/transaction',
        {
          reference_number,
          purpose,
          payee_account_urn: payeeAccount,
          payer_account_urn: payerAccount,
          amount: parseFloat(amount), // Convert amount to float
          consent,
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`, // Add the token in Authorization header
          },
        }
      );

      if (response.status === 200) {
        setResponseMessage('Transaction created successfully! Refreshing the page...');
        setIsError(false);

        setTimeout(() => {
          window.location.reload(); // Refreshing the current view after 2 seconds
        }, 2000);
      }
    } catch (error) {
      if (error.response && error.response.data) {
        setResponseMessage(error.response.data.response_message || 'Transaction creation failed.');
      } else {
        setResponseMessage('An unexpected error occurred.');
      }
      setIsError(true);
      setIsSubmitting(true); // Keep the button disabled after error
    }
  };

  /*
   * Handles the logout functionality, making an API call to log the user out.
   * Redirects to login on successful logout.
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

  /*
   * Handles the input change for the purpose field, restricting it to 30 characters.
   */
  const handlePurposeChange = (e) => {
    const value = e.target.value;
    if (value.length <= 30) {
      setPurpose(value); // Only set value if it's 30 characters or less
    }
  };

  return (
    <div className="create-transaction-container">
      <div className="header-container">
        <img src="/fintrack-logo.png" alt="FinTrack Logo" className="logo" />
        <h2>Create Transaction</h2>
      </div>

      {/* Form for creating a new transaction */}
      <form onSubmit={handleSubmit}>
        <div className="payer-container">
          <input
            list="payer-accounts"
            placeholder="Select or enter payer account"
            value={payerAccount}
            onChange={(e) => setPayerAccount(e.target.value)}
          />
          <datalist id="payer-accounts">
            {accounts.map((account) => (
              <option key={account.account_urn} value={account.account_urn}>
                {account.name} ({account.account_urn})
              </option>
            ))}
          </datalist>
        </div>

        <div className="payee-container">
          <input
            list="payee-accounts"
            placeholder="Select or enter payee account"
            value={payeeAccount}
            onChange={(e) => setPayeeAccount(e.target.value)}
          />
          <datalist id="payee-accounts">
            {accounts.map((account) => (
              <option key={account.account_urn} value={account.account_urn}>
                {account.name} ({account.account_urn})
              </option>
            ))}
          </datalist>
        </div>

        <input
          type="text"
          placeholder="Purpose (e.g., for purchasing books)"
          value={purpose}
          onChange={handlePurposeChange} // Restrict input to 30 characters
          required
        />

        <input
          type="number"
          placeholder="Amount"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
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
          <label htmlFor="consent">I consent to the creation of this transaction.</label>
        </div>

        {/* Response message */}
        {responseMessage && (
          <p className={`response-message ${isError ? 'error-message' : 'success-message'}`}>
            {responseMessage}
          </p>
        )}

        {/* Submit button, disabled if no consent or during submission */}
        <button
          type="submit"
          className={consent && !isSubmitting ? "create-transaction-btn active" : "create-transaction-btn disabled"}
          disabled={!consent || isSubmitting} // Disable after first submit or when submitting
        >
          Create Transaction
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

export default CreateTransaction;
