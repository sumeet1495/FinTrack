// Import necessary modules and components
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid'; // Importing UUID library
import './Login.css';
import { FaEye, FaEyeSlash } from 'react-icons/fa'; // Importing eye icons for password visibility

/*
 * The Login component allows users to log into the application.
 * It handles user input for email and password, toggles password visibility,
 * sends login requests to the server, and manages authentication tokens.
 */
function Login() {
  const [email, setEmail] = useState(''); // State for email input
  const [password, setPassword] = useState(''); // State for password input
  const [showPassword, setShowPassword] = useState(false); // State to toggle password visibility
  const [responseMessage, setResponseMessage] = useState(''); // State to store response message
  const [isError, setIsError] = useState(false); // State to handle error message styling
  const [isButtonDisabled, setIsButtonDisabled] = useState(false); // State to disable the login button
  const navigate = useNavigate(); // Hook for navigation

  /*
   * useEffect hook to handle redirection after successful login.
   * If login is successful and there is a response message, redirects to home after 2 seconds.
   */
  useEffect(() => {
    if (responseMessage && !isError) {
      // Redirect after 2 seconds if login is successful
      const timer = setTimeout(() => navigate('/home'), 2000);

      return () => clearTimeout(timer); // Cleanup the timer on component unmount
    }
  }, [responseMessage, isError, navigate]);

  /*
   * handleLogin function manages the login process.
   * It sends a POST request with email and password to the server,
   * handles the response, stores the token, and updates the UI accordingly.
   */
  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const reference_number = uuidv4(); // Generate UUID for reference_number
      const response = await axios.post('http://127.0.0.1:8002/user/login', {
        reference_number,
        email,
        password,
      });

      if (response.status === 200 && response.data.data.token) {
        const token = response.data.data.token; // Extract the token
        localStorage.setItem('token', token); // Store token in localStorage
        setResponseMessage(response.data.response_message); // Set the response message
        setIsError(false); // Indicate success message
        setIsButtonDisabled(false); // Ensure button is enabled on success
      } else {
        setResponseMessage(response.data.response_message || 'Login failed. Please check your credentials.');
        setIsError(true); // Indicate error message
        setIsButtonDisabled(true); // Disable the button on error
      }
    } catch (error) {
      if (error.response) {
        // Server responded with a status code outside the 2xx range
        console.error('Server responded with error:', error.response.data);
        setResponseMessage(error.response.data.response_message || 'Login failed: An unexpected error occurred.');
        setIsError(true); // Indicate error message
        setIsButtonDisabled(true); // Disable the button on error
      } else if (error.request) {
        // No response received from the server
        console.error('No response received:', error.request);
        setResponseMessage('No response from the server. Please check your network connection.');
        setIsError(true); // Indicate error message
        setIsButtonDisabled(true); // Disable the button on error
      } else {
        // Error setting up the request
        console.error('Error setting up request:', error.message);
        setResponseMessage('Error: ' + error.message);
        setIsError(true); // Indicate error message
        setIsButtonDisabled(true); // Disable the button on error
      }
    }
  };

  /*
   * togglePasswordVisibility function toggles the visibility of the password field.
   * It switches between 'text' and 'password' input types.
   */
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className="container">
      <div className="logo-container">
        <img
          src="http://localhost:3000/fintrack-logo.png"
          alt="FinTrack Logo"
          className="fintrack-logo"
        />
      </div>
      <div className="login-container">
        <h2>Log in</h2>
        {/* Display response message */}
        {responseMessage && (
          <p className={`response-message ${isError ? 'error' : 'success'}`}>
            {responseMessage}
          </p>
        )}
        {/* Login form */}
        <form onSubmit={handleLogin}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <div className="password-container">
            <input
              type={showPassword ? 'text' : 'password'} // Toggle between password and text input types
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            {/* Show eye/eye-slash icons */}
            <span className="password-toggle-icon" onClick={togglePasswordVisibility}>
              {showPassword ? <FaEye /> : <FaEyeSlash />}
            </span>
          </div>
          {/* Disable the button if there is an error */}
          <button type="submit" disabled={isButtonDisabled}>Login</button>
        </form>
        <p>
          Don't have an account? <a href="/register">Register</a>
        </p>
      </div>
    </div>
  );
}

export default Login;
