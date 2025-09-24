<!--
  数据统计页面
  实现需求文档中的"数据统计与可视化用例"
-->
<template>
  <div class="stats-view">
    <!-- 页面标题 -->
    <div class="d-flex align-center justify-space-between mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold text-primary">
          数据统计
        </h1>
        <p class="text-body-1 text-grey-darken-1 mt-1">
          危险行为数据分析与可视化
        </p>
      </div>
      
      <v-btn
        @click="export_report"
        color="primary"
        prepend-icon="mdi-download"
        variant="outlined"
        :disabled="loading"
      >
        导出报表
      </v-btn>
    </div>

    <!-- 时间范围选择 -->
    <v-card class="mb-6" elevation="2">
      <v-card-title>分析时间范围</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="3">
            <v-text-field
              v-model="date_range.start"
              label="开始日期"
              type="date"
              variant="outlined"
              density="comfortable"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-text-field
              v-model="date_range.end"
              label="结束日期"
              type="date"
              variant="outlined"
              density="comfortable"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="selected_analysis_type"
              label="分析维度"
              :items="analysis_types"
              variant="outlined"
              density="comfortable"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-btn
              @click="load_statistics"
              :loading="loading"
              color="primary"
              block
              size="large"
            >
              更新统计
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 统计概览卡片 -->
    <v-row class="mb-6">
      <v-col cols="12" md="3">
        <MetricCard
          title="总事件数"
          :value="overview_stats.total_events"
          subtitle="统计期间内"
          icon="mdi-alert-circle"
          icon-color="info"
          :loading="loading"
        />
      </v-col>
      <v-col cols="12" md="3">
        <MetricCard
          title="高危事件"
          :value="overview_stats.danger_events"
          subtitle="需要重点关注"
          icon="mdi-alert"
          icon-color="error"
          :loading="loading"
        />
      </v-col>
      <v-col cols="12" md="3">
        <MetricCard
          title="涉及驾驶员"
          :value="overview_stats.affected_drivers"
          subtitle="有违规记录"
          icon="mdi-account-alert"
          icon-color="warning"
          :loading="loading"
        />
      </v-col>
      <v-col cols="12" md="3">
        <MetricCard
          title="活跃设备"
          :value="overview_stats.active_devices"
          subtitle="产生数据的设备"
          icon="mdi-cellphone-check"
          icon-color="success"
          :loading="loading"
        />
      </v-col>
    </v-row>

    <!-- 图表区域 -->
    <v-row>
      <!-- 事件类型分布饼图 -->
      <v-col cols="12" md="6">
        <v-card elevation="2" class="h-100">
          <v-card-title class="d-flex align-center justify-space-between">
            <span>事件类型分布</span>
            <v-chip size="small" color="primary">饼图</v-chip>
          </v-card-title>
          <v-card-text>
            <div v-if="loading" class="text-center py-8">
              <v-progress-circular indeterminate color="primary" />
              <p class="text-body-2 mt-2">加载图表数据...</p>
            </div>
            <div v-else-if="event_type_distribution.length === 0" class="text-center py-8">
              <v-icon size="48" color="grey-lighten-1">mdi-chart-pie</v-icon>
              <p class="text-body-2 mt-2">暂无数据</p>
            </div>
            <div v-else class="chart-container">
              <PieChart 
                :data="event_type_distribution" 
                :colors="pie_colors"
              />
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 时间趋势折线图 -->
      <v-col cols="12" md="6">
        <v-card elevation="2" class="h-100">
          <v-card-title class="d-flex align-center justify-space-between">
            <span>事件趋势分析</span>
            <v-chip size="small" color="success">折线图</v-chip>
          </v-card-title>
          <v-card-text>
            <div v-if="loading" class="text-center py-8">
              <v-progress-circular indeterminate color="primary" />
              <p class="text-body-2 mt-2">加载趋势数据...</p>
            </div>
            <div v-else-if="time_trend_data.length === 0" class="text-center py-8">
              <v-icon size="48" color="grey-lighten-1">mdi-chart-line</v-icon>
              <p class="text-body-2 mt-2">暂无趋势数据</p>
            </div>
            <div v-else class="chart-container">
              <LineChart 
                :data="time_trend_data"
                label="事件数量"
                color="#6EE7B7"
              />
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 驾驶员排行和设备分析 -->
    <v-row class="mt-6">
      <!-- 高风险驾驶员排行 -->
      <v-col cols="12" md="6">
        <v-card elevation="2" class="h-100">
          <v-card-title>高风险驾驶员排行</v-card-title>
          <v-card-text>
            <div v-if="loading" class="text-center py-4">
              <v-progress-circular indeterminate color="primary" size="30" />
            </div>
            <div v-else-if="driver_ranking.length === 0" class="text-center py-8">
              <v-icon size="48" color="grey-lighten-1">mdi-account-group</v-icon>
              <p class="text-body-2 mt-2">暂无数据</p>
            </div>
            <v-list v-else density="compact">
              <v-list-item
                v-for="(driver, index) in driver_ranking"
                :key="driver.driver_id"
                class="ranking-item"
              >
                <template #prepend>
                  <v-avatar 
                    size="32" 
                    :color="get_ranking_color(index)"
                    class="text-white font-weight-bold"
                  >
                    {{ index + 1 }}
                  </v-avatar>
                </template>
                
                <v-list-item-title>{{ driver.name }}</v-list-item-title>
                <v-list-item-subtitle>ID: {{ driver.driver_id }}</v-list-item-subtitle>
                
                <template #append>
                  <div class="text-right">
                    <div class="font-weight-bold text-error">{{ driver.event_count }}</div>
                    <div class="text-caption text-grey-darken-2">次违规</div>
                  </div>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 设备数据分析 -->
      <v-col cols="12" md="6">
        <v-card elevation="2" class="h-100">
          <v-card-title>设备检测效率</v-card-title>
          <v-card-text>
            <div v-if="loading" class="text-center py-4">
              <v-progress-circular indeterminate color="primary" size="30" />
            </div>
            <div v-else-if="device_efficiency.length === 0" class="text-center py-8">
              <v-icon size="48" color="grey-lighten-1">mdi-cellphone-cog</v-icon>
              <p class="text-body-2 mt-2">暂无设备数据</p>
            </div>
            <v-list v-else density="compact">
              <v-list-item
                v-for="device in device_efficiency"
                :key="device.device_id"
              >
                <v-list-item-title>{{ device.name }}</v-list-item-title>
                <v-list-item-subtitle>{{ device.device_id }}</v-list-item-subtitle>
                
                <template #append>
                  <div class="text-right" style="min-width: 120px;">
                    <div class="d-flex align-center">
                      <v-progress-linear
                        :model-value="device.efficiency"
                        :color="get_efficiency_color(device.efficiency)"
                        height="6"
                        rounded
                        class="mr-2"
                        style="width: 60px;"
                      />
                      <span class="text-caption">{{ device.efficiency }}%</span>
                    </div>
                    <div class="text-caption text-grey-darken-2 mt-1">
                      {{ device.event_count }} 次检测
                    </div>
                  </div>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 新增柱状图：设备效率可视化 -->
    <v-row class="mt-6">
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center justify-space-between">
            <span>设备效率分析</span>
            <v-chip size="small" color="info">柱状图</v-chip>
          </v-card-title>
          <v-card-text>
            <div v-if="loading" class="text-center py-8">
              <v-progress-circular indeterminate color="primary" />
              <p class="text-body-2 mt-2">加载效率数据...</p>
            </div>
            <div v-else-if="device_efficiency_chart_data.length === 0" class="text-center py-8">
              <v-icon size="48" color="grey-lighten-1">mdi-chart-bar</v-icon>
              <p class="text-body-2 mt-2">暂无设备数据</p>
            </div>
            <div v-else class="chart-container">
              <BarChart 
                :data="device_efficiency_chart_data"
                title="效率百分比"
                color="#A096A5"
              />
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { event_api, driver_api, device_api } from '../../api'
import MetricCard from '../../components/common/MetricCard.vue'
import PieChart from '../../components/common/PieChart.vue'
import LineChart from '../../components/common/LineChart.vue'
import BarChart from '../../components/common/BarChart.vue'

