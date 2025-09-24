<!--
  增强版视频播放器组件
  支持多种视频源和智能连接管理
-->
<template>
  <div class="enhanced-video-player" :class="{ 'player-error': has_error }">
    <!-- 视频元素 -->
    <video
      ref="video_element"
      class="video-element"
      :autoplay="autoplay"
      :muted="muted"
      :loop="loop"
      :controls="show_controls"
      @loadstart="on_load_start"
      @loadedmetadata="on_loaded_metadata"
      @canplay="on_can_play"
      @error="on_error"
      @click="$emit('click')"
    />

    <!-- 加载状态覆盖层 - 只在有真实URL时显示 -->
    <div v-if="is_loading && props.stream_config.url" class="loading-overlay">
      <div class="loading-content">
        <v-progress-circular
          indeterminate
          color="primary"
          size="48"
        />
        <p class="text-body-2 mt-3">{{ loading_message }}</p>
      </div>
    </div>

    <!-- 错误状态覆盖层 - 只在有真实URL时显示 -->
    <div v-if="has_error && props.stream_config.url" class="error-overlay">
      <div class="error-content">
        <v-icon size="64" color="error">mdi-alert-circle</v-icon>
        <h3 class="text-h6 mt-3">连接失败</h3>
        <p class="text-body-2 mt-2 text-grey-darken-1">{{ error_message }}</p>
        
        <div class="error-actions mt-4">
          <v-btn
            @click="retry_connection"
            :loading="is_retrying"
            color="primary"
            variant="outlined"
            prepend-icon="mdi-refresh"
            class="mr-2"
          >
            重新连接
          </v-btn>
          
          <v-btn
            v-if="stream_config.type === 'webcam'"
            @click="request_camera_permission"
            color="success"
            variant="outlined"
            prepend-icon="mdi-camera"
          >
            授权摄像头
          </v-btn>
        </div>
        
        <!-- 重连进度 -->
        <div v-if="retry_attempts > 0" class="retry-info mt-3">
          <v-progress-linear
            :model-value="(retry_attempts / max_retries) * 100"
            color="warning"
            height="4"
            rounded
          />
          <p class="text-caption mt-1">
            重连尝试: {{ retry_attempts }}/{{ max_retries }}
          </p>
        </div>
      </div>
    </div>

    <!-- 视频信息叠加 -->
    <div v-if="show_info && stream_state" class="video-info-overlay">
      <div class="video-info-card">
        <div class="info-item">
          <v-icon size="small" class="mr-1">mdi-connection</v-icon>
          <span>{{ format_status(stream_state.status) }}</span>
        </div>
        
        <div v-if="stream_state.resolution" class="info-item">
          <v-icon size="small" class="mr-1">mdi-monitor</v-icon>
          <span>{{ stream_state.resolution.width }}×{{ stream_state.resolution.height }}</span>
        </div>
        
        <div v-if="stream_state.bandwidth" class="info-item">
          <v-icon size="small" class="mr-1">mdi-speedometer</v-icon>
          <span>{{ format_bandwidth(stream_state.bandwidth) }}</span>
        </div>
      </div>
    </div>

    <!-- 状态指示器 -->
    <div class="status-indicator" :class="status_class">
      <v-icon size="small">{{ status_icon }}</v-icon>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { 
  video_stream_manager, 
  type VideoStreamConfig,
  type VideoStreamState 
} from '../../utils/VideoStreamManager'

interface Props {
  stream_config: VideoStreamConfig
  autoplay?: boolean
  muted?: boolean
  loop?: boolean
  show_controls?: boolean
  show_info?: boolean
}

interface Emits {
  (e: 'click'): void
  (e: 'stream_ready', stream: MediaStream): void
  (e: 'stream_error', error: string): void
  (e: 'state_change', state: VideoStreamState): void
}

const props = withDefaults(defineProps<Props>(), {
  autoplay: true,
  muted: true,
  loop: false,
  show_controls: false,
  show_info: false
})

const emit = defineEmits<Emits>()

// 组件状态
const video_element = ref<HTMLVideoElement>()
const is_loading = ref(false)
const has_error = ref(false)
const error_message = ref('')
const is_retrying = ref(false)
const retry_attempts = ref(0)
const max_retries = ref(5)
const stream_state = ref<VideoStreamState>()

// 计算属性
const loading_message = computed(() => {
  if (!stream_state.value) return '初始化中...'
  
  switch (stream_state.value.status) {
    case 'connecting':
      return `连接${format_stream_type()}中...`
    case 'reconnecting':
      return `重连中... (${retry_attempts.value}/${max_retries.value})`
    default:
      return '加载中...'
  }
})

const status_class = computed(() => {
  if (!stream_state.value) return 'status-disconnected'
  
  switch (stream_state.value.status) {
    case 'connected':
      return 'status-connected'
    case 'connecting':
    case 'reconnecting':
      return 'status-connecting'
    case 'error':
      return 'status-error'
    default:
      return 'status-disconnected'
  }
})

const status_icon = computed(() => {
  if (!stream_state.value) return 'mdi-circle'
  
  switch (stream_state.value.status) {
    case 'connected':
      return 'mdi-check-circle'
    case 'connecting':
    case 'reconnecting':
      return 'mdi-loading'
    case 'error':
      return 'mdi-alert-circle'
    default:
      return 'mdi-circle-outline'
  }
})

