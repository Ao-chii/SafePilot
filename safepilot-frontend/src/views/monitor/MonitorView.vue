<!--
  实时监控中心页面 - Version 2.0 专业版
  SafePilot 核心功能：多路视频流监控 + 实时告警
-->
<template>
  <div class="monitor-view">
    <!-- 顶部控制栏 -->
    <div class="monitor-header">
      <div class="d-flex align-center justify-space-between">
        <div class="d-flex align-center">
          <div class="monitor-title">
            <h1 class="text-h4 font-weight-bold">
              <v-icon class="mr-2" color="primary">mdi-video-box</v-icon>
              SafePilot 实时监控中心
            </h1>
          </div>
          
          <!-- 告警状态指示 -->
          <div class="alert-status ml-6">
            <v-chip
              :color="alert_stats.critical > 0 ? 'error' : alert_stats.warning > 0 ? 'warning' : 'success'"
              variant="elevated"
              class="mr-2"
            >
              <v-icon start>
                {{ alert_stats.critical > 0 ? 'mdi-alert-circle' : alert_stats.warning > 0 ? 'mdi-alert' : 'mdi-check-circle' }}
              </v-icon>
              {{ alert_stats.critical + alert_stats.warning }}个告警
            </v-chip>
          </div>
        </div>

        <!-- 右侧控制按钮 -->
        <div class="d-flex align-center">
          <v-btn
            @click="toggle_fullscreen"
            icon
            variant="text"
            class="mr-2"
            :title="is_fullscreen ? '退出全屏' : '进入全屏'"
          >
            <v-icon>{{ is_fullscreen ? 'mdi-fullscreen-exit' : 'mdi-fullscreen' }}</v-icon>
          </v-btn>
          
          <v-btn
            @click="show_settings = true"
            icon
            variant="text"
            title="监控设置"
          >
            <v-icon>mdi-cog</v-icon>
          </v-btn>
        </div>
      </div>
    </div>

    <!-- 主监控区域 -->
    <div class="monitor-content">
      <v-row no-gutters class="h-100">
        <!-- 视频网格区域 -->
        <v-col :cols="show_alert_panel ? 9 : 12" class="video-section">
          <v-card class="video-grid-container h-100" elevation="2">
            <!-- 视频网格切换控制 -->
            <div class="video-controls">
              <v-btn-toggle
                v-model="grid_layout"
                mandatory
                variant="outlined"
                density="compact"
                class="mr-4"
              >
                <v-btn value="2x2">2×2</v-btn>
                <v-btn value="3x3">3×3</v-btn>
                <v-btn value="4x4">4×4</v-btn>
              </v-btn-toggle>

              <v-btn
                @click="toggle_alert_panel"
                :variant="show_alert_panel ? 'elevated' : 'outlined'"
                size="small"
                :color="show_alert_panel ? 'primary' : ''"
              >
                <v-icon start>mdi-bell</v-icon>
                告警面板
              </v-btn>

              <!-- 视频流状态 -->
              <div class="video-status ml-4">
                <span class="text-caption">
                  在线: {{ online_streams }}/{{ total_streams }}
                </span>
              </div>
            </div>

            <!-- 视频网格 -->
            <div 
              class="video-grid" 
              :class="`grid-${grid_layout}`"
              :style="{ height: 'calc(100% - 60px)' }"
            >
              <div
                v-for="stream in displayed_streams"
                :key="stream.id"
                class="video-item"
                :class="{ 
                  'video-expanded': expanded_video === stream.id,
                  'has-alert': stream.has_alert 
                }"
                @click="toggle_video_expand(stream.id)"
              >
                <!-- 增强版视频播放器 -->
                <div class="video-player">
                  <EnhancedVideoPlayer
                    :stream_config="get_stream_config(stream)"
                    :show_info="true"
                    @click="toggle_video_expand(stream.id)"
                    @stream_ready="on_stream_ready(stream.id, $event)"
                    @stream_error="on_stream_error(stream.id, $event)"
                    @state_change="on_stream_state_change(stream.id, $event)"
                  />

                  <!-- AI分析结果叠加 -->
                  <div class="video-overlay">
                    <!-- 底部：AI分析结果 -->
                    <div class="video-info bottom-left" v-if="stream.ai_analysis">
                      <div class="ai-analysis">
                        <v-chip
                          :color="get_alert_color(stream.ai_analysis.type)"
                          size="small"
                          variant="elevated"
                        >
                          <v-icon start size="small">
                            {{ get_alert_icon(stream.ai_analysis.type) }}
                          </v-icon>
                          {{ stream.ai_analysis.type }}
                        </v-chip>
                        <span class="confidence ml-2">
                          {{ Math.round(stream.ai_analysis.confidence * 100) }}%
                        </span>
                      </div>
                    </div>

                    <!-- 放大按钮 -->
                    <div class="video-info top-right">
                      <v-btn
                        @click.stop="toggle_video_expand(stream.id)"
                        icon
                        size="small"
                        variant="elevated"
                        color="primary"
                        class="expand-btn"
                      >
                        <v-icon>mdi-arrow-expand</v-icon>
                      </v-btn>
                    </div>

                    <!-- 告警动画效果 -->
                    <div 
                      v-if="stream.has_alert" 
                      class="alert-animation"
                    />
                  </div>
                </div>
              </div>
            </div>
          </v-card>
        </v-col>

        <!-- 告警控制台 -->
        <v-col v-if="show_alert_panel" cols="3" class="alert-section">
          <v-card class="alert-panel h-100" elevation="2">
            <v-card-title class="d-flex align-center justify-space-between">
              <span>告警控制台</span>
              <v-btn
                @click="mute_alerts = !mute_alerts"
                :icon="mute_alerts ? 'mdi-volume-off' : 'mdi-volume-high'"
                size="small"
                variant="text"
                :color="mute_alerts ? 'error' : 'primary'"
              />
            </v-card-title>

            <v-card-text class="pa-0">
              <!-- 告警统计 -->
              <div class="alert-summary pa-4">
                <v-row no-gutters>
                  <v-col cols="4" class="text-center">
                    <div class="alert-count critical">{{ alert_stats.critical }}</div>
                    <div class="text-caption">严重</div>
                  </v-col>
                  <v-col cols="4" class="text-center">
                    <div class="alert-count warning">{{ alert_stats.warning }}</div>
                    <div class="text-caption">警告</div>
                  </v-col>
                  <v-col cols="4" class="text-center">
                    <div class="alert-count info">{{ alert_stats.info }}</div>
                    <div class="text-caption">提醒</div>
                  </v-col>
                </v-row>
              </div>

              <v-divider />

              <!-- 实时告警列表 -->
              <div class="alert-list">
                <v-list density="compact">
                  <v-list-item
                    v-for="alert in recent_alerts"
                    :key="alert.id"
                    :class="`alert-item-${alert.level}`"
                    class="alert-item"
                  >
                    <template #prepend>
                      <v-icon :color="get_alert_color(alert.type)">
                        {{ get_alert_icon(alert.type) }}
                      </v-icon>
                    </template>

                    <v-list-item-title>{{ alert.type }}</v-list-item-title>
                    <v-list-item-subtitle>
                      {{ alert.device_name }} - {{ alert.driver_name }}
                    </v-list-item-subtitle>
                    <v-list-item-subtitle>
                      {{ format_time_ago(alert.timestamp) }}
                    </v-list-item-subtitle>

                    <template #append>
                      <v-btn
                        @click="handle_alert(alert)"
                        icon="mdi-check"
                        size="x-small"
                        variant="text"
                      />
                    </template>
                  </v-list-item>
                </v-list>
              </div>
            </v-card-text>

            <v-card-actions>
              <v-btn
                @click="view_all_alerts"
                variant="outlined"
                size="small"
                block
              >
                查看所有告警
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </div>

    <!-- 底部状态栏 -->
    <div class="status-bar">
      <v-card class="status-card" elevation="1">
        <div class="d-flex align-center justify-space-between pa-3">
          <div class="status-item">
            <v-icon color="success" class="mr-1">mdi-cellphone-link</v-icon>
            <span>在线设备: {{ system_stats.online_devices }}/{{ system_stats.total_devices }}</span>
          </div>
          
          <div class="status-item">
            <v-icon color="info" class="mr-1">mdi-account-group</v-icon>
            <span>活跃司机: {{ system_stats.active_drivers }}</span>
          </div>
          
          <div class="status-item">
            <v-icon color="warning" class="mr-1">mdi-alert-circle</v-icon>
            <span>今日告警: {{ system_stats.daily_alerts }}</span>
          </div>
          
          <div class="status-item">
            <v-icon color="primary" class="mr-1">mdi-refresh</v-icon>
            <span>刷新: {{ format_time_ago(last_update) }}</span>
          </div>
          
          <div class="status-item">
            <v-icon :color="network_status.color" class="mr-1">{{ network_status.icon }}</v-icon>
            <span>网络: {{ network_status.text }}</span>
          </div>
        </div>
      </v-card>
    </div>

    <!-- 视频放大弹窗 -->
    <v-dialog 
      v-model="video_fullscreen_dialog" 
      fullscreen
      transition="dialog-bottom-transition"
      class="video-fullscreen-dialog"
    >
      <v-card v-if="selected_video" class="video-fullscreen-card">
        <!-- 顶部控制栏 -->
        <v-app-bar
          color="rgba(0,0,0,0.8)"
          dark
          flat
          class="video-fullscreen-toolbar"
        >
          <v-toolbar-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-video-box</v-icon>
            {{ selected_video.device_name }}
            <v-chip
              :color="selected_video.is_online ? 'success' : 'error'"
              size="small"
              class="ml-3"
            >
              {{ selected_video.is_online ? '在线' : '离线' }}
            </v-chip>
          </v-toolbar-title>
          
          <v-spacer />
          
          <!-- 控制按钮 -->
          <div class="d-flex align-center">
            <v-btn
              @click="toggle_video_recording"
              :icon="is_recording ? 'mdi-stop' : 'mdi-record'"
              :color="is_recording ? 'error' : 'primary'"
              variant="text"
              class="mr-2"
              :title="is_recording ? '停止录制' : '开始录制'"
            />
            
            <v-btn
              @click="take_screenshot"
              icon="mdi-camera"
              variant="text"
              class="mr-2"
              title="截图"
            />
            
            <v-btn
              @click="toggle_video_mute"
              :icon="is_video_muted ? 'mdi-volume-off' : 'mdi-volume-high'"
              variant="text"
              class="mr-2"
              :title="is_video_muted ? '取消静音' : '静音'"
            />
            
            <v-btn
              @click="close_video_fullscreen"
              icon="mdi-close"
              variant="text"
              title="关闭"
            />
          </div>
        </v-app-bar>

        <!-- 视频主体区域 -->
        <v-card-text class="video-fullscreen-content pa-0">
          <div class="video-fullscreen-player">
            <!-- 视频播放器 -->
            <video
              v-if="selected_video.stream_url"
              :src="selected_video.stream_url"
              autoplay
              :muted="is_video_muted"
              loop
              class="fullscreen-video-element"
              @loadedmetadata="on_video_loaded"
              @error="on_video_error"
            />
            
            <!-- 无视频流时的占位 -->
            <div v-else class="video-fullscreen-placeholder">
              <div class="placeholder-content">
                <v-icon size="120" color="grey-lighten-2">mdi-video-off</v-icon>
                <h2 class="text-h4 mt-4 text-grey-lighten-1">视频流断开</h2>
                <p class="text-body-1 text-grey-darken-1 mt-2">
                  设备: {{ selected_video.device_name }}
                </p>
                <v-btn 
                  @click="reconnect_video_stream"
                  variant="outlined"
                  color="primary"
                  class="mt-4"
                  prepend-icon="mdi-refresh"
                >
                  重新连接
                </v-btn>
              </div>
            </div>

            <!-- 视频信息叠加层 -->
            <div class="video-fullscreen-overlay">
              <!-- 左上角：设备详细信息 -->
              <div class="fullscreen-info top-left">
                <v-card class="info-card" elevation="4">
                  <v-card-text class="pa-3">
                    <div class="d-flex align-center mb-2">
                      <v-icon class="mr-2" color="primary">mdi-video</v-icon>
                      <span class="font-weight-bold">{{ selected_video.device_name }}</span>
                    </div>
                    
                    <div class="info-row" v-if="selected_video.driver_name">
                      <v-icon size="small" class="mr-2">mdi-account</v-icon>
                      <span>司机: {{ selected_video.driver_name }}</span>
                    </div>
                    
                    <div class="info-row">
                      <v-icon size="small" class="mr-2">mdi-identifier</v-icon>
                      <span>设备: {{ selected_video.device_id }}</span>
                    </div>
                    
                    <div class="info-row">
                      <v-icon 
                        size="small" 
                        class="mr-2"
                        :color="selected_video.is_online ? 'success' : 'error'"
                      >
                        {{ selected_video.is_online ? 'mdi-check-circle' : 'mdi-alert-circle' }}
                      </v-icon>
                      <span>状态: {{ selected_video.is_online ? '在线' : '离线' }}</span>
                    </div>
                    
                    <div class="info-row">
                      <v-icon size="small" class="mr-2">mdi-clock</v-icon>
                      <span>{{ format_current_time() }}</span>
                    </div>
                  </v-card-text>
                </v-card>
              </div>

              <!-- 右上角：AI分析结果 -->
              <div class="fullscreen-info top-right" v-if="selected_video.ai_analysis">
                <v-card class="ai-analysis-card" elevation="4">
                  <v-card-text class="pa-3">
                    <div class="d-flex align-center mb-2">
                      <v-icon class="mr-2" color="purple">mdi-brain</v-icon>
                      <span class="font-weight-bold">AI分析</span>
                    </div>
                    
                    <div class="ai-result">
                      <v-chip
                        :color="get_alert_color(selected_video.ai_analysis.type)"
                        size="small"
                        variant="elevated"
                        class="mb-2"
                      >
                        <v-icon start size="small">
                          {{ get_alert_icon(selected_video.ai_analysis.type) }}
                        </v-icon>
                        {{ selected_video.ai_analysis.type }}
                      </v-chip>
                      
                      <div class="confidence-bar mt-2">
                        <div class="d-flex align-center justify-space-between mb-1">
                          <span class="text-caption">置信度</span>
                          <span class="text-caption font-weight-bold">
                            {{ Math.round(selected_video.ai_analysis.confidence * 100) }}%
                          </span>
                        </div>
                        <v-progress-linear
                          :model-value="selected_video.ai_analysis.confidence * 100"
                          :color="get_alert_color(selected_video.ai_analysis.type)"
                          height="6"
                          rounded
                        />
                      </div>
                    </div>
                  </v-card-text>
                </v-card>
              </div>

              <!-- 底部中央：录制状态 -->
              <div class="fullscreen-info bottom-center" v-if="is_recording">
                <v-card class="recording-indicator" elevation="4">
                  <v-card-text class="pa-2 d-flex align-center">
                    <v-icon class="recording-dot mr-2" color="error">mdi-circle</v-icon>
                    <span class="font-weight-bold">录制中</span>
                    <span class="ml-2 text-caption">{{ format_recording_time() }}</span>
                  </v-card-text>
                </v-card>
              </div>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- 设置对话框 -->
    <v-dialog v-model="show_settings" max-width="600">
      <v-card title="监控设置">
        <v-card-text>
          <!-- 设置选项 -->
          <v-switch
            v-model="auto_alert_sound"
            label="自动播放告警声音"
            color="primary"
          />
          <v-switch
            v-model="show_ai_overlay"
            label="显示AI分析叠加"
            color="primary"
          />
          <v-slider
            v-model="refresh_interval"
            label="刷新间隔 (秒)"
            min="1"
            max="10"
            step="1"
            thumb-label
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="show_settings = false">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { monitor_api } from '../../api'
import EnhancedVideoPlayer from '../../components/common/EnhancedVideoPlayer.vue'
import { type VideoStreamConfig, type VideoStreamState } from '../../utils/VideoStreamManager'
import { get_websocket_instance, type AlertMessage, type StreamStatusMessage } from '../../utils/WebSocketManager'

