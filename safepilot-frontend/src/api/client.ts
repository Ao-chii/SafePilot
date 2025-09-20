/**
 * API客户端配置
 * 封装Axios请求，实现JWT Token管理和错误处理
 */
import axios from 'axios'
import type { AxiosInstance, AxiosResponse } from 'axios'
import { useAuthStore } from '../stores/auth'
import router from '../router'

// API基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
const API_PREFIX = '/api/v1'

// 创建axios实例
const api_client: AxiosInstance = axios.create({
    baseURL: `${API_BASE_URL}${API_PREFIX}`,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
})

// 请求拦截器 - 自动添加JWT Token
api_client.interceptors.request.use(
    (config) => {
        const auth_store = useAuthStore()
        const token = auth_store.access_token
        
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// 响应拦截器 - 统一错误处理和Token刷新
api_client.interceptors.response.use(
    (response: AxiosResponse) => {
        return response
    },
    async (error) => {
        const auth_store = useAuthStore()
            
        if (error.response?.status === 401) {
            // Token过期，清除认证信息并跳转到登录页
            auth_store.logout()
            router.push('/auth/login')
            return Promise.reject(new Error('认证已过期，请重新登录'))
        }
            
        if (error.response?.status === 403) {
            return Promise.reject(new Error('权限不足'))
        }
            
        if (error.response?.status >= 500) {
            return Promise.reject(new Error('服务器内部错误'))
        }
            
        // 返回API错误信息
        const message = error.response?.data?.error || error.message || '请求失败'
        return Promise.reject(new Error(message))
    }
)

export default api_client