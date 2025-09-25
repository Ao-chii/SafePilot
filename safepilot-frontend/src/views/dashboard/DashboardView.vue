<!--
  仪表板页面
  系统总览和关键指标展示
-->
<template>
  <div class="dashboard">
    <!-- 页面标题 -->
    <div class="d-flex align-center justify-space-between mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold text-primary">
          监控中心
        </h1>
        <p class="text-body-1 text-grey-darken-1 mt-1">
          欢迎回来，{{ user_display_name }}
        </p>
      </div>
      
      <div class="d-flex align-center">
        <v-btn
          prepend-icon="mdi-refresh"
          variant="outlined"
          color="primary"
          :loading="refreshing"
          @click="refresh_data"
        >
          刷新数据
        </v-btn>
      </div>
    </div>
    
    <!-- 关键指标卡片 -->
    <v-row class="mb-6">
      <v-col
        v-for="metric in key_metrics"
        :key="metric.title"
        cols="12"
        sm="6"
        md="3"
      >
        <MetricCard
          :title="metric.title"
          :value="metric.value"
          :subtitle="metric.subtitle"
          :icon="metric.icon"
          :icon-color="metric.color"
          :loading="loading"
          clickable
          @click="navigate_to(metric.route)"
        />
      </v-col>
    </v-row>
    
    <!-- 主要内容区域 -->
    <v-row>
      <!-- 实时事件流 -->
      <v-col
        cols="12"
        md="8"
      >
        <v-card
          title="最新事件"
          subtitle="实时危险行为检测记录"
          class="h-100"
        >
          <template #append>
            <v-btn
              icon="mdi-open-in-new"
              variant="text"
              size="small"
              @click="$router.push('/events')"
            />
          </template>
          
          <v-card-text>
            <div v-if="loading" class="text-center py-8">
              <v-progress-circular indeterminate color="primary" />
              <p class="text-body-2 text-grey-darken-1 mt-2">
                加载中...
              </p>
            </div>
            
            <div v-else-if="recent_events.length === 0" class="text-center py-8">
              <v-icon
                size="48"
                color="grey-lighten-1"
                class="mb-2"
              >
                mdi-check-circle
              </v-icon>
              <p class="text-body-2 text-grey-darken-1">
                暂无最新事件
              </p>
            </div>
            
            <v-timeline
              v-else
              density="compact"
              class="pa-0"
            >
              <v-timeline-item
                v-for="event in recent_events"
                :key="event.id"
                :dot-color="get_event_color(event.event_type)"
                size="small"
              >
                <div class="d-flex align-center justify-space-between">
                  <div>
                    <div class="d-flex align-center">
                      <StatusChip
                        :status="get_event_status(event.event_type)"
                        :text="event.event_type"
                        size="small"
                        class="mr-2"
                      />
                      <span class="font-weight-medium">
                        {{ event.driver_id }}
                      </span>
                    </div>
                    <p class="text-caption text-grey-darken-2 mt-1 mb-0">
                      设备: {{ event.device_id }} | 
                      置信度: {{ Math.round(event.confidence * 100) }}%
                    </p>
                  </div>
                  
                  <div class="text-caption text-grey-darken-2">
                    {{ format_time(event.timestamp) }}
                  </div>
                </div>
              </v-timeline-item>
            </v-timeline>
          </v-card-text>
        </v-card>
      </v-col>
      
      <!-- 系统状态 -->
      <v-col
        cols="12"
        md="4"
      >
        <v-card
          title="系统状态"
          subtitle="设备和驾驶员状态概览"
          class="h-100"
        >
          <v-card-text>
            <div class="system-status">
              <!-- 设备状态 -->
              <div class="status-section mb-4">
                <h4 class="text-subtitle-1 font-weight-medium mb-3">
                  设备状态
                </h4>
                
                <div class="d-flex align-center justify-space-between mb-2">
                  <span class="text-body-2">在线设备</span>
                  <div class="d-flex align-center">
                    <StatusChip
                      status="online"
                      size="x-small"
                      class="mr-2"
                    />
                    <span class="font-weight-medium">
                      {{ system_status.devices.online }}/{{ system_status.devices.total }}
                    </span>
                  </div>
                </div>
                
                <div class="d-flex align-center justify-space-between">
                  <span class="text-body-2">离线设备</span>
                  <div class="d-flex align-center">
                    <StatusChip
                      status="offline"
                      size="x-small"
                      class="mr-2"
                    />
                    <span class="font-weight-medium">
                      {{ system_status.devices.offline }}
                    </span>
                  </div>
                </div>
              </div>
              
              <v-divider class="my-4" />
              
              <!-- 驾驶员状态 -->
              <div class="status-section">
                <h4 class="text-subtitle-1 font-weight-medium mb-3">
                  驾驶员状态
                </h4>
                
                <div class="d-flex align-center justify-space-between mb-2">
                  <span class="text-body-2">活跃驾驶员</span>
                  <span class="font-weight-medium">
                    {{ system_status.drivers.active }}
                  </span>
                </div>
                
                <div class="d-flex align-center justify-space-between">
                  <span class="text-body-2">高风险驾驶员</span>
                  <span class="font-weight-medium error--text">
                    {{ system_status.drivers.high_risk }}
                  </span>
                </div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { event_api, device_api, driver_api } from '../../api'
import StatusChip from '../../components/common/StatusChip.vue'
import MetricCard from '../../components/common/MetricCard.vue'

const router = useRouter()
const auth_store = useAuthStore()

// 状态
const loading = ref(true)
const refreshing = ref(false)
const recent_events = ref<any[]>([])
const system_status = ref({
  devices: {
    total: 0,
    online: 0,
    offline: 0,
  },
  drivers: {
    active: 0,
    high_risk: 0,
  },
})