const router = useRouter()

// 基础状态
const show_alert_panel = ref(true)
const show_settings = ref(false)
const is_fullscreen = ref(false)
const mute_alerts = ref(false)
const grid_layout = ref('2x2')
const expanded_video = ref<string | null>(null)
const last_update = ref(new Date())
const loading = ref(false)

// 视频弹窗相关状态
const video_fullscreen_dialog = ref(false)
const selected_video = ref<VideoStream | null>(null)
const is_recording = ref(false)
const is_video_muted = ref(false)
const recording_start_time = ref<Date | null>(null)

// WebSocket连接状态
const websocket_connected = ref(false)
const websocket_status = ref('disconnected')
const websocket_error = ref('')

// 设置选项
const auto_alert_sound = ref(true)
const show_ai_overlay = ref(true)
const refresh_interval = ref(3)

// 数据状态
interface VideoStream {
  id: string
  device_id: string
  device_name: string
  driver_name: string
  is_online: boolean
  stream_url: string
  has_alert: boolean
  ai_analysis?: {
    type: string
    confidence: number
    level: string
  }
}

interface AlertItem {
  id: string
  type: string
  level: string
  device_name: string
  driver_name: string
  timestamp: Date
  handled: boolean
}

const video_streams = ref<VideoStream[]>([])
const recent_alerts = ref<AlertItem[]>([])
const system_stats = ref({
  online_devices: 0,
  total_devices: 0,
  active_drivers: 0,
  daily_alerts: 0
})

