/**
 * WebSocket连接管理器
 * 处理实时数据推送和连接状态管理
 */

export interface WebSocketConfig {
  url: string
  reconnect_interval?: number
  max_reconnect_attempts?: number
  heartbeat_interval?: number
  protocols?: string[]
}

export interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
}

export interface AlertMessage {
  id: string
  type: string
  level: 'critical' | 'warning' | 'info'
  device_id: string
  device_name: string
  driver_id?: string
  driver_name?: string
  confidence: number
  timestamp: string
  details?: any
}

export interface StreamStatusMessage {
  stream_id: string
  status: 'online' | 'offline' | 'connecting'
  quality?: string
  bandwidth?: number
  error?: string
}

export type MessageHandler<T = any> = (data: T) => void

export class WebSocketManager {
  private ws: WebSocket | null = null
  private config: WebSocketConfig
  private reconnect_attempts = 0
  private reconnect_timer: number | null = null
  private heartbeat_timer: number | null = null
  private message_handlers: Map<string, Set<MessageHandler>> = new Map()
  private is_manually_closed = false

  constructor(config: WebSocketConfig) {
    this.config = {
      reconnect_interval: 3000,
      max_reconnect_attempts: 10,
      heartbeat_interval: 30000,
      ...config
    }
  }

  /**
   * 连接WebSocket
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.is_manually_closed = false
        
        console.log(`连接WebSocket: ${this.config.url}`)
        
        this.ws = new WebSocket(this.config.url, this.config.protocols)

        this.ws.onopen = (event) => {
          console.log('WebSocket连接成功')
          this.reconnect_attempts = 0
          this.start_heartbeat()
          this.emit_event('connected', { event })
          resolve()
        }

        this.ws.onmessage = (event) => {
          this.handle_message(event)
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket连接关闭:', event.code, event.reason)
          this.stop_heartbeat()
          this.emit_event('disconnected', { event })
          
          if (!this.is_manually_closed) {
            this.schedule_reconnect()
          }
        }

        this.ws.onerror = (event) => {
          console.error('WebSocket连接错误:', event)
          this.emit_event('error', { event })
          reject(new Error('WebSocket连接失败'))
        }

        // 连接超时处理
        setTimeout(() => {
          if (this.ws?.readyState === WebSocket.CONNECTING) {
            reject(new Error('WebSocket连接超时'))
          }
        }, 10000)

      } catch (error) {
        reject(error)
      }
    })
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    this.is_manually_closed = true
    
    if (this.reconnect_timer) {
      clearTimeout(this.reconnect_timer)
      this.reconnect_timer = null
    }
    
    this.stop_heartbeat()
    
    if (this.ws) {
      this.ws.close(1000, '手动关闭')
      this.ws = null
    }
  }

  /**
   * 发送消息
   */
  send(message: any): boolean {
    if (this.ws?.readyState === WebSocket.OPEN) {
      try {
        const msg = typeof message === 'string' ? message : JSON.stringify(message)
        this.ws.send(msg)
        return true
      } catch (error) {
        console.error('发送WebSocket消息失败:', error)
        return false
      }
    } else {
      console.warn('WebSocket未连接，无法发送消息')
      return false
    }
  }

  /**
   * 订阅消息类型
   */
  on<T = any>(message_type: string, handler: MessageHandler<T>): void {
    if (!this.message_handlers.has(message_type)) {
      this.message_handlers.set(message_type, new Set())
    }
    this.message_handlers.get(message_type)!.add(handler)
  }

  /**
   * 取消订阅
   */
  off<T = any>(message_type: string, handler: MessageHandler<T>): void {
    const handlers = this.message_handlers.get(message_type)
    if (handlers) {
      handlers.delete(handler)
      if (handlers.size === 0) {
        this.message_handlers.delete(message_type)
      }
    }
  }

