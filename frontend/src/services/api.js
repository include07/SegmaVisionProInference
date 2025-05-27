// src/services/api.js
import axios from 'axios';

// Get the base API URL from environment variables (defined in .env)
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
console.log(`Using Central API URL: ${API_URL}`);

// Create the central Axios instance named 'api'
const api = axios.create({
    baseURL: API_URL,
});

// Add a request interceptor to automatically add the JWT token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token'); // Use consistent key 'token'
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        // Let Axios handle Content-Type for FormData automatically
        if (!(config.data instanceof FormData)) {
             config.headers['Content-Type'] = 'application/json';
        } else {
             // For FormData, delete Content-Type so browser can set it with boundary
             delete config.headers['Content-Type'];
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Optional: Add response interceptor for handling 401 errors globally
api.interceptors.response.use(
    (response) => {
        return response; // Pass through successful responses
    },
    (error) => {
        if (error.response && error.response.status === 401) {
            console.warn('Unauthorized (401) detected by interceptor. Logging out.');
            // Optionally clear local storage and redirect to login
            localStorage.removeItem('user');
            localStorage.removeItem('token');
            // Redirect - This might be better handled in AuthContext or component
            if (window.location.pathname !== '/login') {
                 window.location.href = '/login';
            }
        }
        return Promise.reject(error); // Pass error along
    }
);

// Export the configured instance so other files can import it
export default api;