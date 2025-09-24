<!--
  驾驶员详情页面
  显示驾驶员的详细信息、风险评级、历史行为分析
-->
<template>
  <div class="driver-detail-view">
    <!-- 返回按钮 -->
    <v-btn
      @click="go_back"
      variant="text"
      prepend-icon="mdi-arrow-left"
      class="mb-4"
    >
      返回驾驶员列表
    </v-btn>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-16">
      <v-progress-circular size="64" indeterminate color="primary" />
      <p class="text-h6 mt-4">加载驾驶员详情...</p>
    </div>

    <!-- 驾驶员不存在 -->
    <div v-else-if="!driver_info" class="text-center py-16">
      <v-icon size="96" color="grey-lighten-2">mdi-account-question</v-icon>
      <h2 class="text-h5 mt-4">驾驶员不存在</h2>
      <p class="text-body-1 text-grey-darken-1">请检查驾驶员ID是否正确</p>
    </div>

    <!-- 驾驶员详情内容 -->
    <div v-else>
      <!-- 基本信息卡片 -->
      <v-row class="mb-6">
        <v-col cols="12" md="8">
          <v-card elevation="2" class="h-100">
            <v-card-title class="d-flex align-center">
              <v-avatar size="48" :color="risk_level_info.color" class="mr-4">
                <span class="text-white font-weight-bold">{{ driver_info.name.charAt(0) }}</span>
              </v-avatar>
              <div>
                <h2 class="text-h5">{{ driver_info.name }}</h2>
                <p class="text-body-2 text-grey-darken-1">ID: {{ driver_info.driver_id }}</p>
              </div>
            </v-card-title>
            
            <v-card-text>
              <v-row>
                <v-col cols="12" sm="6">
                  <div class="info-item">
                    <div class="info-label">状态</div>
                    <StatusChip
                      :status="driver_info.is_active ? 'online' : 'offline'"
                      :text="driver_info.is_active ? '活跃' : '非活跃'"
                    />
                  </div>
                </v-col>
                <v-col cols="12" sm="6">
                  <div class="info-item">
                    <div class="info-label">注册时间</div>
                    <div class="info-value">{{ format_date(driver_info.created_at) }}</div>
                  </div>
                </v-col>
                <v-col cols="12" sm="6">
                  <div class="info-item">
                    <div class="info-label">总违规次数</div>
                    <div class="info-value text-error font-weight-bold">{{ total_violations }}</div>
                  </div>
                </v-col>
                <v-col cols="12" sm="6">
                  <div class="info-item">
                    <div class="info-label">最近活动</div>
                    <div class="info-value">{{ last_activity || '暂无记录' }}</div>
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- 风险评级卡片 -->
        <v-col cols="12" md="4">
          <v-card elevation="2" class="h-100 risk-card">
            <v-card-title class="text-center">
              风险评级
            </v-card-title>
            <v-card-text class="text-center">
              <div class="risk-level-display">
                <v-progress-circular
                  :model-value="risk_score"
                  :color="risk_level_info.color"
                  :size="120"
                  :width="12"
                  class="mb-4"
                >
                  <div class="risk-score-inner">
                    <div class="risk-score">{{ risk_score }}</div>
                    <div class="risk-score-label">分</div>
                  </div>
                </v-progress-circular>
                <div>
                  <v-chip
                    :color="risk_level_info.color"
                    size="large"
                    label
                    class="font-weight-bold"
                  >
                    {{ risk_level_info.label }}
                  </v-chip>
                  <p class="text-body-2 text-grey-darken-1 mt-2">
                    {{ risk_level_info.description }}
                  </p>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 统计指标 -->
      <v-row class="mb-6">
        <v-col cols="12" sm="6" md="3">
          <MetricCard
            title="疲劳驾驶"
            :value="violation_stats.fatigue_count"
            subtitle="次违规"
            icon="mdi-sleep"
            icon-color="error"
          />
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <MetricCard
            title="分心驾驶"
            :value="violation_stats.distraction_count"
            subtitle="次违规"
            icon="mdi-phone"
            icon-color="warning"
          />
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <MetricCard
            title="危险行为"
            :value="violation_stats.dangerous_count"
            subtitle="次违规"
            icon="mdi-alert"
            icon-color="error"
          />
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <MetricCard
            title="本月违规"
            :value="violation_stats.this_month_count"
            subtitle="次违规"
            icon="mdi-calendar-month"
            icon-color="info"
          />
        </v-col>
      </v-row>

      <!-- 图表分析区域 -->
      <v-row>
        <!-- 违规趋势折线图 -->
        <v-col cols="12" md="6">
          <v-card elevation="2" class="h-100">
            <v-card-title>违规趋势分析</v-card-title>
            <v-card-text>
              <div v-if="violation_trend.length === 0" class="text-center py-8">
                <v-icon size="48" color="grey-lighten-1">mdi-chart-line</v-icon>
                <p class="text-body-2 mt-2">暂无趋势数据</p>
              </div>
              <div v-else class="chart-container">
                <LineChart 
                  :data="violation_trend"
                  label="违规次数"
                  color="#FCA5A5"
                />
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- 违规类型分布饼图 -->
        <v-col cols="12" md="6">
          <v-card elevation="2" class="h-100">
            <v-card-title>违规类型分布</v-card-title>
            <v-card-text>
              <div v-if="violation_distribution.length === 0" class="text-center py-8">
                <v-icon size="48" color="grey-lighten-1">mdi-chart-pie</v-icon>
                <p class="text-body-2 mt-2">暂无违规数据</p>
              </div>
              <div v-else class="chart-container">
                <PieChart 
                  :data="violation_distribution"
                  :colors="violation_colors"
                />
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 最近违规记录 -->
      <v-row class="mt-6">
        <v-col cols="12">
          <v-card elevation="2">
            <v-card-title class="d-flex align-center justify-space-between">
              <span>最近违规记录</span>
              <v-btn
                @click="load_recent_violations"
                :loading="loading_violations"
                size="small"
                variant="outlined"
                prepend-icon="mdi-refresh"
              >
                刷新
              </v-btn>
            </v-card-title>
            
            <v-card-text>
              <div v-if="loading_violations" class="text-center py-8">
                <v-progress-circular indeterminate color="primary" />
                <p class="text-body-2 mt-2">加载违规记录...</p>
              </div>
              <div v-else-if="recent_violations.length === 0" class="text-center py-8">
                <v-icon size="48" color="grey-lighten-1">mdi-format-list-bulleted</v-icon>
                <p class="text-body-2 mt-2">暂无违规记录</p>
              </div>
              <v-list v-else class="violation-list">
                <v-list-item
                  v-for="(violation, index) in recent_violations"
                  :key="violation.event_id"
                  class="violation-item"
                  :class="{ 'border-bottom': index < recent_violations.length - 1 }"
                >
                  <template #prepend>
                    <v-avatar 
                      :color="get_violation_color(violation.event_type)"
                      size="40"
                    >
                      <v-icon color="white">{{ get_violation_icon(violation.event_type) }}</v-icon>
                    </v-avatar>
                  </template>
                  
                  <v-list-item-title>{{ violation.event_type }}</v-list-item-title>
                  <v-list-item-subtitle>
                    <div>设备: {{ violation.device_id }}</div>
                    <div class="text-caption">{{ format_datetime(violation.timestamp) }}</div>
                  </v-list-item-subtitle>
                  
                  <template #append>
                    <v-chip
                      :color="get_violation_color(violation.event_type)"
                      size="small"
                      variant="outlined"
                    >
                      {{ get_violation_severity(violation.event_type) }}
                    </v-chip>
                  </template>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { driver_api, event_api } from '../../api'
