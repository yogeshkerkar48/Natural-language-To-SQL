import axios from 'axios';
import { reactive } from 'vue';

const AUTH_API_URL = import.meta.env.VITE_API_URL || '/api';

const authClient = axios.create({
    baseURL: `${AUTH_API_URL}/auth`,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Reactive state for global access
const state = reactive({
    user: JSON.parse(localStorage.getItem('user')) || null,
    isAuthenticated: !!localStorage.getItem('auth_token')
});

export default {
    state,

    /**
     * Register a new user
     */
    async register(userData) {
        const response = await authClient.post('/register', userData);
        return response.data;
    },

    /**
     * Login user and store token
     */
    async login(credentials) {
        const response = await authClient.post('/login', credentials);
        const { access_token } = response.data;

        // Store token in localStorage
        localStorage.setItem('auth_token', access_token);
        state.isAuthenticated = true;

        // Fetch user info immediately after login to populate state
        await this.getCurrentUser();

        return response.data;
    },

    /**
     * Get current user information
     */
    async getCurrentUser() {
        const token = this.getToken();
        if (!token) {
            state.user = null;
            state.isAuthenticated = false;
            return null;
        }

        try {
            const response = await axios.get(`${AUTH_API_URL}/auth/me`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            // Update reactive state and localStorage
            state.user = response.data;
            state.isAuthenticated = true;
            localStorage.setItem('user', JSON.stringify(response.data));

            return response.data;
        } catch (error) {
            // If token is invalid, clear it
            this.logout();
            return null;
        }
    },

    /**
     * Logout user (clear token)
     */
    logout() {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        state.user = null;
        state.isAuthenticated = false;
    },

    /**
     * Get stored token
     */
    getToken() {
        return localStorage.getItem('auth_token');
    },

    /**
     * Check if user is authenticated (using reactive state)
     */
    isAuthenticated() {
        return state.isAuthenticated;
    },
};
