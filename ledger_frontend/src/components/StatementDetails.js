// Import necessary modules and components
import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios'; // For making the logout API request
import { v4 as uuidv4 } from 'uuid'; // For generating the reference_number
import { FaSignOutAlt } from 'react-icons/fa'; // Importing the icon for logout
import './StatementDetails.css'; // Import the CSS file for styling

/*
 * The StatementDetails component displays filtered transaction details for a selected account.
 * It allows users to view transactions, view a report, and log out.
 */
function StatementDetails() {
  const { state } = useLocation(); // Retrieve passed state from the previous route
  const { data, fromDate, toDate } = state; // Destructure the data, fromDate, and toDate from the state
  const navigate = useNavigate(); // Hook for programmatic navigation

  // Convert from and to dates into JavaScript Date objects
  const from = new Date(fromDate);
  const to = new Date(toDate);

  const [message, setMessage] = useState(''); // State to store success/error messages
  const [isError, setIsError] = useState(false); // State to track error state

  /*
   * Filter transactions that fall within the specified date range.
   * This creates a new array with only the relevant transactions.
   */
  const filteredTransactions = data.filter(transaction => {
    const transactionDate = new Date(transaction.transaction_timestamp);
    return transactionDate >= from && transactionDate <= to;
  });

  // Use currency code from the first transaction, assuming all transactions have the same currency code
  const currencyCode = data.length > 0 ? data[0].currency_code : '';

  /*
   * Calculate total credit and debit across all transactions
   * Total balance is derived by subtracting total debits from total credits.
   */
  const totalCredit = data
    .filter(transaction => transaction.transaction_type === 'CREDIT')
    .reduce((sum, transaction) => sum + transaction.amount, 0);

  const totalDebit = data
    .filter(transaction => transaction.transaction_type === 'DEBIT')
    .reduce((sum, transaction) => sum + transaction.amount, 0);

  const totalBalance = totalCredit - totalDebit; // Calculate overall total balance

  /*
   * Calculate the total credit and debit for only the filtered transactions.
   * Filtered balance is derived by subtracting debits from credits.
   */
  const filteredCredit = filteredTransactions
    .filter(transaction => transaction.transaction_type === 'CREDIT')
    .reduce((sum, transaction) => sum + transaction.amount, 0);

  const filteredDebit = filteredTransactions
    .filter(transaction => transaction.transaction_type === 'DEBIT')
    .reduce((sum, transaction) => sum + transaction.amount, 0);

  const filteredBalance = filteredCredit - filteredDebit; // Calculate filtered total balance

  /*
   * handleLogout function handles the user logout process.
   * It sends a logout request to the API and clears the token from local storage.
   */
  const handleLogout = async () => {
    const token = localStorage.getItem('token'); // Get the token from local storage
    const reference_number = uuidv4(); // Generate a unique reference number

    if (!token) {
      setMessage('No token found, redirecting to login.'); // Handle missing token
      setIsError(true);
      setTimeout(() => {
        navigate('/login', { replace: true }); // Redirect to login after 2 seconds
      }, 2000);
      return;
    }

    try {
      // Send logout request to the backend
      const response = await axios.post(
        'http://127.0.0.1:8002/user/logout',
        { reference_number }, // Send reference_number in the body
        {
          headers: {
            'Authorization': `Bearer ${token}`, // Include token in the Authorization header
            'Content-Type': 'application/json'
          }
        }
      );

      // Handle successful logout
      if (response.status === 200 && response.data.status === "SUCCESS") {
        setMessage('Successfully logged out the User.');
        setIsError(false);
        localStorage.removeItem('token'); // Remove token from local storage
        setTimeout(() => {
          navigate('/login', { replace: true }); // Redirect to login after 2 seconds
        }, 2000);
      } else {
        throw new Error('Unexpected response format.');
      }
    } catch (error) {
      setMessage('Logout failed. Please try again.'); // Handle errors
      setIsError(true);
    }
  };

  return (
    <div className="statement-details-container">
      {/* Logo and title */}
      <img src="/fintrack-logo.png" alt="FinTrack Logo" className="statement-details-logo" />
      <h2>Statement Details</h2>

      {/* Display filtered transactions in a table, or a message if none are found */}
      {filteredTransactions.length > 0 ? (
        <div className="table-container">
          <table className="transaction-table">
            <thead>
              <tr>
                <th>Transaction URN</th>
                <th>Payer URN</th>
                <th>Payer Name</th> 
                <th>Payee URN</th>
                <th>Payee Name</th>
                <th>Amount</th>
                <th>Purpose</th> {/* Column for Purpose */}
                <th>Type</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {filteredTransactions.map((transaction, index) => (
                <tr key={index}>
                  <td>{transaction.transaction_urn}</td>
                  <td>{transaction.payer_account_urn}</td>
                  <td>{transaction.payer_account_name}</td> 
                  <td>{transaction.payee_account_urn}</td>
                  <td>{transaction.payee_account_name}</td> 
                  <td>{transaction.amount}</td>
                  <td>{transaction.purpose ? transaction.purpose.slice(0, 30) : ''}</td> {/* Limit purpose to 30 characters */}
                  <td>{transaction.transaction_type}</td>
                  <td>{transaction.transaction_timestamp}</td>
                </tr>
              ))}
              {/* Total Balance for filtered transactions */}
              <tr className="total-balance-row">
                <td colSpan="6"><strong>Total Balance - Filtered</strong></td>
                <td colSpan="3" className="balance-amount">{`${currencyCode} ${filteredBalance.toFixed(2)}`}</td>
              </tr>
              {/* Overall Total Balance */}
              <tr className="total-balance-row">
                <td colSpan="6"><strong>Overall Total Balance</strong></td>
                <td colSpan="3" className="balance-amount">{`${currencyCode} ${totalBalance.toFixed(2)}`}</td>
              </tr>
            </tbody>
          </table>
        </div>
      ) : (
        <p>No transactions found for the selected date range.</p> // Show message if no transactions found
      )}

      {/* Display message for logout */}
      {message && (
        <p className={`message ${isError ? 'error-message' : 'success-message'}`}>
          {message}
        </p>
      )}

      {/* Button group for viewing report, returning to home, and logging out */}
      <div className="button-group">
        <button className="view-report-button" onClick={() => navigate('/view-report', { state: { data } })}>
          View Report
        </button>

        <button className="home-button" onClick={() => navigate('/home')}>
          Return to Home
        </button>

        <button className="logout-button" onClick={handleLogout}>
          <FaSignOutAlt className="fa-sign-out" /> Logout
        </button>
      </div>
    </div>
  );
}

export default StatementDetails;
