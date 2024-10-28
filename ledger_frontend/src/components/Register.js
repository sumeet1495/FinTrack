// Import necessary modules and components
import React, { useState } from 'react'; 
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid'; // Importing UUID library for generating unique reference numbers
import './Register.css'; // Importing the CSS file for styling
import { FaEye, FaEyeSlash } from 'react-icons/fa'; // Importing eye icons from react-icons

/*
 * The Register component allows users to create a new account.
 * It validates user input (email and password), sends the registration request,
 * and handles both success and error states.
 */
function Register() {
  const [email, setEmail] = useState(''); // State for email input
  const [password, setPassword] = useState(''); // State for password input
  const [showPassword, setShowPassword] = useState(false); // State to toggle password visibility
  const [responseMessage, setResponseMessage] = useState(''); // State to store response messages (success/error)
  const [isError, setIsError] = useState(false); // State to track error state
  const navigate = useNavigate(); // Hook for programmatic navigation

  // Regular expressions for validating password and email format
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$/; // Password must contain upper, lower case, number, special char, and be 8+ characters long
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; // Email format validation

  /*
   * handleRegister function manages the registration process.
   * It validates email and password, sends a POST request to the server,
   * and handles the response by updating the UI accordingly.
   */
  const handleRegister = async (e) => {
    e.preventDefault();

    // Validate email format
    if (!emailRegex.test(email)) {
      setResponseMessage('Invalid email format.');
      setIsError(true);
      return;
    }

    // Validate password format
    if (!passwordRegex.test(password)) {
      setResponseMessage('Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one number, and one special character.');
      setIsError(true);
      return;
    }

    const reference_number = uuidv4(); // Generate a unique reference number

    try {
      console.log('Sending data:', { reference_number, email, password }); // Log data being sent (for debugging)

      // Sending POST request to the backend API for registration
      await axios.post('http://127.0.0.1:8002/user/register', {
        reference_number,
        email,
        password,
      });

      setResponseMessage('Successfully registered! Redirecting to login...');
      setIsError(false); // Indicate success message

      // Redirect to login page after a 2-second delay
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (error) {
      console.error('Registration error:', error); // Log the error for debugging
      setIsError(true); // Indicate error message

      if (error.response) {
        // If the backend responds with an error message
        const backendMessage = error.response.data.response_message;
        setResponseMessage(backendMessage || 'Registration failed: An unexpected error occurred.');
      } else if (error.request) {
        // If there is no response from the server
        setResponseMessage('No response from the server. Please check your network connection.');
      } else {
        // If there is an error setting up the request
        setResponseMessage('Error: ' + error.message);
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
      {/* Logo container with FinTrack logo */}
      <div className="logo-container">
        <img src="http://localhost:3000/fintrack-logo.png" alt="FinTrack Logo" className="fintrack-logo" />
      </div>

      {/* Registration form container */}
      <div className="register-container">
        <h2>Register</h2>
        {/* Display response message */}
        {responseMessage && (
          <p className={`response-message ${isError ? 'error' : 'success'}`}>{responseMessage}</p>
        )}
        {/* Registration form */}
        <form onSubmit={handleRegister}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          {/* Password field with visibility toggle */}
          <div className="password-container">
            <input
              type={showPassword ? "text" : "password"} // Toggle between password and text input types
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
          {/* Register button, disabled if there is an error */}
          <button type="submit" disabled={isError}>Register</button>
        </form>
        {/* Link to navigate to the login page */}
        <p>Already have an account? <a href="/login">Login</a></p>
      </div>
    </div>
  );
}

export default Register;
