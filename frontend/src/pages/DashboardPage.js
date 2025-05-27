// src/pages/DashboardPage.js
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import authService from '../services/authService';

const DashboardPage = () => {
  const { currentUser } = useAuth();
  const [protectedData, setProtectedData] = useState(null);
  const [message, setMessage] = useState('Loading protected data...'); // Initial message
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    const fetchProtectedData = async () => {
      setMessage('Loading protected data...'); // Reset message on fetch
      setIsError(false);
      try {
        const data = await authService.getProtectedData();
        setProtectedData(data);
        setMessage(''); // Clear message on success
      } catch (err) {
        const resMessage = err.response?.data?.message || err.response?.data?.msg || err.message || err.toString();
        setMessage(`Error fetching protected data: ${resMessage}`);
        setIsError(true); setProtectedData(null);
      }
    };
    fetchProtectedData();
  }, []); // Run once on mount

  if (!currentUser) return <p>Loading user information...</p>; // Should be brief

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Welcome, {currentUser.username} ({currentUser.email})!</p>
      <hr />
      <h2>Protected API Data:</h2>
      {message && <p className={`message ${isError ? 'error' : 'success'}`}>{message}</p>}
      {protectedData && !isError && (
        <div className="dashboard-data">
            <pre>{JSON.stringify(protectedData, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};
export default DashboardPage;