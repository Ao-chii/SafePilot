<!--
  驾驶员管理页面
  实现驾驶员的增删改查功能
-->
<template>
  <div class="drivers-view">
    <!-- 页面标题 -->
    <div class="d-flex align-center justify-space-between mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold text-primary">
          驾驶员管理
        </h1>
        <p class="text-body-1 text-grey-darken-1 mt-1">
          管理系统中的驾驶员信息
        </p>
      </div>
      
      <v-btn
        @click="open_create_dialog"
        color="primary"
        prepend-icon="mdi-plus"
        size="large"
      >
        添加驾驶员
      </v-btn>
    </div>

    <!-- 搜索和筛选 -->
    <v-card class="mb-6" elevation="2">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="search_text"
              label="搜索驾驶员"
              placeholder="输入驾驶员ID或姓名"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="comfortable"
              clearable
              @input="search_drivers"
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
              @update:model-value="search_drivers"
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
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 驾驶员列表 -->
    <v-card elevation="2">
      <v-card-title class="d-flex align-center justify-space-between">
        <span>驾驶员列表</span>
        <span class="text-caption text-grey-darken-2">
          共 {{ filtered_drivers.length }} 名驾驶员
        </span>
      </v-card-title>

      <v-data-table
        :headers="table_headers"
        :items="filtered_drivers"
        :loading="loading"
        class="elevation-0"
        loading-text="正在加载驾驶员数据..."
        no-data-text="暂无驾驶员数据"
      >
        <!-- 状态显示 -->
        <template #item.is_active="{ item }">
          <StatusChip
            :status="item.is_active ? 'online' : 'offline'"
            :text="item.is_active ? '活跃' : '非活跃'"
            size="small"
          />
        </template>

        <!-- 创建时间格式化 -->
        <template #item.created_at="{ item }">
          {{ format_date(item.created_at) }}
        </template>

        <!-- 操作按钮 -->
        <template #item.actions="{ item }">
          <div class="d-flex">
            <v-btn
              @click="view_driver_detail(item)"
              icon
              size="small"
              variant="text"
              class="mr-1"
              title="查看详情"
            >
              <v-icon>mdi-eye</v-icon>
            </v-btn>
            <v-btn
              @click="edit_driver(item)"
              icon
              size="small"
              variant="text"
              class="mr-1"
              title="编辑"
            >
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
            <v-btn
              @click="toggle_driver_status(item)"
              icon
              size="small"
              variant="text"
              :color="item.is_active ? 'warning' : 'success'"
              class="mr-1"
              :title="item.is_active ? '暂停' : '启用'"
            >
              <v-icon>{{ item.is_active ? 'mdi-pause' : 'mdi-play' }}</v-icon>
            </v-btn>
            <v-btn
              @click="delete_driver(item)"
              icon
              size="small"
              variant="text"
              color="error"
              title="删除"
            >
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- 创建/编辑驾驶员对话框 -->
    <v-dialog v-model="driver_dialog" max-width="500">
      <v-card>
        <v-card-title>
          {{ editing_driver ? '编辑驾驶员' : '添加驾驶员' }}
        </v-card-title>
        
        <v-card-text>
          <v-form ref="form_ref" v-model="form_valid">
            <v-text-field
              v-model="driver_form.driver_id"
              label="驾驶员ID"
              :rules="[v => !!v || '请输入驾驶员ID']"
              :disabled="editing_driver"
              variant="outlined"
              class="mb-4"
            />
            
            <v-text-field
              v-model="driver_form.name"
              label="姓名"
              :rules="[v => !!v || '请输入姓名']"
              variant="outlined"
              class="mb-4"
            />
            
            <v-switch
              v-model="driver_form.is_active"
              label="是否活跃"
              color="primary"
              hide-details
            />
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn @click="close_driver_dialog" text>取消</v-btn>
          <v-btn
            @click="save_driver"
            :loading="saving"
            :disabled="!form_valid"
            color="primary"
          >
            {{ editing_driver ? '更新' : '创建' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 删除确认对话框 -->
    <v-dialog v-model="delete_dialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6">确认删除</v-card-title>
        <v-card-text>
          确定要删除驾驶员 "{{ driver_to_delete?.name }}" 吗？此操作无法撤销。
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { driver_api } from '../../api'
import StatusChip from '../../components/common/StatusChip.vue'

const router = useRouter()

// 状态管理
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const drivers = ref<any[]>([])
const search_text = ref('')
const status_filter = ref<boolean | null>(null)
const driver_dialog = ref(false)
const delete_dialog = ref(false)
const editing_driver = ref(false)
const driver_to_delete = ref<any>(null)
const form_ref = ref()
const form_valid = ref(false)

// 驾驶员表单
const driver_form = reactive({
  driver_id: '',
  name: '',
  is_active: true,
})

// 状态筛选选项
const status_options = [
  { title: '活跃', value: true },
  { title: '非活跃', value: false },
]

// 表格列定义
const table_headers = [
  { title: '驾驶员ID', key: 'driver_id', width: '150px' },
  { title: '姓名', key: 'name', width: '150px' },
  { title: '状态', key: 'is_active', width: '100px' },
  { title: '创建时间', key: 'created_at', width: '180px' },
  { title: '操作', key: 'actions', width: '150px', sortable: false },
]

// 筛选后的驾驶员列表
const filtered_drivers = computed(() => {
  let result = drivers.value

  // 文本搜索
  if (search_text.value) {
    const search = search_text.value.toLowerCase()
    result = result.filter(driver => 
      driver.driver_id.toLowerCase().includes(search) ||
      driver.name.toLowerCase().includes(search)
    )
  }

  // 状态筛选
  if (status_filter.value !== null) {
    result = result.filter(driver => driver.is_active === status_filter.value)
  }

  return result
})

// 格式化日期
const format_date = (date_string: string): string => {
  return new Date(date_string).toLocaleDateString('zh-CN')
}

// 加载驾驶员数据
const load_drivers = async () => {
  loading.value = true
  try {
    const response = await driver_api.get_drivers()
    drivers.value = response.data || []
  } catch (error) {
    console.error('加载驾驶员数据失败:', error)
    drivers.value = []
  } finally {
    loading.value = false
  }
}

// 搜索驾驶员
const search_drivers = () => {
  // 筛选逻辑在computed中处理，这里不需要额外操作
}

// 刷新数据
const refresh_data = () => {
  load_drivers()
}

// 查看驾驶员详情
const view_driver_detail = (driver: any) => {
  router.push(`/drivers/${driver.driver_id}`)
}

// 打开创建对话框
const open_create_dialog = () => {
  editing_driver.value = false
  driver_form.driver_id = ''
  driver_form.name = ''
  driver_form.is_active = true
  driver_dialog.value = true
}

// 编辑驾驶员
const edit_driver = (driver: any) => {
  editing_driver.value = true
  driver_form.driver_id = driver.driver_id
  driver_form.name = driver.name
  driver_form.is_active = driver.is_active
  driver_dialog.value = true
}

// 关闭驾驶员对话框
const close_driver_dialog = () => {
  driver_dialog.value = false
  if (form_ref.value) {
    form_ref.value.reset()
  }
}

// 保存驾驶员
const save_driver = async () => {
  if (!form_valid.value) return

  saving.value = true
  try {
    if (editing_driver.value) {
      // 更新驾驶员
      await driver_api.update_driver(driver_form.driver_id, {
        name: driver_form.name,
        is_active: driver_form.is_active,
      })
    } else {
      // 创建驾驶员
      await driver_api.create_driver({
        driver_id: driver_form.driver_id,
        name: driver_form.name,
        is_active: driver_form.is_active,
      })
    }
    
    close_driver_dialog()
    load_drivers() // 重新加载数据
  } catch (error) {
    console.error('保存驾驶员失败:', error)
  } finally {
    saving.value = false
  }
}

// 切换驾驶员状态
const toggle_driver_status = async (driver: any) => {
  try {
    await driver_api.update_driver(driver.driver_id, {
      is_active: !driver.is_active,
    })
    load_drivers() // 重新加载数据
  } catch (error) {
    console.error('更新驾驶员状态失败:', error)
  }
}

// 删除驾驶员
const delete_driver = (driver: any) => {
  driver_to_delete.value = driver
  delete_dialog.value = true
}

// 确认删除
const confirm_delete = async () => {
  if (!driver_to_delete.value) return

  deleting.value = true
  try {
    await driver_api.delete_driver(driver_to_delete.value.driver_id)
    delete_dialog.value = false
    driver_to_delete.value = null
    load_drivers() // 重新加载数据
  } catch (error) {
    console.error('删除驾驶员失败:', error)
  } finally {
    deleting.value = false
  }
}

// 初始化
onMounted(() => {
  load_drivers()
})
</script>

<style scoped>
.drivers-view {
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