// 计算属性
const displayed_streams = computed(() => {
  const max_streams = grid_layout.value === '2x2' ? 4 : grid_layout.value === '3x3' ? 9 : 16
  return video_streams.value.slice(0, max_streams)
})

const online_streams = computed(() => 
  displayed_streams.value.filter(s => s.is_online).length
)

const total_streams = computed(() => displayed_streams.value.length)

const alert_stats = computed(() => {
  const stats = { critical: 0, warning: 0, info: 0 }
  recent_alerts.value.forEach(alert => {
    if (alert.level === 'critical') stats.critical++
    else if (alert.level === 'warning') stats.warning++
    else stats.info++
  })
  return stats
})

const network_status = computed(() => {
  return {
    text: '良好',
    color: 'success',
    icon: 'mdi-wifi'
  }
})

// 数据加载方法
const load_video_streams = async () => {
  try {
    const response = await monitor_api.get_video_streams()
    video_streams.value = response.data.streams || []
  } catch (error: unknown) {
    console.error('加载视频流失败:', error)
    // 使用模拟数据作为fallback
    video_streams.value = [
      {
        id: 'stream-001',
        device_id: 'CAM001',
        device_name: '车辆001-内',
        driver_name: '张三',
        is_online: true,
        stream_url: '',
        has_alert: true,
        ai_analysis: {
          type: '疲劳驾驶',
          confidence: 0.85,
          level: 'critical'
        }
      },
      {
        id: 'stream-002',
        device_id: 'CAM002',
        device_name: '车辆001-外',
        driver_name: '',
        is_online: true,
        stream_url: '',
        has_alert: false,
        ai_analysis: {
          type: '正常行驶',
          confidence: 0.95,
          level: 'normal'
        }
      },
      {
        id: 'stream-003',
        device_id: 'CAM003',
        device_name: '车辆002-内',
        driver_name: '李四',
        is_online: true,
        stream_url: '',
        has_alert: true,
        ai_analysis: {
          type: '使用手机',
          confidence: 0.92,
          level: 'warning'
        }
      },
      {
        id: 'stream-004',
        device_id: 'CAM004',
        device_name: '车辆002-外',
        driver_name: '',
        is_online: false,
        stream_url: '',
        has_alert: false,
        ai_analysis: undefined
      }
    ]
  }
}

