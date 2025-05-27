// src/context/AuthContext.js
import React, { createContext, useState, useContext, useEffect } from 'react';
import authService from '../services/authService';

const AuthContext = createContext();
export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedUser = authService.getCurrentUser();
    const storedToken = authService.getToken();
    if (storedUser && storedToken) {
      setCurrentUser(storedUser);
      setToken(storedToken);
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    const data = await authService.login(username, password); // Can throw error
    setCurrentUser(data.user);
    setToken(data.access_token);
    return data; // Return data on success
  };

  const logout = () => {
    authService.logout();
    setCurrentUser(null);
    setToken(null);
  };

  const value = { currentUser, token, isLoggedIn: !!token, login, logout };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};