import StatusChip from '../../components/common/StatusChip.vue'
import MetricCard from '../../components/common/MetricCard.vue'
import PieChart from '../../components/common/PieChart.vue'
import LineChart from '../../components/common/LineChart.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const loading_violations = ref(false)
const driver_info = ref<any>(null)
const driver_violations = ref<any[]>([])
const recent_violations = ref<any[]>([])

// 违规统计数据
const violation_stats = ref({
  fatigue_count: 0,
  distraction_count: 0,
  dangerous_count: 0,
  this_month_count: 0,
})

// 违规趋势数据
const violation_trend = ref<Array<{date: string, count: number}>>([])

// 违规类型颜色
const violation_colors = [
  '#FCA5A5', // 疲劳驾驶 - 红色
  '#FDE68A', // 分心驾驶 - 黄色 
  '#F87171', // 危险驾驶 - 深红
  '#A78BFA', // 其他违规 - 紫色
]

// 计算总违规次数
const total_violations = computed(() => {
  return driver_violations.value.length
})

// 计算最近活动时间
const last_activity = computed(() => {
  if (driver_violations.value.length === 0) return null
  const latest = driver_violations.value[0]?.timestamp
  return latest ? format_datetime(latest) : null
})

// 风险评级算法
const risk_score = computed(() => {
  const violations = driver_violations.value
  if (violations.length === 0) return 0

  let score = 0
  const now = new Date()
  const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
  
  violations.forEach(violation => {
    const violationDate = new Date(violation.timestamp)
    const isRecent = violationDate >= thirtyDaysAgo
    
    // 基础分数根据违规类型
    let baseScore = 0
    switch (violation.event_type) {
      case '疲劳驾驶':
        baseScore = 25
        break
      case '分心驾驶':
        baseScore = 20
        break
      case '危险驾驶':
        baseScore = 30
        break
      default:
        baseScore = 15
    }
    
    // 最近30天的违规加权更高
    if (isRecent) {
      score += baseScore * 1.5
    } else {
      score += baseScore * 0.5
    }
  })
  
  // 限制在0-100之间
  return Math.min(Math.round(score), 100)
})