const load_real_time_alerts = async () => {
  try {
    const response = await monitor_api.get_real_time_alerts({ limit: 20 })
    recent_alerts.value = response.data.alerts || []
  } catch (error: unknown) {
    console.error('加载实时告警失败:', error)
    // 使用模拟数据作为fallback
    recent_alerts.value = [
      {
        id: 'alert-001',
        type: '疲劳驾驶',
        level: 'critical',
        device_name: '车辆001',
        driver_name: '张三',
        timestamp: new Date(Date.now() - 2 * 60 * 1000),
        handled: false
      },
      {
        id: 'alert-002',
        type: '使用手机',
        level: 'warning',
        device_name: '车辆002',
        driver_name: '李四',
        timestamp: new Date(Date.now() - 5 * 60 * 1000),
        handled: false
      }
    ]
  }
}

const load_system_status = async () => {
  try {
    const response = await monitor_api.get_system_status()
    system_stats.value = response.data || system_stats.value
  } catch (error: unknown) {
    console.error('加载系统状态失败:', error)
    // 使用模拟数据作为fallback
    system_stats.value = {
      online_devices: 8,
      total_devices: 10,
      active_drivers: 15,
      daily_alerts: 23
    }
  }
}

const load_all_data = async () => {
  loading.value = true
  try {
    await Promise.all([
      load_video_streams(),
      load_real_time_alerts(),
      load_system_status()
    ])
    last_update.value = new Date()
  } finally {
    loading.value = false
  }
}

