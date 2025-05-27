// src/components/RegisterForm.js
import React, { useState } from 'react';
import authService from '../services/authService';

const RegisterForm = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [isError, setIsError] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    setMessage(''); setIsError(false);
    try {
      const response = await authService.register(username, email, password);
      setMessage(response.data.message); setIsError(false);
      setUsername(''); setEmail(''); setPassword(''); // Clear form on success
    } catch (err) {
      const resMessage = err.response?.data?.message || err.message || err.toString();
      setMessage(resMessage); setIsError(true);
    }
  };

  return (
    <div>
      <h2>Register</h2>
      <form onSubmit={handleRegister}>
        <div>
          <label htmlFor="reg-username">Username</label>
          <input type="text" id="reg-username" value={username} onChange={(e) => setUsername(e.target.value)} required autoComplete="username"/>
        </div>
        <div>
          <label htmlFor="reg-email">Email</label>
          <input type="email" id="reg-email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email"/>
        </div>
        <div>
          <label htmlFor="reg-password">Password</label>
          <input type="password" id="reg-password" value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="new-password"/>
        </div>
        <button type="submit">Register</button>
      </form>
      {message && <p className={`message ${isError ? 'error' : 'success'}`}>{message}</p>}
    </div>
  );
};
export default RegisterForm;