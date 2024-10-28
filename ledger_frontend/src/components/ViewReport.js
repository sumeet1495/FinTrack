// Import necessary modules and components
import React, { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Chart } from 'chart.js/auto'; // Including Chart.js for rendering charts
import axios from 'axios'; // For making the logout API request
import { FaSignOutAlt } from 'react-icons/fa'; // Importing the logout icon
import { v4 as uuidv4 } from 'uuid'; // Importing UUID for reference number
import './ViewReport.css'; // Import the CSS file for styling

/*
 * ViewReport component displays a report of transactions between selected dates,
 * including bar and line charts for visualizing credits, debits, and balance changes.
 * Users can also log out from this component.
 */
function ViewReport() {
  const { state } = useLocation(); // Retrieve passed state from the previous route
  const { data } = state; // Destructuring the transaction data
  const navigate = useNavigate(); // Hook for programmatic navigation

  const [fromDate, setFromDate] = useState(''); // State for selected from date
  const [toDate, setToDate] = useState(''); // State for selected to date
  const [filteredData, setFilteredData] = useState([]); // State for filtered transactions based on the date range
  const [errorMessage, setErrorMessage] = useState(''); 
  const [logoutMessage, setLogoutMessage] = useState(''); 
  const [isError, setIsError] = useState(false); // State to track if there is an error

  const barChartRef = useRef(null); // Reference for bar chart instance
  const lineChartRef = useRef(null); // Reference for line chart instance

  // Function to calculate tomorrow's date in the format yyyy-MM-dd
  const getTomorrowDate = () => {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1); // Increment the day by 1
    return tomorrow.toISOString().split('T')[0]; // Return in yyyy-MM-dd format
  };

  const tomorrowDate = getTomorrowDate(); // Get tomorrow's date

  /*
   * useEffect to create bar and line charts based on filtered data.
   * Destroys previous charts if they exist before creating new ones.
   */
  useEffect(() => {
    if (filteredData.length > 0) {
      if (barChartRef.current) {
        barChartRef.current.destroy(); // Destroy previous bar chart
      }

      const barCtx = document.getElementById('barChart').getContext('2d'); // Get bar chart context

      // Ensure data is sorted by date in ascending order
      const sortedFilteredData = filteredData.sort(
        (a, b) => new Date(a.transaction_timestamp) - new Date(b.transaction_timestamp)
      );

      // Create bar chart for credit and debit transactions
      barChartRef.current = new Chart(barCtx, {
        type: 'bar',
        data: {
          labels: sortedFilteredData.map(transaction => transaction.transaction_timestamp.split(' ')[0]), // Date labels
          datasets: [
            {
              label: 'Credit',
              data: sortedFilteredData.map(transaction => transaction.transaction_type === 'CREDIT' ? transaction.amount : 0), // Credit data
              backgroundColor: 'green', // Color for credit bars
            },
            {
              label: 'Debit',
              data: sortedFilteredData.map(transaction => transaction.transaction_type === 'DEBIT' ? transaction.amount : 0), // Debit data
              backgroundColor: 'red', // Color for debit bars
            },
          ],
        },
        options: {
          responsive: true,
          scales: {
            x: {
              title: {
                display: true,
                text: 'Transaction Date', // X-axis label
              },
            },
            y: {
              title: {
                display: true,
                text: 'Amount', // Y-axis label
              },
            },
          },
        },
      });

      // Calculate balance changes for line chart
      const balanceChanges = sortedFilteredData.reduce((balances, transaction) => {
        const lastBalance = balances.length ? balances[balances.length - 1] : 0;
        const newBalance = transaction.transaction_type === 'CREDIT' ? lastBalance + transaction.amount : lastBalance - transaction.amount;
        balances.push(newBalance);
        return balances;
      }, []);

      if (lineChartRef.current) {
        lineChartRef.current.destroy(); // Destroy previous line chart
      }

      const lineCtx = document.getElementById('lineChart').getContext('2d'); // Get line chart context

      // Create line chart for balance changes
      lineChartRef.current = new Chart(lineCtx, {
        type: 'line',
        data: {
          labels: sortedFilteredData.map(transaction => transaction.transaction_timestamp.split(' ')[0]), // Date labels
          datasets: [
            {
              label: 'Balance',
              data: balanceChanges, // Balance data points
              borderColor: 'blue', // Line color
              fill: false, // No fill below the line
            },
          ],
        },
        options: {
          responsive: true,
          scales: {
            x: {
              title: {
                display: true,
                text: 'Transaction Date', // X-axis label
              },
            },
            y: {
              title: {
                display: true,
                text: 'Balance', // Y-axis label
              },
            },
          },
        },
      });

      return () => {
        if (barChartRef.current) barChartRef.current.destroy(); // Cleanup bar chart
        if (lineChartRef.current) lineChartRef.current.destroy(); // Cleanup line chart
      };
    }
  }, [filteredData]); // Effect runs when filteredData changes

  /*
   * handleFilter function filters transactions based on the selected date range.
   * If dates are invalid, an error message is displayed.
   */
  const handleFilter = () => {
    if (!fromDate || !toDate) {
      setErrorMessage('Please select both From and To dates.'); // Error for missing dates
      setFilteredData([]); // Clear filtered data
      return;
    }

    if (new Date(fromDate) > new Date(toDate)) {
      setErrorMessage('To Date should be greater than or equal to From Date.'); // Error for invalid date range
      setFilteredData([]); // Clear filtered data
      return;
    }

    setErrorMessage(''); // Clear any previous error messages

    // Filter transactions based on the date range
    const filtered = data.filter(transaction => {
      const transactionDate = new Date(transaction.transaction_timestamp.split(' ')[0]);
      return transactionDate >= new Date(fromDate) && transactionDate <= new Date(toDate);
    });

    setFilteredData(filtered); // Update state with filtered transactions
  };

  /*
   * handleLogout function logs the user out by calling the logout API.
   * It clears the token from local storage and navigates back to the login page.
   */
  const handleLogout = async () => {
    const token = localStorage.getItem('token'); // Get the token from local storage
    const reference_number = uuidv4(); // Generate a unique reference number
    if (!token) {
      setLogoutMessage('No token found, redirecting to login.'); // Handle missing token
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
        { reference_number }, // Send reference number in the body
        {
          headers: {
            'Authorization': `Bearer ${token}` // Include token in Authorization header
          }
        }
      );

      // Handle successful logout
      if (response.status === 200 && response.data.status === "SUCCESS") {
        setLogoutMessage('Successfully logged out the User.');
        setIsError(false);
        localStorage.removeItem('token'); // Remove token from local storage
        setTimeout(() => {
          navigate('/login', { replace: true }); // Redirect to login after 2 seconds
        }, 2000);
      } else {
        throw new Error('Unexpected response format.');
      }
    } catch (error) {
      setLogoutMessage('Logout failed. Please try again.'); // Handle errors
      setIsError(true);
    }
  };

  // Use the currency code from any transaction (assuming all transactions have the same currency)
  const currencyCode = filteredData.length > 0 ? filteredData[0].currency_code : '';

  return (
    <div className="view-report-container">
      <img src="/fintrack-logo.png" alt="FinTrack Logo" className="view-report-logo" />

      <h2>Transaction Report</h2>

      {/* Date picker and filter button */}
      <div className="date-picker-container">
        <input
          type="date"
          value={fromDate}
          onChange={(e) => setFromDate(e.target.value)}
          max={tomorrowDate} // Disable future dates
          placeholder="From Date"
          className="date-input-small"
        />
        <input
          type="date"
          value={toDate}
          onChange={(e) => setToDate(e.target.value)}
          max={tomorrowDate} // Disable future dates
          placeholder="To Date"
          className="date-input-small"
        />
        <button onClick={handleFilter}>Filter</button>
      </div>

      {/* Error message display */}
      {errorMessage && <div className="error-message">{errorMessage}</div>}

      {/* Render charts if filtered data is available */}
      {filteredData.length > 0 && (
        <div className="chart-container">
          <div className="chart-item">
            <canvas id="barChart"></canvas> {/* Bar chart for credits and debits */}
          </div>
          <div className="chart-item">
            <canvas id="lineChart"></canvas> {/* Line chart for balance changes */}
          </div>
        </div>
      )}

      {/* Totals table for credits and debits */}
      <div className="totals-table">
        <table>
          <thead>
            <tr>
              <th>Total Credit</th>
              <th>Total Debit</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{`${currencyCode} ${filteredData.reduce((sum, transaction) => sum + (transaction.transaction_type === 'CREDIT' ? transaction.amount : 0), 0).toFixed(2)}`}</td>
              <td>{`${currencyCode} ${filteredData.reduce((sum, transaction) => sum + (transaction.transaction_type === 'DEBIT' ? transaction.amount : 0), 0).toFixed(2)}`}</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Display logout message */}
      {logoutMessage && (
        <p className={`message ${isError ? 'error-message' : 'success-message'}`}>
          {logoutMessage}
        </p>
      )}

      {/* Button group for navigation and logout */}
      <div className="button-group">
        <button className="view-report-button" onClick={() => navigate(-1)}>Back</button>
        <button className="home-button" onClick={() => navigate('/home')}>Return to Home</button>
        <button className="logout-button" onClick={handleLogout}>
          <FaSignOutAlt /> Logout
        </button>
      </div>
    </div>
  );
}

export default ViewReport;