// 用户显示名称
const user_display_name = computed(() => auth_store.user_display_name)

// 关键指标
const key_metrics = computed(() => [
  {
    title: '在线设备',
    value: system_status.value.devices.online,
    subtitle: `总计 ${system_status.value.devices.total} 台`,
    icon: 'mdi-cellphone-link',
    color: 'success',
    route: '/devices',
  },
  {
    title: '今日事件',
    value: recent_events.value.length,
    subtitle: '危险行为检测',
    icon: 'mdi-alert-circle',
    color: 'warning',
    route: '/events',
  },
  {
    title: '活跃驾驶员',
    value: system_status.value.drivers.active,
    subtitle: '当前驾驶中',
    icon: 'mdi-account-group',
    color: 'info',
    route: '/drivers',
  },
  {
    title: '高风险驾驶员',
    value: system_status.value.drivers.high_risk,
    subtitle: '需要关注',
    icon: 'mdi-account-alert',
    color: 'error',
    route: '/drivers',
  },
])

// 获取事件状态
const get_event_status = (event_type: string): 'normal' | 'warning' | 'danger' => {
  const danger_events = ['疲劳驾驶','危险行为']
  const warning_events = ['打哈欠', '闭眼','使用手机', '抽烟','饮食']
  
  if (danger_events.some(type => event_type.includes(type))) {
    return 'danger'
  } else if (warning_events.some(type => event_type.includes(type))) {
    return 'warning'
  }
  return 'normal'
}

// 获取事件颜色
const get_event_color = (event_type: string): string => {
  const status = get_event_status(event_type)
  switch (status) {
    case 'danger':
      return 'error'
    case 'warning':
      return 'warning'
    default:
      return 'success'
  }
}

// 格式化时间
const format_time = (timestamp: string): string => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) { // 1分钟内
    return '刚刚'
  } else if (diff < 3600000) { // 1小时内
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) { // 24小时内
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  }
}

// 导航到指定路由
const navigate_to = (route: string) => {
  router.push(route)
}

// 加载数据
const load_data = async () => {
  try {
    // 并行加载数据
    const [events_response, devices_response, drivers_response] = await Promise.all([
      event_api.get_events({ limit: 10 }),
      device_api.get_devices(),
      driver_api.get_drivers(),
    ])
    
    recent_events.value = events_response.data.events || []
    
    const devices = devices_response.data || []
    system_status.value.devices.total = devices.length
    system_status.value.devices.online = devices.filter((d: any) => d.is_active).length
    system_status.value.devices.offline = devices.length - system_status.value.devices.online
    
    const drivers = drivers_response.data || []
    system_status.value.drivers.active = drivers.filter((d: any) => d.is_active).length
    
    // 根据事件数据计算高风险驾驶员
    const events = events_response.data.events || []
    const danger_events = ['疲劳驾驶', '分心驾驶', '危险行为']
    const high_risk_drivers = new Set()
    
    events.forEach((event: any) => {
      if (danger_events.some(type => event.event_type.includes(type))) {
        high_risk_drivers.add(event.driver_id)
      }
    })
    
    system_status.value.drivers.high_risk = high_risk_drivers.size
    
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

// 刷新数据
const refresh_data = async () => {
  refreshing.value = true
  await load_data()
  refreshing.value = false
}

// 页面加载时获取数据
onMounted(async () => {
  await load_data()
  loading.value = false
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.system-status .status-section {
  padding: 0;
}

.v-timeline {
  max-height: 400px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(231, 209, 187, 0.3) transparent;
}

.v-timeline::-webkit-scrollbar {
  width: 6px;
}

.v-timeline::-webkit-scrollbar-track {
  background: transparent;
}

.v-timeline::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #E7D1BB, #c8b39e);
  border-radius: 3px;
}

/* 主标题样式优化 - 使用新配色方案 */
h1 {
  background: linear-gradient(135deg, #E7D1BB 0%, #A096A5 50%, #c8b39e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 2px 8px rgba(231, 209, 187, 0.2);
}

/* 卡片样式优化 - 统一配色方案 */
:deep(.v-card) {
  backdrop-filter: blur(16px);
  background: linear-gradient(135deg, rgba(37, 40, 65, 0.8), rgba(61, 63, 91, 0.6));
  border: 1px solid rgba(231, 209, 187, 0.15);
  transition: all 350ms cubic-bezier(0.4, 0, 0.2, 1);
  color: #A096A2;
  box-shadow: 0 8px 32px rgba(21, 25, 49, 0.3);
}

:deep(.v-card:hover) {
  transform: translateY(-2px);
  box-shadow: 0 12px 48px rgba(21, 25, 49, 0.4), 0 0 0 1px rgba(231, 209, 187, 0.2);
  border-color: rgba(231, 209, 187, 0.25);
}

/* 按钮优化 - 统一配色 */
:deep(.v-btn) {
  border-radius: 12px;
  font-weight: 500;
  letter-spacing: 0.3px;
  transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.v-btn--variant-outlined) {
  border: 2px solid;
}

:deep(.v-btn:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(231, 209, 187, 0.3);
}

/* 时间线样式优化 - 统一配色 */
:deep(.v-timeline-item) {
  margin-bottom: 16px;
}

:deep(.v-timeline-item__body) {
  padding: 12px;
  background: rgba(61, 63, 91, 0.3);
  border-radius: 12px;
  border-left: 3px solid transparent;
  transition: all 250ms ease;
  color: #A096A2;
  backdrop-filter: blur(8px);
}

:deep(.v-timeline-item:hover .v-timeline-item__body) {
  background: rgba(231, 209, 187, 0.08);
  border-left-color: #E7D1BB;
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(231, 209, 187, 0.2);
}
</style>