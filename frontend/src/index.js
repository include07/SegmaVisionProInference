// src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
// import './index.css'; // REMOVED/COMMENTED - We use App.css
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);