// 状态管理
const loading = ref(false)
const date_range = reactive({
  start: '',
  end: '',
})
const selected_analysis_type = ref('event_type')

// 分析维度选项
const analysis_types = [
  { title: '事件类型分析', value: 'event_type' },
  { title: '驾驶员分析', value: 'driver' },
  { title: '时间趋势分析', value: 'time_trend' },
  { title: '设备效率分析', value: 'device' },
]

// 统计数据
const overview_stats = reactive({
  total_events: 0,
  danger_events: 0,
  affected_drivers: 0,
  active_devices: 0,
})

const event_type_distribution = ref<any[]>([])
const time_trend_data = ref<any[]>([])
const driver_ranking = ref<any[]>([])
const device_efficiency = ref<any[]>([])

// 图表配置 - 使用新配色方案
const pie_colors = [
  '#E7D1BB', // primary-100
  '#c8b39e', // primary-200  
  '#A096A5', // accent-100
  '#84725e', // primary-300
  '#463e4b', // accent-200
  '#6EE7B7', // success
  '#FDE68A', // warning
  '#FCA5A5', // error
  '#93C5FD'  // info
]

// 计算属性
const max_daily_count = computed(() => {
  return Math.max(...time_trend_data.value.map(item => item.count), 1)
})

// 设备效率柱状图数据
const device_efficiency_chart_data = computed(() => {
  return device_efficiency.value.map(device => ({
    label: device.name,
    value: device.efficiency
  }))
})