// 风险等级信息
const risk_level_info = computed(() => {
  const score = risk_score.value
  
  if (score >= 80) {
    return {
      label: '高危',
      color: 'error',
      description: '需要立即关注和干预'
    }
  } else if (score >= 60) {
    return {
      label: '中危',
      color: 'warning', 
      description: '需要加强监管'
    }
  } else if (score >= 30) {
    return {
      label: '低危',
      color: 'info',
      description: '保持观察'
    }
  } else {
    return {
      label: '安全',
      color: 'success',
      description: '表现良好'
    }
  }
})

// 违规类型分布数据
const violation_distribution = computed(() => {
  const typeCount: Record<string, number> = {}
  
  driver_violations.value.forEach(violation => {
    typeCount[violation.event_type] = (typeCount[violation.event_type] || 0) + 1
  })
  
  const total = driver_violations.value.length
  return Object.entries(typeCount).map(([type, count]) => ({
    type,
    count,
    percentage: total > 0 ? Math.round((count / total) * 100) : 0
  }))
})

// 格式化日期
const format_date = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 格式化日期时间
const format_datetime = (dateString: string): string => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 获取违规图标
const get_violation_icon = (type: string): string => {
  const iconMap: Record<string, string> = {
    '疲劳驾驶': 'mdi-sleep',
    '分心驾驶': 'mdi-phone',
    '危险驾驶': 'mdi-car-emergency',
    '超速驾驶': 'mdi-speedometer'
  }
  return iconMap[type] || 'mdi-alert-circle'
}

// 获取违规颜色
const get_violation_color = (type: string): string => {
  const colorMap: Record<string, string> = {
    '疲劳驾驶': 'error',
    '分心驾驶': 'warning',
    '危险驾驶': 'error',
    '超速驾驶': 'orange'
  }
  return colorMap[type] || 'grey'
}

// 获取违规严重程度
const get_violation_severity = (type: string): string => {
  const severityMap: Record<string, string> = {
    '疲劳驾驶': '严重',
    '分心驾驶': '中等',
    '危险驾驶': '严重',
    '超速驾驶': '中等'
  }
  return severityMap[type] || '轻微'
}

