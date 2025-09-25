<!--
  事件历史查询页面
  根据需求文档的"危险行为历史查询用例"实现
-->
<template>
  <div class="events-view">
    <!-- 页面标题 -->
    <div class="d-flex align-center justify-space-between mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold text-primary">
          事件历史查询
        </h1>
        <p class="text-body-1 text-grey-darken-1 mt-1">
          查询和分析危险行为检测记录
        </p>
      </div>
    </div>

    <!-- 查询条件面板 -->
    <v-card class="mb-6" elevation="2">
      <v-card-title>筛选条件</v-card-title>
      <v-card-text>
        <v-row>
          <!-- 时间范围 -->
          <v-col cols="12" md="3">
            <v-text-field
              v-model="filter.start_date"
              label="开始日期"
              type="date"
              variant="outlined"
              density="comfortable"
              :disabled="loading"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-text-field
              v-model="filter.end_date"
              label="结束日期"
              type="date"
              variant="outlined"
              density="comfortable"
              :disabled="loading"
            />
          </v-col>

          <!-- 驾驶员筛选 -->
          <v-col cols="12" md="2">
            <v-text-field
              v-model="filter.driver_id"
              label="驾驶员ID"
              variant="outlined"
              density="comfortable"
              :disabled="loading"
            />
          </v-col>

          <!-- 事件类型筛选 -->
          <v-col cols="12" md="2">
            <v-select
              v-model="filter.event_type"
              label="事件类型"
              :items="event_type_options"
              variant="outlined"
              density="comfortable"
              clearable
              :disabled="loading"
            />
          </v-col>

          <!-- 查询按钮 -->
          <v-col cols="12" md="2">
            <v-btn
              @click="search_events"
              :loading="loading"
              color="primary"
              block
              size="large"
              prepend-icon="mdi-magnify"
            >
              查询
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 结果数据表格 -->
    <v-card elevation="2">
      <v-card-title class="d-flex align-center justify-space-between">
        <span>查询结果</span>
        <div class="d-flex align-center">
          <span class="text-caption text-grey-darken-2 mr-4">
            共 {{ total_count }} 条记录
          </span>
          <v-btn
            @click="export_results"
            :disabled="events.length === 0 || loading"
            variant="outlined"
            size="small"
            prepend-icon="mdi-download"
          >
            导出
          </v-btn>
        </div>
      </v-card-title>

      <v-data-table
        :headers="table_headers"
        :items="events"
        :loading="loading"
        :items-per-page="page_size"
        class="elevation-0"
        loading-text="正在加载数据..."
        no-data-text="暂无数据"
      >
        <!-- 事件类型显示 -->
        <template #item.event_type="{ item }">
          <StatusChip
            :status="get_event_status(item.event_type)"
            :text="item.event_type"
            size="small"
          />
        </template>

        <!-- 置信度显示 -->
        <template #item.confidence="{ item }">
          <div class="d-flex align-center">
            <v-progress-linear
              :model-value="item.confidence * 100"
              :color="get_confidence_color(item.confidence)"
              height="6"
              rounded
              class="mr-2"
              style="min-width: 60px;"
            />
            <span class="text-caption">{{ Math.round(item.confidence * 100) }}%</span>
          </div>
        </template>

        <!-- 时间格式化 -->
        <template #item.timestamp="{ item }">
          {{ format_datetime(item.timestamp) }}
        </template>

        <!-- 操作按钮 -->
        <template #item.actions="{ item }">
          <v-btn
            @click="view_event_detail(item)"
            icon
            size="small"
            variant="text"
          >
            <v-icon>mdi-eye</v-icon>
          </v-btn>
        </template>
      </v-data-table>

      <!-- 分页 -->
      <v-divider />
      <div class="d-flex justify-center pa-4">
        <v-pagination
          v-model="current_page"
          :length="total_pages"
          :total-visible="7"
          @update:model-value="load_events"
        />
      </div>
    </v-card>

    <!-- 事件详情对话框 -->
    <v-dialog v-model="detail_dialog" max-width="600">
      <v-card v-if="selected_event">
        <v-card-title>事件详情</v-card-title>
        <v-card-text>
          <v-list density="compact">
            <v-list-item>
              <v-list-item-title>事件ID</v-list-item-title>
              <v-list-item-subtitle>{{ selected_event.id }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>事件类型</v-list-item-title>
              <v-list-item-subtitle>
                <StatusChip
                  :status="get_event_status(selected_event.event_type)"
                  :text="selected_event.event_type"
                  size="small"
                />
              </v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>驾驶员</v-list-item-title>
              <v-list-item-subtitle>{{ selected_event.driver_id }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>设备</v-list-item-title>
              <v-list-item-subtitle>{{ selected_event.device_id }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>置信度</v-list-item-title>
              <v-list-item-subtitle>{{ Math.round(selected_event.confidence * 100) }}%</v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>发生时间</v-list-item-title>
              <v-list-item-subtitle>{{ format_datetime(selected_event.timestamp) }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="detail_dialog = false" text>关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { event_api } from '../../api'
import StatusChip from '../../components/common/StatusChip.vue'

// 状态管理
const loading = ref(false)
const events = ref<any[]>([])
const total_count = ref(0)
const current_page = ref(1)
const page_size = ref(10)
const detail_dialog = ref(false)
const selected_event = ref<any>(null)

// 筛选条件
const filter = reactive({
  start_date: '',
  end_date: '',
  driver_id: '',
  event_type: '',
})

// 事件类型选项
const event_type_options = [
  '疲劳驾驶',
  '危险行为',
  // '闭眼',
  // '打哈欠',
  '使用手机',
  '抽烟',
  '饮食',
]

// 表格列定义
const table_headers = [
  { title: '事件ID', key: 'id', width: '100px' },
  { title: '事件类型', key: 'event_type', width: '120px' },
  { title: '驾驶员', key: 'driver_id', width: '100px' },
  { title: '设备', key: 'device_id', width: '100px' },
  { title: '置信度', key: 'confidence', width: '150px' },
  { title: '发生时间', key: 'timestamp', width: '180px' },
  { title: '操作', key: 'actions', width: '80px', sortable: false },
]

// 计算总页数
const total_pages = computed(() => 
  Math.ceil(total_count.value / page_size.value)
)

// 获取事件状态
const get_event_status = (event_type: string): 'normal' | 'warning' | 'danger' => {
  const danger_events = ['疲劳驾驶', '危险行为']
  const warning_events = ['打哈欠', '闭眼', '使用手机', '抽烟','饮食']
  
  if (danger_events.includes(event_type)) {
    return 'danger'
  } else if (warning_events.includes(event_type)) {
    return 'warning'
  }
  return 'normal'
}

// 获取置信度颜色
const get_confidence_color = (confidence: number): string => {
  if (confidence >= 0.8) return 'success'
  if (confidence >= 0.6) return 'warning'
  return 'error'
}

// 格式化日期时间
const format_datetime = (timestamp: string): string => {
  return new Date(timestamp).toLocaleString('zh-CN')
}

// 加载事件数据
const load_events = async () => {
  loading.value = true
  try {
    const params: any = {
      limit: page_size.value,
      offset: (current_page.value - 1) * page_size.value,
    }

    // 添加筛选条件
    if (filter.start_date) {
      params.start_time = filter.start_date + 'T00:00:00'
    }
    if (filter.end_date) {
      params.end_time = filter.end_date + 'T23:59:59'
    }
    if (filter.driver_id) {
      params.driver_id = filter.driver_id
    }
    if (filter.event_type) {
      params.event_type = filter.event_type
    }

    const response = await event_api.get_events(params)
    events.value = response.data.events || []
    total_count.value = response.data.total || 0
  } catch (error) {
    console.error('加载事件数据失败:', error)
    events.value = []
    total_count.value = 0
  } finally {
    loading.value = false
  }
}

// 搜索事件
const search_events = () => {
  current_page.value = 1
  load_events()
}

// 查看事件详情
const view_event_detail = (event: any) => {
  selected_event.value = event
  detail_dialog.value = true
}

// 导出结果
const export_results = () => {
  // TODO: 实现导出功能
  console.log('导出功能待实现')
}

// 初始化数据
onMounted(() => {
  // 设置默认时间范围（最近7天）
  const today = new Date()
  const seven_days_ago = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
  
  filter.start_date = seven_days_ago.toISOString().split('T')[0]
  filter.end_date = today.toISOString().split('T')[0]
  
  load_events()
})
</script>

<style scoped>
.events-view {
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

/* 美化表格 - 统一配色 */
:deep(.v-data-table) {
  background: transparent;
}

:deep(.v-data-table-header) {
  background: rgba(231, 209, 187, 0.1);
}

:deep(.v-data-table__td) {
  border-bottom: 1px solid rgba(231, 209, 187, 0.1);
  color: #A096A2;
}

:deep(.v-data-table__tr:hover) {
  background: rgba(231, 209, 187, 0.05) !important;
}

/* 卡片样式 - 统一配色方案 */
:deep(.v-card) {
  backdrop-filter: blur(16px);
  background: linear-gradient(135deg, rgba(37, 40, 65, 0.8), rgba(61, 63, 91, 0.6));
  border: 1px solid rgba(231, 209, 187, 0.15);
  transition: all 300ms ease;
  color: #A096A2;
  box-shadow: 0 8px 32px rgba(21, 25, 49, 0.3);
}

:deep(.v-card:hover) {
  transform: translateY(-2px);
  box-shadow: 0 12px 48px rgba(21, 25, 49, 0.4), 0 0 0 1px rgba(231, 209, 187, 0.2);
}

/* 主标题样式优化 - 使用新配色方案 */
h1 {
  background: linear-gradient(135deg, #E7D1BB 0%, #A096A5 50%, #c8b39e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 2px 8px rgba(231, 209, 187, 0.2);
}
</style>