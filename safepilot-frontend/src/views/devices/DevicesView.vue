<!--
  设备管理页面
  实现需求文档中的设备状态监控和管理功能
-->
<template>
  <div class="devices-view">
    <!-- 页面标题 -->
    <div class="d-flex align-center justify-space-between mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold text-primary">
          设备管理
        </h1>
        <p class="text-body-1 text-grey-darken-1 mt-1">
          监控和管理车载检测设备
        </p>
      </div>
      
      <v-btn
        @click="open_create_dialog"
        color="primary"
        prepend-icon="mdi-plus"
        size="large"
      >
        添加设备
      </v-btn>
    </div>

    <!-- 设备状态概览 -->
    <v-row class="mb-6">
      <v-col cols="12" md="3">
        <MetricCard
          title="总设备数"
          :value="devices.length"
          subtitle="已注册设备"
          icon="mdi-cellphone-link"
          icon-color="info"
        />
      </v-col>
      <v-col cols="12" md="3">
        <MetricCard
          title="在线设备"
          :value="online_devices_count"
          subtitle="正常运行中"
          icon="mdi-check-circle"
          icon-color="success"
        />
      </v-col>
      <v-col cols="12" md="3">
        <MetricCard
          title="离线设备"
          :value="offline_devices_count"
          subtitle="需要检查"
          icon="mdi-alert-circle"
          icon-color="warning"
        />
      </v-col>
      <v-col cols="12" md="3">
        <MetricCard
          title="在线率"
          :value="online_rate + '%'"
          subtitle="设备可用性"
          icon="mdi-chart-line"
          icon-color="primary"
        />
      </v-col>
    </v-row>

    <!-- 搜索和筛选 -->
    <v-card class="mb-6" elevation="2">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="search_text"
              label="搜索设备"
              placeholder="输入设备ID或名称"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="comfortable"
              clearable
              @input="search_devices"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="status_filter"
              label="状态筛选"
              :items="status_options"
              variant="outlined"
              density="comfortable"
              clearable
              @update:model-value="search_devices"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-btn
              @click="refresh_data"
              :loading="loading"
              variant="outlined"
              prepend-icon="mdi-refresh"
              block
            >
              刷新
            </v-btn>
          </v-col>
          <v-col cols="12" md="2">
            <v-btn
              @click="auto_refresh = !auto_refresh"
              :color="auto_refresh ? 'success' : 'default'"
              variant="outlined"
              block
            >
              <v-icon>{{ auto_refresh ? 'mdi-pause' : 'mdi-play' }}</v-icon>
              自动刷新
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 设备列表 -->
    <v-card elevation="2">
      <v-card-title class="d-flex align-center justify-space-between">
        <span>设备列表</span>
        <div class="d-flex align-center">
          <span class="text-caption text-grey-darken-2 mr-4">
            共 {{ filtered_devices.length }} 台设备
          </span>
          <v-chip
            v-if="auto_refresh"
            size="small"
            color="success"
            prepend-icon="mdi-autorenew"
          >
            自动刷新中
          </v-chip>
        </div>
      </v-card-title>

      <v-data-table
        :headers="table_headers"
        :items="filtered_devices"
        :loading="loading"
        class="elevation-0"
        loading-text="正在加载设备数据..."
        no-data-text="暂无设备数据"
      >
        <!-- 设备状态显示 -->
        <template #item.is_active="{ item }">
          <div class="d-flex align-center">
            <v-icon
              :color="item.is_active ? 'success' : 'error'"
              class="mr-2"
              size="small"
            >
              {{ item.is_active ? 'mdi-circle' : 'mdi-circle-outline' }}
            </v-icon>
            <StatusChip
              :status="item.is_active ? 'online' : 'offline'"
              :text="item.is_active ? '在线' : '离线'"
              size="small"
            />
          </div>
        </template>

        <!-- 信号强度 -->
        <template #item.signal_strength="{ item }">
          <div class="d-flex align-center">
            <v-progress-linear
              :model-value="item.signal_strength || 0"
              :color="get_signal_color(item.signal_strength || 0)"
              height="6"
              rounded
              class="mr-2"
              style="min-width: 60px;"
            />
            <span class="text-caption">{{ item.signal_strength || 0 }}%</span>
          </div>
        </template>

        <!-- 最后上线时间 -->
        <template #item.last_seen="{ item }">
          <div>
            <div>{{ format_datetime(item.last_seen) }}</div>
            <div class="text-caption text-grey-darken-2">
              {{ get_time_ago(item.last_seen) }}
            </div>
          </div>
        </template>

        <!-- 操作按钮 -->
        <template #item.actions="{ item }">
          <div class="d-flex">
            <v-btn
              @click="view_device_detail(item)"
              icon
              size="small"
              variant="text"
              class="mr-1"
            >
              <v-icon>mdi-eye</v-icon>
            </v-btn>
            <v-btn
              @click="edit_device(item)"
              icon
              size="small"
              variant="text"
              class="mr-1"
            >
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
            <v-btn
              @click="remote_config(item)"
              icon
              size="small"
              variant="text"
              :disabled="!item.is_active"
              class="mr-1"
            >
              <v-icon>mdi-cog</v-icon>
            </v-btn>
            <v-btn
              @click="delete_device(item)"
              icon
              size="small"
              variant="text"
              color="error"
            >
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- 创建/编辑设备对话框 -->
    <v-dialog v-model="device_dialog" max-width="600">
      <v-card>
        <v-card-title>
          {{ editing_device ? '编辑设备' : '添加设备' }}
        </v-card-title>
        
        <v-card-text>
          <v-form ref="form_ref" v-model="form_valid">
            <v-text-field
              v-model="device_form.device_id"
              label="设备ID"
              :rules="[v => !!v || '请输入设备ID']"
              :disabled="editing_device"
              variant="outlined"
              class="mb-4"
            />
            
            <v-text-field
              v-model="device_form.name"
              label="设备名称"
              :rules="[v => !!v || '请输入设备名称']"
              variant="outlined"
              class="mb-4"
            />
            
            <v-textarea
              v-model="device_form.description"
              label="设备描述"
              variant="outlined"
              rows="3"
              class="mb-4"
            />
            
            <v-switch
              v-model="device_form.is_active"
              label="是否启用"
              color="primary"
              hide-details
            />
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn @click="close_device_dialog" text>取消</v-btn>
          <v-btn
            @click="save_device"
            :loading="saving"
            :disabled="!form_valid"
            color="primary"
          >
            {{ editing_device ? '更新' : '创建' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 设备详情对话框 -->
    <v-dialog v-model="detail_dialog" max-width="700">
      <v-card v-if="selected_device">
        <v-card-title>设备详情</v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <v-list density="compact">
                <v-list-item>
                  <v-list-item-title>设备ID</v-list-item-title>
                  <v-list-item-subtitle>{{ selected_device.device_id }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>设备名称</v-list-item-title>
                  <v-list-item-subtitle>{{ selected_device.name }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>设备状态</v-list-item-title>
                  <v-list-item-subtitle>
                    <StatusChip
                      :status="selected_device.is_active ? 'online' : 'offline'"
                      :text="selected_device.is_active ? '在线' : '离线'"
                      size="small"
                    />
                  </v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>信号强度</v-list-item-title>
                  <v-list-item-subtitle>{{ selected_device.signal_strength || 0 }}%</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-col>
            <v-col cols="12" md="6">
              <v-list density="compact">
                <v-list-item>
                  <v-list-item-title>最后上线</v-list-item-title>
                  <v-list-item-subtitle>{{ format_datetime(selected_device.last_seen) }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>创建时间</v-list-item-title>
                  <v-list-item-subtitle>{{ format_datetime(selected_device.created_at) }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>设备描述</v-list-item-title>
                  <v-list-item-subtitle>{{ selected_device.description || '无' }}</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="detail_dialog = false" text>关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 删除确认对话框 -->
    <v-dialog v-model="delete_dialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6">确认删除</v-card-title>
        <v-card-text>
          确定要删除设备 "{{ device_to_delete?.name }}" 吗？此操作无法撤销。
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="delete_dialog = false" text>取消</v-btn>
          <v-btn
            @click="confirm_delete"
            :loading="deleting"
            color="error"
          >
            删除
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { device_api } from '../../api'
import StatusChip from '../../components/common/StatusChip.vue'
import MetricCard from '../../components/common/MetricCard.vue'

// 状态管理
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const devices = ref<any[]>([])
const search_text = ref('')
const status_filter = ref<boolean | null>(null)
const device_dialog = ref(false)
const detail_dialog = ref(false)
const delete_dialog = ref(false)
const editing_device = ref(false)
const device_to_delete = ref<any>(null)
const selected_device = ref<any>(null)
const form_ref = ref()
const form_valid = ref(false)
const auto_refresh = ref(false)
const refresh_interval = ref<number | null>(null)

// 设备表单
const device_form = reactive({
  device_id: '',
  name: '',
  description: '',
  is_active: true,
})

// 状态筛选选项
const status_options = [
  { title: '在线', value: true },
  { title: '离线', value: false },
]

// 表格列定义
const table_headers = [
  { title: '设备ID', key: 'device_id', width: '150px' },
  { title: '设备名称', key: 'name', width: '150px' },
  { title: '状态', key: 'is_active', width: '120px' },
  { title: '信号强度', key: 'signal_strength', width: '150px' },
  { title: '最后上线', key: 'last_seen', width: '180px' },
  { title: '操作', key: 'actions', width: '200px', sortable: false },
]

// 计算属性
const filtered_devices = computed(() => {
  let result = devices.value

  if (search_text.value) {
    const search = search_text.value.toLowerCase()
    result = result.filter(device => 
      device.device_id.toLowerCase().includes(search) ||
      device.name.toLowerCase().includes(search)
    )
  }

  if (status_filter.value !== null) {
    result = result.filter(device => device.is_active === status_filter.value)
  }

  return result
})

const online_devices_count = computed(() => 
  devices.value.filter(device => device.is_active).length
)

const offline_devices_count = computed(() => 
  devices.value.filter(device => !device.is_active).length
)

const online_rate = computed(() => 
  devices.value.length ? Math.round((online_devices_count.value / devices.value.length) * 100) : 0
)

// 工具函数
const get_signal_color = (strength: number): string => {
  if (strength >= 80) return 'success'
  if (strength >= 60) return 'warning'
  return 'error'
}

const format_datetime = (datetime: string): string => {
  return new Date(datetime).toLocaleString('zh-CN')
}

const get_time_ago = (datetime: string): string => {
  const now = new Date().getTime()
  const time = new Date(datetime).getTime()
  const diff = now - time
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${Math.floor(diff / 86400000)}天前`
}

// 数据操作
const load_devices = async () => {
  loading.value = true
  try {
    const response = await device_api.get_devices()
    devices.value = response.data || [] 
    // 模拟一些设备状态数据（实际应该从API获取）
    devices.value = devices.value.map(device => ({
      ...device,
      signal_strength: Math.floor(Math.random() * 100),
      last_seen: device.updated_at || device.created_at,
    }))
  } catch (error) {
    console.error('加载设备数据失败:', error)
    devices.value = []
  } finally {
    loading.value = false
  }
}

const search_devices = () => {
  // 筛选逻辑在computed中处理
}

const refresh_data = () => {
  load_devices()
}

// 设备操作
const open_create_dialog = () => {
  editing_device.value = false
  device_form.device_id = ''
  device_form.name = ''
  device_form.description = ''
  device_form.is_active = true
  device_dialog.value = true
}

const edit_device = (device: any) => {
  editing_device.value = true
  device_form.device_id = device.device_id
  device_form.name = device.name
  device_form.description = device.description || ''
  device_form.is_active = device.is_active
  device_dialog.value = true
}

const close_device_dialog = () => {
  device_dialog.value = false
  if (form_ref.value) {
    form_ref.value.reset()
  }
}

const save_device = async () => {
  if (!form_valid.value) return

  saving.value = true
  try {
    if (editing_device.value) {
      await device_api.update_device(device_form.device_id, {
        name: device_form.name,
        description: device_form.description,
        is_active: device_form.is_active,
      })
    } else {
      await device_api.create_device({
        device_id: device_form.device_id,
        name: device_form.name,
        description: device_form.description,
        is_active: device_form.is_active,
      })
    }
    
    close_device_dialog()
    load_devices()
  } catch (error) {
    console.error('保存设备失败:', error)
  } finally {
    saving.value = false
  }
}

const view_device_detail = (device: any) => {
  selected_device.value = device
  detail_dialog.value = true
}

const remote_config = (device: any) => {
  // TODO: 实现远程配置功能
  console.log('远程配置设备:', device.device_id)
}

const delete_device = (device: any) => {
  device_to_delete.value = device
  delete_dialog.value = true
}

const confirm_delete = async () => {
  if (!device_to_delete.value) return

  deleting.value = true
  try {
    await device_api.delete_device(device_to_delete.value.device_id)
    delete_dialog.value = false
    device_to_delete.value = null
    load_devices()
  } catch (error) {
    console.error('删除设备失败:', error)
  } finally {
    deleting.value = false
  }
}

// 自动刷新
const start_auto_refresh = () => {
  if (refresh_interval.value) {
    clearInterval(refresh_interval.value)
  }
  refresh_interval.value = setInterval(() => {
    load_devices()
  }, 30000) // 30秒刷新一次
}

const stop_auto_refresh = () => {
  if (refresh_interval.value) {
    clearInterval(refresh_interval.value)
    refresh_interval.value = null
  }
}

// 监听自动刷新状态
const toggleAutoRefresh = () => {
  if (auto_refresh.value) {
    start_auto_refresh()
  } else {
    stop_auto_refresh()
  }
}

// 生命周期
onMounted(() => {
  load_devices()
})

onUnmounted(() => {
  stop_auto_refresh()
})
</script>

<style scoped>
.devices-view {
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

/* 主标题样式 */
/* 主标题样式优化 - 使用新配色方案 */
h1 {
  background: linear-gradient(135deg, #E7D1BB 0%, #A096A5 50%, #c8b39e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 2px 8px rgba(231, 209, 187, 0.2);
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
</style>