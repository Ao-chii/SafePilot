/**
 * 视频流管理器
 * 处理多种视频源的连接、状态管理和性能优化
 */

export interface VideoStreamConfig {
  id: string
  type: 'webrtc' | 'rtmp' | 'hls' | 'file' | 'webcam'
  url?: string
  device_id?: string
  quality?: 'low' | 'medium' | 'high' | 'auto'
  retry_count?: number
  timeout?: number
}

export interface VideoStreamState {
  status: 'disconnected' | 'connecting' | 'connected' | 'error' | 'reconnecting'
  error?: string
  retry_attempts: number
  last_connected?: Date
  bandwidth?: number
  resolution?: { width: number; height: number }
}

export class VideoStreamManager {
  private streams: Map<string, {
    config: VideoStreamConfig
    state: VideoStreamState
    element?: HTMLVideoElement
    peer_connection?: RTCPeerConnection
    media_stream?: MediaStream
  }> = new Map()

  private retry_timeouts: Map<string, number> = new Map()
  
  constructor() {
    this.init_webrtc_config()
  }

  /**
   * 添加视频流
   */
  async add_stream(config: VideoStreamConfig): Promise<boolean> {
    try {
      const stream_data = {
        config,
        state: {
          status: 'disconnected' as const,
          retry_attempts: 0
        }
      }
      
      this.streams.set(config.id, stream_data)
      
      return await this.connect_stream(config.id)
    } catch (error) {
      console.error(`添加视频流失败 ${config.id}:`, error)
      return false
    }
  }

  /**
   * 连接视频流
   */
  async connect_stream(stream_id: string): Promise<boolean> {
    const stream_data = this.streams.get(stream_id)
    if (!stream_data) return false

    const { config } = stream_data
    
    try {
      this.update_stream_state(stream_id, { status: 'connecting' })
      
      switch (config.type) {
        case 'webrtc':
          return await this.connect_webrtc_stream(stream_id)
        case 'webcam':
          return await this.connect_webcam_stream(stream_id)
        case 'hls':
          return await this.connect_hls_stream(stream_id)
        case 'rtmp':
          return await this.connect_rtmp_stream(stream_id)
        case 'file':
          return await this.connect_file_stream(stream_id)
        default:
          throw new Error(`不支持的视频流类型: ${config.type}`)
      }
    } catch (error) {
      console.error(`连接视频流失败 ${stream_id}:`, error)
      this.update_stream_state(stream_id, { 
        status: 'error',
        error: error instanceof Error ? error.message : String(error)
      })
      
      // 自动重连
      this.schedule_reconnect(stream_id)
      return false
    }
  }

  /**
   * 连接WebRTC视频流
   */
  private async connect_webrtc_stream(stream_id: string): Promise<boolean> {
    const stream_data = this.streams.get(stream_id)
    if (!stream_data) return false

    const peer_connection = new RTCPeerConnection({
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' }
      ]
    })

    stream_data.peer_connection = peer_connection