// 交互方法
const toggle_alert_panel = () => {
  show_alert_panel.value = !show_alert_panel.value
}

const toggle_fullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    is_fullscreen.value = true
  } else {
    document.exitFullscreen()
    is_fullscreen.value = false
  }
}

const toggle_video_expand = (stream_id: string) => {
  const stream = video_streams.value.find(s => s.id === stream_id)
  if (stream) {
    selected_video.value = stream
    video_fullscreen_dialog.value = true
  }
}

const get_alert_color = (type: string): string => {
  const critical_types = ['疲劳驾驶', '危险驾驶']
  const warning_types = ['使用手机', '分心驾驶', '抽烟']
  
  if (critical_types.includes(type)) return 'error'
  if (warning_types.includes(type)) return 'warning'
  return 'success'
}

const get_alert_icon = (type: string): string => {
  const icon_map: Record<string, string> = {
    '疲劳驾驶': 'mdi-sleep',
    '使用手机': 'mdi-cellphone',
    '分心驾驶': 'mdi-eye-off',
    '抽烟': 'mdi-smoking',
    '正常行驶': 'mdi-check-circle'
  }
  return icon_map[type] || 'mdi-alert-circle'
}

const format_time_ago = (timestamp: Date): string => {
  const now = new Date()
  const diff = now.getTime() - timestamp.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return timestamp.toLocaleDateString()
}

const handle_alert = async (alert: AlertItem) => {
  try {
    await monitor_api.handle_alert(alert.id, 'acknowledge')
    alert.handled = true
    console.log('告警已处理:', alert)
  } catch (error: unknown) {
    console.error('处理告警失败:', error)
  }
}

const view_all_alerts = () => {
  router.push('/events')
}

// 弹窗相关方法
const close_video_fullscreen = () => {
  video_fullscreen_dialog.value = false
  selected_video.value = null
  if (is_recording.value) {
    toggle_video_recording()
  }
}

const toggle_video_recording = () => {
  if (is_recording.value) {
    is_recording.value = false
    recording_start_time.value = null
    console.log('停止录制')
  } else {
    is_recording.value = true
    recording_start_time.value = new Date()
    console.log('开始录制')
  }
}

const take_screenshot = () => {
  if (selected_video.value) {
    console.log('截图:', selected_video.value.device_name)
    // 实际项目中会调用API或使用Canvas API进行截图
  }
}

const toggle_video_mute = () => {
  is_video_muted.value = !is_video_muted.value
}

const reconnect_video_stream = () => {
  if (selected_video.value) {
    console.log('重新连接视频流:', selected_video.value.device_id)
    // 实际项目中会调用API重新连接视频流
  }
}

const on_video_loaded = (event: Event) => {
  console.log('视频加载完成:', event)
}

