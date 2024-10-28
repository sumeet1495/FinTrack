// Import React to enable JS and component creation
import React from 'react';

// Import ReactDOM for rendering React components into the DOM
import ReactDOM from 'react-dom/client';

// Import global CSS styles for the entire app
import './index.css';

// Import the main App component, which contains the application's routing and core logic
import App from './App';

/*
 * Create the root of the React app by targeting the DOM element with the ID 'root'.
 * This is where the entire React application will be mounted.
 */
const root = ReactDOM.createRoot(document.getElementById('root'));

/*
 * Render the React application within React's StrictMode.
 * StrictMode is a development tool that helps highlight potential issues in the application.
 * It activates additional checks and warnings for its descendants.
 */
root.render(
  <React.StrictMode>
    <App /> {/* Render the App component, which contains the entire application */}
  </React.StrictMode>
);
