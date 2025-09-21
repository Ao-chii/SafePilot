import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// 布局组件
import AppLayout from '../components/layouts/AppLayout.vue'
import AuthLayout from '../components/layouts/AuthLayout.vue'

// 认证页面
import LoginView from '../views/auth/LoginView.vue'
import RegisterView from '../views/auth/RegisterView.vue'
import ChangePasswordView from '../views/auth/ChangePasswordView.vue'

// 主页面
import DashboardView from '../views/dashboard/DashboardView.vue'
import EventsView from '../views/events/EventsView.vue'
import DriversView from '../views/drivers/DriversView.vue'
import DevicesView from '../views/devices/DevicesView.vue'
import StatsView from '../views/stats/StatsView.vue'
import ProfileView from '../views/ProfileView.vue'
import SettingsView from '../views/SettingsView.vue'
import ColorSchemeDemo from '../views/ColorSchemeDemo.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            redirect: '/dashboard',
        },
        {
            path: '/auth',
            component: AuthLayout,
            children: [
                {
                    path: 'login',
                    name: 'Login',
                    component: LoginView,
                    meta: { requiresGuest: true },
                },
                {
                    path: 'register',
                    name: 'Register',
                    component: RegisterView,
                    meta: { requiresGuest: true },
                },
            ],
        },
        {
            path: '/',
            component: AppLayout,
            meta: { requiresAuth: true },
            children: [
                {
                    path: 'dashboard',
                    name: 'Dashboard',
                    component: DashboardView,
                },
                {
                    path: 'events',
                    name: 'Events',
                    component: EventsView,
                },
                {
                    path: 'drivers',
                    name: 'Drivers',
                    component: DriversView,
                },
                {
                    path: 'devices',
                    name: 'Devices',
                    component: DevicesView,
                },
                {
                    path: 'stats',
                    name: 'Stats',
                    component: StatsView,
                },
                {
                    path: 'profile',
                    name: 'Profile',
                    component: ProfileView,
                },
                {
                    path: 'settings',
                    name: 'Settings',
                    component: SettingsView,
                },
                {
                    path: 'color-demo',
                    name: 'ColorDemo',
                    component: ColorSchemeDemo,
                },
                {
                    path: 'change-password',
                    name: 'ChangePassword',
                    component: ChangePasswordView,
                },
            ],
        },
    ],
})

// 路由守卫 - 认证检查
router.beforeEach((to, from, next) => {
    const auth_store = useAuthStore()
    
    // 检查是否需要登录
    if (to.meta.requiresAuth && !auth_store.is_authenticated) {
        next('/auth/login')
        return
    }
    
    // 检查是否需要游客状态（已登录用户不能访问登录页）
    if (to.meta.requiresGuest && auth_store.is_authenticated) {
        next('/dashboard')
        return
    }
    
    next()
})

export default router