const on_video_error = (event: Event) => {
  console.error('视频加载错误:', event)
}

const format_current_time = (): string => {
  return new Date().toLocaleString('zh-CN')
}

const format_recording_time = (): string => {
  if (!recording_start_time.value) return '00:00'
  
  const now = new Date()
  const diff = now.getTime() - recording_start_time.value.getTime()
  const minutes = Math.floor(diff / 60000)
  const seconds = Math.floor((diff % 60000) / 1000)
  
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
}

// 增强视频播放器相关方法
const get_stream_config = (stream: VideoStream): VideoStreamConfig => {
  // 对于模拟数据，直接使用webcam类型避免文件加载问题
  let stream_type: VideoStreamConfig['type'] = 'webcam'
  
  // 根据设备名称判断类型
  if (stream.stream_url?.includes('webrtc')) {
    stream_type = 'webrtc'
  } else if (stream.stream_url?.includes('.m3u8')) {
    stream_type = 'hls'
  } else if (stream.stream_url?.includes('rtmp')) {
    stream_type = 'rtmp'
  } else if (stream.stream_url && stream.stream_url.startsWith('http')) {
    stream_type = 'file'
  }

  return {
    id: stream.id,
    type: stream_type,
    url: stream.stream_url || undefined,
    device_id: stream.device_id,
    quality: 'auto',
    retry_count: 3,
    timeout: 10000
  }
}

const on_stream_ready = (stream_id: string, media_stream: MediaStream) => {
  console.log(`视频流 ${stream_id} 准备就绪:`, media_stream)
  
  // 更新流状态
  const stream = video_streams.value.find(s => s.id === stream_id)
  if (stream) {
    stream.is_online = true
  }
}

const on_stream_error = (stream_id: string, error: string) => {
  console.error(`视频流 ${stream_id} 错误:`, error)
  
  // 更新流状态
  const stream = video_streams.value.find(s => s.id === stream_id)
  if (stream) {
    stream.is_online = false
  }
}

const on_stream_state_change = (stream_id: string, state: VideoStreamState) => {
  console.log(`视频流 ${stream_id} 状态变更:`, state)
  
  // 可以根据状态更新UI或发送通知
  if (state.status === 'error') {
    console.warn(`视频流连接失败: ${state.error}`)
  }
}

// WebSocket连接管理
let websocket_instance: ReturnType<typeof get_websocket_instance> | null = null

const init_websocket = async () => {
  try {
    // 实际项目中这里应该从配置或环境变量获取WebSocket URL
    const ws_url = import.meta.env.VITE_WEBSOCKET_URL || 'ws://localhost:8080/ws'
    
    websocket_instance = get_websocket_instance(ws_url)
    
    // 订阅连接状态事件
    websocket_instance.on('connected', () => {
      websocket_connected.value = true
      websocket_status.value = 'connected'
      websocket_error.value = ''
      console.log('WebSocket连接成功')
    })
    
    websocket_instance.on('disconnected', () => {
      websocket_connected.value = false
      websocket_status.value = 'disconnected'
      console.log('WebSocket连接断开')
    })
    
    websocket_instance.on('reconnecting', (data: { attempt: number }) => {
      websocket_status.value = 'reconnecting'
      console.log(`WebSocket重连中 (${data.attempt})`)
    })
    
    websocket_instance.on('error', (data: { event: Event }) => {
      websocket_connected.value = false
      websocket_status.value = 'error'
      websocket_error.value = 'WebSocket连接错误'
      console.error('WebSocket错误:', data.event)
    })

    // 订阅实时告警
    websocket_instance.subscribe_alerts((alert: AlertMessage) => {
      console.log('收到实时告警:', alert)
      
      // 添加到告警列表
      recent_alerts.value.unshift({
        id: alert.id,
        type: alert.type,
        level: alert.level,
        device_name: alert.device_name,
        driver_name: alert.driver_name || '',
        timestamp: new Date(alert.timestamp),
        handled: false
      })
      
      // 限制告警列表长度
      if (recent_alerts.value.length > 50) {
        recent_alerts.value = recent_alerts.value.slice(0, 50)
      }
      
      // 更新视频流告警状态
      const stream = video_streams.value.find(s => s.device_id === alert.device_id)
      if (stream) {
        stream.has_alert = alert.level === 'critical' || alert.level === 'warning'
        
        // 更新AI分析结果
        if (alert.confidence) {
          stream.ai_analysis = {
            type: alert.type,
            confidence: alert.confidence,
            level: alert.level
          }
        }
      }
      
      // 播放告警声音
      if (auto_alert_sound.value && !mute_alerts.value) {
        play_alert_sound(alert.level)
      }
    })

    // 订阅流状态更新
    websocket_instance.subscribe_stream_status((status: StreamStatusMessage) => {
      console.log('收到流状态更新:', status)
      
      const stream = video_streams.value.find(s => s.id === status.stream_id)
      if (stream) {
        stream.is_online = status.status === 'online'
        
        // 更新其他状态信息
        if (status.quality) {
          // 可以添加质量信息显示
        }
        if (status.error) {
          console.warn(`视频流 ${status.stream_id} 错误: ${status.error}`)
        }
      }
    })

    // 订阅系统状态
    websocket_instance.subscribe_system_status((status: any) => {
      console.log('收到系统状态更新:', status)
      
      if (status.devices) {
        system_stats.value.online_devices = status.devices.online || 0
        system_stats.value.total_devices = status.devices.total || 0
      }
      
      if (status.drivers) {
        system_stats.value.active_drivers = status.drivers.active || 0
      }
      
      if (status.alerts) {
        system_stats.value.daily_alerts = status.alerts.today || 0
      }
    })

    // 连接WebSocket
    await websocket_instance.connect()
    
    // 请求初始数据
    websocket_instance.request_stream_list()
    websocket_instance.request_device_status()
    
  } catch (error) {
    console.error('WebSocket初始化失败:', error)
    websocket_error.value = error instanceof Error ? error.message : 'WebSocket初始化失败'
  }
}

