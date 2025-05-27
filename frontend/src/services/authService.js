// src/services/authService.js
import api from './api'; // <-- IMPORT the configured Axios instance from api.js
import axios from 'axios'; // Keep base axios for non-authenticated calls if needed

// Use the base URL from the api instance or define separately if preferred
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api/';

// --- Auth Functions ---

const register = (username, email, password) => {
    // Using base axios for register as it doesn't need auth token interceptor
    return axios.post(API_URL + 'register', { username, email, password });
};

const login = async (username, password) => {
    try {
        // Using base axios for login
        const response = await axios.post(API_URL + 'login', { username, password });
        if (response.data.access_token) {
            localStorage.setItem('user', JSON.stringify(response.data.user));
            localStorage.setItem('token', response.data.access_token); // Key is 'token'
        }
        return response.data;
    } catch (error) {
        console.error("Login service error:", error.response?.data || error.message);
        throw error;
    }
};

const logout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('token'); // Key is 'token'
};

const getCurrentUser = () => {
    const userStr = localStorage.getItem('user');
    try { return userStr ? JSON.parse(userStr) : null; } catch (e) { return null; }
};

const getToken = () => localStorage.getItem('token'); // Key is 'token'


// --- Authenticated API Calls (using the 'api' instance) ---

const getProtectedData = async () => {
    try {
       // Use 'api' instance - Authorization header added automatically by interceptor in api.js
       const response = await api.get('/protected');
       return response.data;
    } catch(error) {
      // Interceptor might handle 401 redirect, but log/re-throw for component feedback
      console.error("Protected data service error:", error.response?.data || error.message);
      throw error;
    }
};

const uploadImage = async (file, keywords, colorMapJson) => {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('keywords', keywords);
    formData.append('color_map', colorMapJson);

    try {
        // Use 'api' instance - Interceptor adds Auth header and handles Content-Type for FormData
        const response = await api.post('/upload_image', formData, {
            responseType: 'blob' // Expect image data back (for Method B)
        });
        return response.data; // This will be the Blob
    } catch(error) {
      console.error("Upload image service error:", error.response?.data || error.message);
      throw error; // Re-throw for component to handle
    }
};

// --- Export ---

// Group functions for export
const authService = {
    register,
    login,
    logout,
    getCurrentUser,
    getToken,
    getProtectedData,
    uploadImage // Include upload function
};

export default authService;