  /**
   * 获取连接状态
   */
  get is_connected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  /**
   * 获取连接状态字符串
   */
  get connection_state(): string {
    if (!this.ws) return 'disconnected'
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting'
      case WebSocket.OPEN:
        return 'connected'
      case WebSocket.CLOSING:
        return 'closing'
      case WebSocket.CLOSED:
        return 'disconnected'
      default:
        return 'unknown'
    }
  }

  /**
   * 处理接收到的消息
   */
  private handle_message(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data)
      
      console.log('收到WebSocket消息:', message.type, message.data)
      
      // 处理心跳响应
      if (message.type === 'pong') {
        return
      }
      
      // 分发消息给订阅者
      this.emit_event(message.type, message.data)
      
    } catch (error) {
      console.error('解析WebSocket消息失败:', error, event.data)
    }
  }

  /**
   * 发送事件给订阅者
   */
  private emit_event(event_type: string, data: any): void {
    const handlers = this.message_handlers.get(event_type)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data)
        } catch (error) {
          console.error(`处理WebSocket事件 ${event_type} 失败:`, error)
        }
      })
    }
  }

  /**
   * 安排重连
   */
  private schedule_reconnect(): void {
    if (this.is_manually_closed) return
    
    if (this.reconnect_attempts >= this.config.max_reconnect_attempts!) {
      console.error('WebSocket重连次数已达上限')
      this.emit_event('max_reconnect_reached', {})
      return
    }

    this.reconnect_attempts++
    const delay = Math.min(
      this.config.reconnect_interval! * Math.pow(1.5, this.reconnect_attempts - 1),
      30000
    )

    console.log(`${delay / 1000}秒后尝试重连 (${this.reconnect_attempts}/${this.config.max_reconnect_attempts})`)

    this.reconnect_timer = window.setTimeout(() => {
      this.emit_event('reconnecting', { attempt: this.reconnect_attempts })
      this.connect().catch(error => {
        console.error('重连失败:', error)
      })
    }, delay)
  }

  /**
   * 开始心跳
   */
  private start_heartbeat(): void {
    if (this.config.heartbeat_interval! > 0) {
      this.heartbeat_timer = window.setInterval(() => {
        this.send({ type: 'ping', timestamp: new Date().toISOString() })
      }, this.config.heartbeat_interval!)
    }
  }

  /**
   * 停止心跳
   */
  private stop_heartbeat(): void {
    if (this.heartbeat_timer) {
      clearInterval(this.heartbeat_timer)
      this.heartbeat_timer = null
    }
  }
}

/**
 * SafePilot专用WebSocket管理器
 */
export class SafePilotWebSocket extends WebSocketManager {
  constructor(ws_url: string) {
    super({
      url: ws_url,
      reconnect_interval: 3000,
      max_reconnect_attempts: 10,
      heartbeat_interval: 30000
    })
    
    this.setup_message_handlers()
  }

  /**
   * 设置消息处理器
   */
  private setup_message_handlers(): void {
    // 可以在这里添加通用的消息处理逻辑
  }

  /**
   * 订阅实时告警
   */
  subscribe_alerts(handler: MessageHandler<AlertMessage>): void {
    this.on('alert', handler)
  }

  /**
   * 订阅流状态更新
   */
  subscribe_stream_status(handler: MessageHandler<StreamStatusMessage>): void {
    this.on('stream_status', handler)
  }

  /**
   * 订阅系统状态
   */
  subscribe_system_status(handler: MessageHandler<any>): void {
    this.on('system_status', handler)
  }

  /**
   * 请求视频流列表
   */
  request_stream_list(): void {
    this.send({
      type: 'request_stream_list',
      timestamp: new Date().toISOString()
    })
  }

  /**
   * 请求设备状态
   */
  request_device_status(): void {
    this.send({
      type: 'request_device_status',
      timestamp: new Date().toISOString()
    })
  }
}

// 导出实例（在实际使用时需要配置WebSocket URL）
let safepilot_websocket: SafePilotWebSocket | null = null

export const get_websocket_instance = (ws_url?: string): SafePilotWebSocket => {
  if (!safepilot_websocket && ws_url) {
    safepilot_websocket = new SafePilotWebSocket(ws_url)
  }
  
  if (!safepilot_websocket) {
    throw new Error('WebSocket未初始化，请先提供WebSocket URL')
  }
  
  return safepilot_websocket
}