const disconnect_websocket_connection = () => {
  if (websocket_instance) {
    websocket_instance.disconnect()
    websocket_instance = null
  }
  
  websocket_connected.value = false
  websocket_status.value = 'disconnected'
}

const play_alert_sound = (level: string) => {
  try {
    // 创建告警声音
    const audio_context = new (window.AudioContext || (window as any).webkitAudioContext)()
    const oscillator = audio_context.createOscillator()
    const gain_node = audio_context.createGain()
    
    oscillator.connect(gain_node)
    gain_node.connect(audio_context.destination)
    
    // 根据告警级别设置不同频率
    switch (level) {
      case 'critical':
        oscillator.frequency.setValueAtTime(800, audio_context.currentTime)
        oscillator.frequency.setValueAtTime(400, audio_context.currentTime + 0.1)
        break
      case 'warning':
        oscillator.frequency.setValueAtTime(600, audio_context.currentTime)
        break
      default:
        oscillator.frequency.setValueAtTime(400, audio_context.currentTime)
    }
    
    gain_node.gain.setValueAtTime(0.1, audio_context.currentTime)
    gain_node.gain.exponentialRampToValueAtTime(0.01, audio_context.currentTime + 0.5)
    
    oscillator.start()
    oscillator.stop(audio_context.currentTime + 0.5)
  } catch (error) {
    console.warn('播放告警声音失败:', error)
  }
}

// WebSocket连接 - 实际项目中的实时数据更新
let websocket_timer: number | null = null

const connect_websocket = () => {
  websocket_timer = setInterval(() => {
    load_real_time_alerts()
    last_update.value = new Date()
  }, refresh_interval.value * 1000)
}

const disconnect_websocket = () => {
  if (websocket_timer) {
    clearInterval(websocket_timer)
    websocket_timer = null
  }
}

// 生命周期
onMounted(async () => {
  await load_all_data()
  
  // 初始化WebSocket连接
  await init_websocket()
  
  document.addEventListener('fullscreenchange', () => {
    is_fullscreen.value = !!document.fullscreenElement
  })
})

onUnmounted(() => {
  disconnect_websocket_connection()
})
</script>

<style scoped>
.monitor-view {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1d29 0%, #2d3142 100%);
}

.monitor-header {
  padding: 16px 24px;
  background: rgba(37, 40, 65, 0.9);
  border-bottom: 1px solid rgba(231, 209, 187, 0.1);
}