// 方法
const format_stream_type = (): string => {
  switch (props.stream_config.type) {
    case 'webcam':
      return '摄像头'
    case 'webrtc':
      return 'WebRTC流'
    case 'hls':
      return 'HLS流'
    case 'rtmp':
      return 'RTMP流'
    case 'file':
      return '视频文件'
    default:
      return '视频流'
  }
}

const format_status = (status: string): string => {
  const status_map = {
    'connected': '已连接',
    'connecting': '连接中',
    'reconnecting': '重连中',
    'disconnected': '已断开',
    'error': '连接失败'
  }
  return status_map[status as keyof typeof status_map] || status
}

const format_bandwidth = (bandwidth: number): string => {
  if (bandwidth < 1024) return `${bandwidth} B/s`
  if (bandwidth < 1024 * 1024) return `${(bandwidth / 1024).toFixed(1)} KB/s`
  return `${(bandwidth / (1024 * 1024)).toFixed(1)} MB/s`
}

const init_stream = async () => {
  is_loading.value = true
  has_error.value = false
  
  try {
    // 添加视频流到管理器
    const success = await video_stream_manager.add_stream(props.stream_config)
    
    if (success && video_element.value) {
      // 绑定视频元素
      video_stream_manager.bind_video_element(props.stream_config.id, video_element.value)
      
      // 获取媒体流
      const media_stream = video_stream_manager.get_media_stream(props.stream_config.id)
      if (media_stream) {
        emit('stream_ready', media_stream)
      }
    }
  } catch (error) {
    console.error('初始化视频流失败:', error)
    show_error(error instanceof Error ? error.message : '初始化失败')
  } finally {
    is_loading.value = false
  }
}

const retry_connection = async () => {
  is_retrying.value = true
  has_error.value = false
  
  try {
    const success = await video_stream_manager.connect_stream(props.stream_config.id)
    if (!success) {
      show_error('重连失败')
    }
  } catch (error) {
    show_error(error instanceof Error ? error.message : '重连失败')
  } finally {
    is_retrying.value = false
  }
}

const request_camera_permission = async () => {
  try {
    await navigator.mediaDevices.getUserMedia({ video: true })
    retry_connection()
  } catch (error) {
    show_error('摄像头权限被拒绝')
  }
}

const show_error = (message: string) => {
  has_error.value = true
  error_message.value = message
  emit('stream_error', message)
}

const update_state = () => {
  const state = video_stream_manager.get_stream_state(props.stream_config.id)
  if (state) {
    stream_state.value = state
    retry_attempts.value = state.retry_attempts
    
    if (state.status === 'error') {
      show_error(state.error || '连接失败')
    } else if (state.status === 'connected') {
      has_error.value = false
      is_loading.value = false
    } else if (state.status === 'connecting' || state.status === 'reconnecting') {
      is_loading.value = true
      has_error.value = false
    }
    
    emit('state_change', state)
  }
}

// 视频事件处理
const on_load_start = () => {
  console.log('视频开始加载')
}

const on_loaded_metadata = () => {
  console.log('视频元数据加载完成')
  if (video_element.value) {
    const { videoWidth, videoHeight } = video_element.value
    console.log(`视频尺寸: ${videoWidth}×${videoHeight}`)
  }
}

const on_can_play = () => {
  console.log('视频可以播放')
  is_loading.value = false
}

const on_error = (event: Event) => {
  console.error('视频播放错误:', event)
  show_error('视频播放失败')
}

// 状态轮询
let state_timer: number | null = null

const start_state_polling = () => {
  state_timer = window.setInterval(() => {
    update_state()
  }, 1000)
}

const stop_state_polling = () => {
  if (state_timer) {
    clearInterval(state_timer)
    state_timer = null
  }
}

// 监听配置变化
watch(() => props.stream_config, () => {
  init_stream()
}, { deep: true })

// 生命周期
onMounted(() => {
  init_stream()
  start_state_polling()
})

onUnmounted(() => {
  stop_state_polling()
  video_stream_manager.remove_stream(props.stream_config.id)
})
</script>

<style scoped>
.enhanced-video-player {
  position: relative;
  width: 100%;
  height: 100%;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.video-element {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.loading-overlay,
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.8);
}

.loading-content,
.error-content {
  text-align: center;
  color: white;
}

.error-actions {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.retry-info {
  max-width: 200px;
  margin: 0 auto;
}

.video-info-overlay {
  position: absolute;
  top: 8px;
  right: 8px;
  pointer-events: none;
}

.video-info-card {
  background: rgba(0, 0, 0, 0.8);
  border-radius: 6px;
  padding: 8px 12px;
  color: white;
  font-size: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.status-indicator {
  position: absolute;
  top: 8px;
  left: 8px;
  padding: 4px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
}

.status-connected {
  color: #4caf50;
}

.status-connecting {
  color: #ff9800;
  animation: pulse 1.5s infinite;
}

.status-error {
  color: #f44336;
}

.status-disconnected {
  color: #9e9e9e;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.player-error {
  border: 2px solid #f44336;
}
</style>