// 加载驾驶员详情
const load_driver_detail = async () => {
  const driverId = route.params.id as string
  if (!driverId) return

  loading.value = true
  try {
    // 并行加载驾驶员信息和违规记录
    const [driverResponse, violationsResponse] = await Promise.all([
      driver_api.get_driver(driverId),
      event_api.get_events({ driver_id: driverId })
    ])
    
    driver_info.value = driverResponse.data.driver
    driver_violations.value = violationsResponse.data.events || []
    
    // 计算统计数据
    calculate_violation_stats()
    calculate_violation_trend()
    
    // 加载最近违规记录
    recent_violations.value = driver_violations.value.slice(0, 10)
    
  } catch (error) {
    console.error('加载驾驶员详情失败:', error)
  } finally {
    loading.value = false
  }
}

// 计算违规统计
const calculate_violation_stats = () => {
  const violations = driver_violations.value
  const now = new Date()
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
  
  violation_stats.value = {
    fatigue_count: violations.filter(v => v.event_type === '疲劳驾驶').length,
    distraction_count: violations.filter(v => v.event_type === '分心驾驶').length,
    dangerous_count: violations.filter(v => v.event_type === '危险驾驶').length,
    this_month_count: violations.filter(v => new Date(v.timestamp) >= startOfMonth).length,
  }
}

// 计算违规趋势
const calculate_violation_trend = () => {
  const violations = driver_violations.value
  const dateCount: Record<string, number> = {}
  
  violations.forEach(violation => {
    const date = new Date(violation.timestamp).toISOString().split('T')[0]
    dateCount[date] = (dateCount[date] || 0) + 1
  })
  
  violation_trend.value = Object.entries(dateCount)
    .map(([date, count]) => ({ date, count }))
    .sort((a, b) => a.date.localeCompare(b.date))
    .slice(-30) // 只显示最近30天
}

// 加载最近违规记录
const load_recent_violations = async () => {
  const driverId = route.params.id as string
  if (!driverId) return

  loading_violations.value = true
  try {
    const response = await event_api.get_events({ 
      driver_id: driverId,
      limit: 20
    })
    recent_violations.value = response.data.events || []
  } catch (error) {
    console.error('加载违规记录失败:', error)
  } finally {
    loading_violations.value = false
  }
}

// 返回上一页
const go_back = () => {
  router.push('/drivers')
}

// 初始化
onMounted(() => {
  load_driver_detail()
})
</script>

<style scoped>
.driver-detail-view {
  max-width: 1400px;
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

.info-item {
  margin-bottom: 16px;
}

.info-label {
  font-size: 14px;
  color: #A096A5;
  margin-bottom: 4px;
}

.info-value {
  font-size: 16px;
  font-weight: 500;
  color: #E7D1BB;
}

.risk-card {
  background: linear-gradient(135deg, rgba(37, 40, 65, 0.9), rgba(61, 63, 91, 0.7)) !important;
}

.risk-level-display {
  padding: 20px 0;
}

.risk-score-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.risk-score {
  font-size: 32px;
  font-weight: bold;
  color: #E7D1BB;
  line-height: 1;
}

.risk-score-label {
  font-size: 14px;
  color: #A096A5;
}

.chart-container {
  min-height: 300px;
  padding: 16px;
  background: rgba(61, 63, 91, 0.3);
  border-radius: 12px;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(231, 209, 187, 0.1);
}

.violation-list {
  background: transparent;
}

.violation-item {
  padding: 16px 0;
  transition: all 200ms ease;
}

.violation-item:hover {
  background: rgba(231, 209, 187, 0.05);
  border-radius: 8px;
}

.violation-item.border-bottom {
  border-bottom: 1px solid rgba(160, 150, 165, 0.15);
}

/* 卡片样式优化 */
:deep(.v-card) {
  backdrop-filter: blur(16px);
  background: linear-gradient(135deg, rgba(37, 40, 65, 0.8), rgba(61, 63, 91, 0.6));
  border: 1px solid rgba(231, 209, 187, 0.15);
  box-shadow: 0 8px 32px rgba(21, 25, 49, 0.3);
  transition: all 300ms ease;
}

:deep(.v-card:hover) {
  transform: translateY(-2px);
  box-shadow: 0 12px 48px rgba(21, 25, 49, 0.4), 0 0 0 1px rgba(231, 209, 187, 0.2);
}

/* 标题样式 */
h2 {
  background: linear-gradient(135deg, #E7D1BB 0%, #A096A5 50%, #c8b39e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>