.monitor-title h1 {
  background: linear-gradient(135deg, #E7D1BB 0%, #A096A5 50%, #c8b39e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.monitor-content {
  flex: 1;
  padding: 16px;
  overflow: hidden;
}

/* 视频网格样式 */
.video-grid-container {
  background: transparent;
  border: 1px solid rgba(231, 209, 187, 0.15);
}

.video-controls {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  background: rgba(61, 63, 91, 0.6);
  border-bottom: 1px solid rgba(231, 209, 187, 0.1);
}

.video-grid {
  display: grid;
  gap: 8px;
  padding: 8px;
}

.video-grid.grid-2x2 { grid-template-columns: repeat(2, 1fr); }
.video-grid.grid-3x3 { grid-template-columns: repeat(3, 1fr); }
.video-grid.grid-4x4 { grid-template-columns: repeat(4, 1fr); }

.video-item {
  position: relative;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.video-item:hover {
  transform: scale(1.02);
  border-color: rgba(231, 209, 187, 0.3);
}

.video-item.video-expanded {
  grid-column: 1 / -1;
  grid-row: 1 / -1;
  z-index: 10;
  transform: none;
  border-color: #E7D1BB;
}

.video-item.has-alert {
  border-color: #ff5722;
  animation: alertPulse 2s infinite;
}

@keyframes alertPulse {
  0%, 100% { border-color: #ff5722; }
  50% { border-color: rgba(255, 87, 34, 0.3); }
}

.video-player {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 200px;
}

.video-element {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
}

/* 视频叠加信息 */
.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.video-info {
  position: absolute;
  padding: 8px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 6px;
  color: white;
  font-size: 12px;
}

.video-info.top-left { top: 8px; left: 8px; }
.video-info.top-right { top: 8px; right: 8px; }
.video-info.bottom-left { bottom: 8px; left: 8px; }

.expand-btn {
  pointer-events: all;
}

.device-name {
  font-weight: 600;
}

.ai-analysis {
  display: flex;
  align-items: center;
}

.confidence {
  font-size: 11px;
  color: #ccc;
}

.alert-animation {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border: 3px solid #ff5722;
  border-radius: 8px;
  animation: alertBorder 1.5s infinite;
}

@keyframes alertBorder {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

/* 告警面板样式 */
.alert-panel {
  background: rgba(37, 40, 65, 0.8);
  border: 1px solid rgba(231, 209, 187, 0.15);
}

.alert-summary {
  background: rgba(61, 63, 91, 0.3);
}

.alert-count {
  font-size: 24px;
  font-weight: bold;
}

.alert-count.critical { color: #ff5722; }
.alert-count.warning { color: #ff9800; }
.alert-count.info { color: #2196f3; }

.alert-list {
  max-height: calc(100vh - 400px);
  overflow-y: auto;
}

.alert-item {
  border-left: 4px solid transparent;
  margin-bottom: 1px;
}

.alert-item-critical {
  border-left-color: #ff5722;
  background: rgba(255, 87, 34, 0.1);
}

.alert-item-warning {
  border-left-color: #ff9800;
  background: rgba(255, 152, 0, 0.1);
}

/* 状态栏样式 */
.status-bar {
  padding: 8px 16px;
}

.status-card {
  background: rgba(37, 40, 65, 0.9);
  border: 1px solid rgba(231, 209, 187, 0.15);
}

.status-item {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #A096A2;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .monitor-content {
    padding: 8px;
  }
  
  .video-grid {
    gap: 4px;
    padding: 4px;
  }
}

@media (max-width: 768px) {
  .video-grid.grid-3x3,
  .video-grid.grid-4x4 {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .show_alert_panel {
    display: none;
  }
}

/* 统一配色方案 */
:deep(.v-card) {
  background: linear-gradient(135deg, rgba(37, 40, 65, 0.8), rgba(61, 63, 91, 0.6)) !important;
  border: 1px solid rgba(231, 209, 187, 0.15);
  color: #A096A2;
}

/* 只对非视频区域的卡片应用模糊效果 */
:deep(.alert-panel),
:deep(.status-card) {
  backdrop-filter: blur(16px);
}

/* 确保视频播放区域完全清晰 */
.video-grid-container,
.video-grid,
.video-item,
.video-player,
.enhanced-video-player {
  backdrop-filter: none !important;
}

:deep(.v-btn) {
  border-radius: 8px;
  font-weight: 500;
}

:deep(.v-chip) {
  border-radius: 6px;
}

/* 视频弹窗样式 */
.video-fullscreen-dialog {
  z-index: 9999;
}

.video-fullscreen-card {
  height: 100vh;
  background: #000 !important;
  border: none !important;
}

.video-fullscreen-toolbar {
  z-index: 10000;
}

.video-fullscreen-content {
  height: calc(100vh - 64px);
}

.video-fullscreen-player {
  position: relative;
  width: 100%;
  height: 100%;
  background: #000;
}

.fullscreen-video-element {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.video-fullscreen-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #1a1d29 0%, #2d3142 100%);
}

.placeholder-content {
  text-align: center;
  max-width: 400px;
}

.video-fullscreen-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.fullscreen-info {
  position: absolute;
  pointer-events: all;
}

.fullscreen-info.top-left {
  top: 20px;
  left: 20px;
}

.fullscreen-info.top-right {
  top: 20px;
  right: 20px;
}

.fullscreen-info.bottom-center {
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
}

.info-card, .ai-analysis-card, .recording-indicator {
  background: rgba(37, 40, 65, 0.95) !important;
  border: 1px solid rgba(231, 209, 187, 0.2);
  color: #A096A2;
  min-width: 250px;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.ai-result {
  text-align: center;
}

.confidence-bar {
  margin-top: 12px;
}

.recording-indicator {
  min-width: auto;
}

.recording-dot {
  animation: recordingPulse 1.5s infinite;
}

@keyframes recordingPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

/* 响应式适配 */
@media (max-width: 768px) {
  .fullscreen-info.top-left,
  .fullscreen-info.top-right {
    position: static;
    margin: 10px;
  }
  
  .info-card, .ai-analysis-card {
    min-width: auto;
    width: calc(100vw - 40px);
  }
}
</style>