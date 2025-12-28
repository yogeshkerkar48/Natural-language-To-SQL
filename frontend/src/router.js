import { createRouter, createWebHistory } from 'vue-router';
import authService from './services/authService';

// Import components
import Login from './components/Login.vue';
import Register from './components/Register.vue';
import MainPage from './components/MainPage.vue';

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: Login,
        meta: { requiresGuest: true },
    },
    {
        path: '/register',
        name: 'Register',
        component: Register,
        meta: { requiresGuest: true },
    },
    {
        path: '/',
        name: 'Home',
        component: MainPage,
        meta: { requiresAuth: true },
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

// Navigation guard
router.beforeEach((to, from, next) => {
    const isAuthenticated = authService.isAuthenticated();

    if (to.meta.requiresAuth && !isAuthenticated) {
        // Redirect to login if trying to access protected route
        next('/login');
    } else if (to.meta.requiresGuest && isAuthenticated) {
        // Redirect to home if trying to access guest-only route while authenticated
        next('/');
    } else {
        next();
    }
});

export default router;