// 工具函数
const format_chart_date = (date: string): string => {
  return new Date(date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

const get_ranking_color = (index: number): string => {
  const colors = ['error', 'warning', 'orange', 'grey']
  return colors[index] || 'grey'
}

const get_efficiency_color = (efficiency: number): string => {
  if (efficiency >= 80) return 'success'
  if (efficiency >= 60) return 'warning'
  return 'error'
}

// 数据加载
const load_statistics = async () => {
  loading.value = true
  try {
    await Promise.all([
      load_overview_stats(),
      load_event_type_distribution(),
      load_time_trend(),
      load_driver_ranking(),
      load_device_efficiency(),
    ])
  } catch (error) {
    console.error('加载统计数据失败:', error)
  } finally {
    loading.value = false
  }
}

const load_overview_stats = async () => {
  try {
    const params = {
      start_time: date_range.start ? date_range.start + 'T00:00:00' : undefined,
      end_time: date_range.end ? date_range.end + 'T23:59:59' : undefined,
    }
    
    const response = await event_api.get_events(params)
    const events = response.data.events || []
    
    overview_stats.total_events = events.length
    overview_stats.danger_events = events.filter((e: any) => 
      ['疲劳驾驶', '分心驾驶'].includes(e.event_type)
    ).length
    overview_stats.affected_drivers = new Set(events.map((e: any) => e.driver_id)).size
    overview_stats.active_devices = new Set(events.map((e: any) => e.device_id)).size
  } catch (error) {
    console.error('加载概览统计失败:', error)
  }
}

const load_event_type_distribution = async () => {
  try {
    const params = {
      start_time: date_range.start ? date_range.start + 'T00:00:00' : undefined,
      end_time: date_range.end ? date_range.end + 'T23:59:59' : undefined,
    }
    
    const response = await event_api.get_events(params)
    const events = response.data.events || []
    
    // 统计事件类型分布
    const typeCount = events.reduce((acc: any, event: any) => {
      acc[event.event_type] = (acc[event.event_type] || 0) + 1
      return acc
    }, {})
    
    const total = events.length
    event_type_distribution.value = Object.entries(typeCount).map(([type, count]: any) => ({
      type,
      count,
      percentage: total > 0 ? Math.round((count / total) * 100) : 0,
    })).sort((a: any, b: any) => b.count - a.count)
  } catch (error) {
    console.error('加载事件类型分布失败:', error)
    event_type_distribution.value = []
  }
}

const load_time_trend = async () => {
  try {
    const params = {
      start_time: date_range.start ? date_range.start + 'T00:00:00' : undefined,
      end_time: date_range.end ? date_range.end + 'T23:59:59' : undefined,
    }
    
    const response = await event_api.get_events(params)
    const events = response.data.events || []
    
    // 按日期分组统计
    const dateCount = events.reduce((acc: any, event: any) => {
      const date = new Date(event.timestamp).toISOString().split('T')[0]
      acc[date] = (acc[date] || 0) + 1
      return acc
    }, {})
    
    time_trend_data.value = Object.entries(dateCount)
      .map(([date, count]: any) => ({ date, count }))
      .sort((a: any, b: any) => a.date.localeCompare(b.date))
  } catch (error) {
    console.error('加载时间趋势失败:', error)
    time_trend_data.value = []
  }
}

const load_driver_ranking = async () => {
  try {
    const params = {
      start_time: date_range.start ? date_range.start + 'T00:00:00' : undefined,
      end_time: date_range.end ? date_range.end + 'T23:59:59' : undefined,
    }
    
    const [events_response, drivers_response] = await Promise.all([
      event_api.get_events(params),
      driver_api.get_drivers(),
    ])
    
    const events = events_response.data.events || []
    const drivers = drivers_response.data.drivers || []
    
    // 统计每个驾驶员的事件数
    const driverEventCount = events.reduce((acc: any, event: any) => {
      acc[event.driver_id] = (acc[event.driver_id] || 0) + 1
      return acc
    }, {})
    
    // 构建排行榜
    driver_ranking.value = Object.entries(driverEventCount)
      .map(([driver_id, event_count]: any) => {
        const driver = drivers.find((d: any) => d.driver_id === driver_id)
        return {
          driver_id,
          name: driver?.name || driver_id,
          event_count,
        }
      })
      .sort((a: any, b: any) => b.event_count - a.event_count)
      .slice(0, 10) // 只显示前10名
  } catch (error) {
    console.error('加载驾驶员排行失败:', error)
    driver_ranking.value = []
  }
}

const load_device_efficiency = async () => {
  try {
    const params = {
      start_time: date_range.start ? date_range.start + 'T00:00:00' : undefined,
      end_time: date_range.end ? date_range.end + 'T23:59:59' : undefined,
    }
    
    const [events_response, devices_response] = await Promise.all([
      event_api.get_events(params),
      device_api.get_devices(),
    ])
    
    const events = events_response.data.events || []
    const devices = devices_response.data.devices || []
    
    // 统计每个设备的事件数
    const deviceEventCount = events.reduce((acc: any, event: any) => {
      acc[event.device_id] = (acc[event.device_id] || 0) + 1
      return acc
    }, {})
    
    // 构建设备效率数据（这里简化处理，实际应该根据设备运行时间计算）
    device_efficiency.value = devices.map((device: any) => {
      const event_count = deviceEventCount[device.device_id] || 0
      const efficiency = device.is_active ? Math.min(event_count * 10 + 60, 100) : 0
      
      return {
        device_id: device.device_id,
        name: device.name,
        event_count,
        efficiency,
      }
    }).sort((a: any, b: any) => b.efficiency - a.efficiency)
  } catch (error) {
    console.error('加载设备效率失败:', error)
    device_efficiency.value = []
  }
}

// 导出报表
const export_report = () => {
  // TODO: 实现报表导出功能
  console.log('导出报表功能待实现')
}

// 初始化
onMounted(() => {
  // 设置默认时间范围（最近30天）
  const today = new Date()
  const thirty_days_ago = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
  
  date_range.start = thirty_days_ago.toISOString().split('T')[0]
  date_range.end = today.toISOString().split('T')[0]
  
  load_statistics()
})
</script>

<style scoped>
.stats-view {
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

/* 图表容器样式优化 */
.chart-container {
  min-height: 300px;
  padding: 16px;
  background: rgba(61, 63, 91, 0.3);
  border-radius: 12px;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(231, 209, 187, 0.1);
}

.ranking-item {
  border-bottom: 1px solid rgba(160, 150, 165, 0.15);
  transition: all 200ms ease;
}

.ranking-item:hover {
  background: rgba(231, 209, 187, 0.05);
  border-radius: 8px;
}

.ranking-item:last-child {
  border-bottom: none;
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

/* 主标题样式优化 */
h1 {
  background: linear-gradient(135deg, #E7D1BB 0%, #A096A5 50%, #c8b39e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 2px 8px rgba(231, 209, 187, 0.2);
}
</style>