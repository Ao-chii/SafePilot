/**
 * API接口定义
 * 定义所有后端API接口的调用方法
 */
import api_client from './client'

// 用户认证相关接口
export const auth_api = {
    // 用户登录
    login: (username: string, password: string) =>
        api_client.post('/auth/login', { username, password }),
    
    // 用户注册
    register: (data: {
        username: string
        email: string
        password: string
        first_name: string
        last_name?: string
        phone: string
        role: string
    }) =>
        api_client.post('/auth/register', data),
    
    // 获取用户资料
    get_profile: () =>
        api_client.get('/auth/profile'),
    
    // 更新用户资料
    update_profile: (data: {
        first_name?: string
        last_name?: string
        phone?: string
    }) =>
        api_client.put('/auth/profile', data),
    
    // 删除账户
    delete_account: () =>
        api_client.delete('/auth/account'),
    
    // 修改密码
    change_password: (data: {
        current_password: string
        new_password: string
    }) =>
        api_client.post('/auth/change-password', data),
    
    // 发送密码重置验证码
    send_reset_code: (data: {
        contact: string
        type: 'email' | 'phone'
    }) =>
        api_client.post('/auth/send-reset-code', data),
    
    // 验证重置验证码
    verify_reset_code: (data: {
        contact: string
        type: 'email' | 'phone'
        code: string
    }) =>
        api_client.post('/auth/verify-reset-code', data),
    
    // 重置密码
    reset_password: (data: {
        contact: string
        type: 'email' | 'phone'
        code: string
        new_password: string
    }) =>
        api_client.post('/auth/reset-password', data),
}

// 设备管理相关接口
export const device_api = {
    // 获取设备列表
    get_devices: () =>
        api_client.get('/devices'),
    
    // 获取设备详情
    get_device: (device_id: string) =>
        api_client.get(`/devices/${device_id}`),
    
    // 创建设备
    create_device: (data: {
        device_id: string
        name: string
        description?: string
    }) =>
        api_client.post('/devices', data),
    
    // 更新设备
    update_device: (device_id: string, data: {
        name?: string
        description?: string
        is_active?: boolean
    }) =>
        api_client.put(`/devices/${device_id}`, data),
    
    // 删除设备
    delete_device: (device_id: string) =>
        api_client.delete(`/devices/${device_id}`),
}

// 驾驶员管理相关接口
export const driver_api = {
    // 获取驾驶员列表
    get_drivers: () =>
        api_client.get('/drivers'),
    
    // 获取驾驶员详情
    get_driver: (driver_id: string) =>
        api_client.get(`/drivers/${driver_id}`),
    
    // 创建驾驶员
    create_driver: (data: {
        driver_id: string
        name: string
    }) =>
        api_client.post('/drivers', data),
    
    // 更新驾驶员
    update_driver: (driver_id: string, data: {
        name?: string
        is_active?: boolean
    }) =>
        api_client.put(`/drivers/${driver_id}`, data),
    
    // 删除驾驶员
    delete_driver: (driver_id: string) =>
        api_client.delete(`/drivers/${driver_id}`),
}

// 事件数据相关接口
export const event_api = {
    // 获取事件列表
    get_events: (params?: {
        device_id?: string
        driver_id?: string
        event_type?: string
        start_time?: string
        end_time?: string
        limit?: number
    }) =>
        api_client.get('/events', { params }),
    
    // 获取事件详情
    get_event: (event_id: string) =>
        api_client.get(`/events/${event_id}`),
    
    // 创建事件（客户端上报）
    create_events: (data: {
        device_id: string
        events: Array<{
            driver_id: string
            event_type: string
            confidence: number
            timestamp: string
            details?: object
        }>
    }) =>
        api_client.post('/events', data),
}

// 统计分析相关接口
export const stats_api = {
    // 获取设备统计信息
    get_device_stats: (device_id: string) =>
        api_client.get(`/stats/device/${device_id}`),
    
    // 获取驾驶员统计信息
    get_driver_stats: (driver_id: string) =>
        api_client.get(`/stats/driver/${driver_id}`),
}

// 系统相关接口
export const system_api = {
    // 健康检查
    health_check: () =>
        api_client.get('/system/health'),
}

// 实时监控相关接口
export const monitor_api = {
    // 获取视频流列表
    get_video_streams: () =>
        api_client.get('/monitor/streams'),
    
    // 获取指定视频流信息
    get_stream_info: (stream_id: string) =>
        api_client.get(`/monitor/streams/${stream_id}`),
    
    // 获取实时告警
    get_real_time_alerts: (params?: {
        limit?: number
        level?: string
    }) =>
        api_client.get('/monitor/alerts', { params }),
    
    // 处理告警
    handle_alert: (alert_id: string, action: string) =>
        api_client.post(`/monitor/alerts/${alert_id}/handle`, { action }),
    
    // 获取系统状态统计
    get_system_status: () =>
        api_client.get('/monitor/status'),
}