// src/components/LoginForm.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const LoginForm = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [isError, setIsError] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setMessage(''); setIsError(false);
    try {
      await login(username, password);
      navigate('/dashboard'); // Redirect on success
    } catch (err) {
      const resMessage = err.response?.data?.message || err.message || err.toString();
      setMessage(resMessage); setIsError(true);
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <div>
          <label htmlFor="login-username">Username</label>
          <input type="text" id="login-username" value={username} onChange={(e) => setUsername(e.target.value)} required autoComplete="username"/>
        </div>
        <div>
          <label htmlFor="login-password">Password</label>
          <input type="password" id="login-password" value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="current-password"/>
        </div>
        <button type="submit">Login</button>
      </form>
      {message && <p className={`message ${isError ? 'error' : 'success'}`}>{message}</p>}
    </div>
  );
};
export default LoginForm;