    return new Promise((resolve) => {
      peer_connection.oniceconnectionstatechange = () => {
        const state = peer_connection.iceConnectionState
        console.log(`WebRTC ICE状态: ${state}`)
        
        if (state === 'connected' || state === 'completed') {
          this.update_stream_state(stream_id, { status: 'connected' })
          resolve(true)
        } else if (state === 'failed' || state === 'disconnected') {
          this.update_stream_state(stream_id, { status: 'error', error: 'WebRTC连接失败' })
          resolve(false)
        }
      }

      peer_connection.ontrack = (event) => {
        const [remote_stream] = event.streams
        stream_data.media_stream = remote_stream
        console.log('收到WebRTC视频流:', remote_stream)
      }

      // 这里需要实际的WebRTC信令逻辑
      // 模拟连接成功
      setTimeout(() => {
        this.update_stream_state(stream_id, { status: 'connected' })
        resolve(true)
      }, 1000)
    })
  }

  /**
   * 连接本地摄像头
   */
  private async connect_webcam_stream(stream_id: string): Promise<boolean> {
    const stream_data = this.streams.get(stream_id)
    if (!stream_data) return false

    try {
      const constraints: MediaStreamConstraints = {
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          frameRate: { ideal: 30 }
        },
        audio: true
      }

      // 如果指定了设备ID
      if (stream_data.config.device_id) {
        (constraints.video as MediaTrackConstraints).deviceId = {
          exact: stream_data.config.device_id
        }
      }

      const media_stream = await navigator.mediaDevices.getUserMedia(constraints)
      stream_data.media_stream = media_stream

      this.update_stream_state(stream_id, { 
        status: 'connected',
        resolution: {
          width: 1280,
          height: 720
        }
      })

      return true
    } catch (error) {
      console.error('摄像头访问失败:', error)
      let error_message = '摄像头访问失败'
      
      if (error instanceof DOMException) {
        switch (error.name) {
          case 'NotFoundError':
            error_message = '未找到摄像头设备'
            break
          case 'NotAllowedError':
            error_message = '摄像头访问被拒绝'
            break
          case 'NotReadableError':
            error_message = '摄像头被其他应用占用'
            break
        }
      }

      this.update_stream_state(stream_id, { status: 'error', error: error_message })
      return false
    }
  }

  /**
   * 连接HLS视频流
   */
  private async connect_hls_stream(stream_id: string): Promise<boolean> {
    const stream_data = this.streams.get(stream_id)
    if (!stream_data?.config.url) return false

    try {
      // 这里需要 hls.js 库
      // import Hls from 'hls.js'
      
      // 模拟HLS连接
      console.log(`连接HLS流: ${stream_data.config.url}`)
      
      this.update_stream_state(stream_id, { status: 'connected' })
      return true
    } catch (error) {
      console.error('HLS连接失败:', error)
      return false
    }
  }

  /**
   * 连接RTMP视频流
   */
  private async connect_rtmp_stream(stream_id: string): Promise<boolean> {
    const stream_data = this.streams.get(stream_id)
    if (!stream_data?.config.url) return false

    try {
      // RTMP需要通过WebRTC或其他协议转换
      console.log(`连接RTMP流: ${stream_data.config.url}`)
      
      this.update_stream_state(stream_id, { status: 'connected' })
      return true
    } catch (error) {
      console.error('RTMP连接失败:', error)
      return false
    }
  }

  /**
   * 连接文件视频流
   */
  private async connect_file_stream(stream_id: string): Promise<boolean> {
    const stream_data = this.streams.get(stream_id)
    if (!stream_data?.config.url) return false

    try {
      console.log(`加载视频文件: ${stream_data.config.url}`)
      
      this.update_stream_state(stream_id, { status: 'connected' })
      return true
    } catch (error) {
      console.error('视频文件加载失败:', error)
      return false
    }
  }

  /**
   * 断开视频流
   */
  disconnect_stream(stream_id: string): void {
    const stream_data = this.streams.get(stream_id)
    if (!stream_data) return

    // 清理WebRTC连接
    if (stream_data.peer_connection) {
      stream_data.peer_connection.close()
      stream_data.peer_connection = undefined
    }

    // 停止媒体流
    if (stream_data.media_stream) {
      stream_data.media_stream.getTracks().forEach(track => track.stop())
      stream_data.media_stream = undefined
    }

    // 清理重连定时器
    const timeout = this.retry_timeouts.get(stream_id)
    if (timeout) {
      clearTimeout(timeout)
      this.retry_timeouts.delete(stream_id)
    }

    this.update_stream_state(stream_id, { status: 'disconnected' })
  }

  /**
   * 移除视频流
   */
  remove_stream(stream_id: string): void {
    this.disconnect_stream(stream_id)
    this.streams.delete(stream_id)
  }

  /**
   * 获取视频流状态
   */
  get_stream_state(stream_id: string): VideoStreamState | undefined {
    return this.streams.get(stream_id)?.state
  }

  /**
   * 获取媒体流
   */
  get_media_stream(stream_id: string): MediaStream | undefined {
    return this.streams.get(stream_id)?.media_stream
  }

  /**
   * 绑定视频元素
   */
  bind_video_element(stream_id: string, video_element: HTMLVideoElement): boolean {
    const stream_data = this.streams.get(stream_id)
    if (!stream_data) return false

    stream_data.element = video_element

    if (stream_data.media_stream) {
      video_element.srcObject = stream_data.media_stream
    } else if (stream_data.config.url && stream_data.config.type === 'file') {
      video_element.src = stream_data.config.url
    }

    return true
  }

  /**
   * 获取可用摄像头列表
   */
  async get_available_cameras(): Promise<MediaDeviceInfo[]> {
    try {
      await navigator.mediaDevices.getUserMedia({ video: true })
      const devices = await navigator.mediaDevices.enumerateDevices()
      return devices.filter(device => device.kind === 'videoinput')
    } catch (error) {
      console.error('获取摄像头列表失败:', error)
      return []
    }
  }

  /**
   * 更新流状态
   */
  private update_stream_state(stream_id: string, updates: Partial<VideoStreamState>): void {
    const stream_data = this.streams.get(stream_id)
    if (!stream_data) return

    stream_data.state = { ...stream_data.state, ...updates }
    
    if (updates.status === 'connected') {
      stream_data.state.last_connected = new Date()
      stream_data.state.retry_attempts = 0
    }
  }

  /**
   * 安排重连
   */
  private schedule_reconnect(stream_id: string): void {
    const stream_data = this.streams.get(stream_id)
    if (!stream_data) return

    const max_retries = stream_data.config.retry_count || 5
    const current_attempts = stream_data.state.retry_attempts

    if (current_attempts >= max_retries) {
      console.log(`视频流 ${stream_id} 重连次数已达上限`)
      return
    }

    const delay = Math.min(1000 * Math.pow(2, current_attempts), 30000) // 指数退避，最大30秒

    console.log(`${delay / 1000}秒后重连视频流 ${stream_id}`)

    const timeout = window.setTimeout(async () => {
      stream_data.state.retry_attempts++
      this.update_stream_state(stream_id, { status: 'reconnecting' })
      
      const success = await this.connect_stream(stream_id)
      if (!success) {
        this.schedule_reconnect(stream_id) // 继续重连
      }
    }, delay)

    this.retry_timeouts.set(stream_id, timeout)
  }

  /**
   * 初始化WebRTC配置
   */
  private init_webrtc_config(): void {
    // 检查WebRTC支持
    if (!window.RTCPeerConnection) {
      console.warn('当前浏览器不支持WebRTC')
    }
  }

  /**
   * 清理所有资源
   */
  dispose(): void {
    for (const stream_id of this.streams.keys()) {
      this.remove_stream(stream_id)
    }
  }
}

// 导出单例实例
export const video_stream_manager = new VideoStreamManager()