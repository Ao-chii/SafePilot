/**
 * 认证状态管理
 * 管理用户登录状态、JWT Token和用户信息
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface User {
    id: number
    username: string
    email: string
    first_name?: string
    last_name?: string
    is_admin?: boolean
}

export const useAuthStore = defineStore('auth', () => {
    // 状态
    const access_token = ref<string | null>(
        localStorage.getItem('access_token')
    )
    const user = ref<User | null>(
        JSON.parse(localStorage.getItem('user') || 'null')
    )
    const is_loading = ref(false)

    // 计算属性
    const is_authenticated = computed(() => !!access_token.value)
    const user_display_name = computed(() => {
        if (!user.value) return ''
        if (user.value.first_name && user.value.last_name) {
            return `${user.value.first_name} ${user.value.last_name}`
        }
        return user.value.username
    })

    // 登录
    const login = (token: string, user_data: User) => {
        access_token.value = token
        user.value = user_data
        
        // 持久化存储
        localStorage.setItem('access_token', token)
        localStorage.setItem('user', JSON.stringify(user_data))
    }

    // 登出
    const logout = () => {
        access_token.value = null
        user.value = null
        
        // 清除存储
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
    }

    // 更新用户信息
    const update_user = (user_data: User) => {
        user.value = user_data
        localStorage.setItem('user', JSON.stringify(user_data))
    }

    return {
        // 状态
        access_token,
        user,
        is_loading,
        
        // 计算属性
        is_authenticated,
        user_display_name,
        
        // 方法
        login,
        logout,
        update_user,
    }
})