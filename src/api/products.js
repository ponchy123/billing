import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000/api';

// Create axios instance with default config
const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    }
});

// Add request interceptor to add auth token
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export const getProducts = async (page = 1, query = '') => {
    try {
        const response = await apiClient.get(`/products?page=${page}&query=${query}`);
        return response.data;
    } catch (error) {
        if (error.response && error.response.status === 403) {
            // Handle authentication error
            throw new Error('Authentication failed. Please login again.');
        }
        throw error;
    }
};
