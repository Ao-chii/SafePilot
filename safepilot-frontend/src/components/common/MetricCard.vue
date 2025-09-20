<!--
  指标卡片组件
  显示关键指标的统一卡片样式
-->
<template>
  <v-card
    :loading="loading"
    class="metric-card elevation-2"
    :class="{ 'metric-card--clickable': clickable }"
    @click="handle_click"
  >
    <v-card-text class="pb-2">
      <div class="d-flex align-center justify-space-between">
        <div class="metric-content">
          <div class="metric-title text-body-2 text-grey-darken-1">
            {{ title }}
          </div>
          <div class="metric-value text-h4 font-weight-bold mt-1">
            {{ formatted_value }}
          </div>
          <div 
            v-if="subtitle"
            class="metric-subtitle text-caption text-grey-darken-2 mt-1"
          >
            {{ subtitle }}
          </div>
        </div>
        
        <div class="metric-icon">
          <v-avatar
            :color="icon_color"
            size="48"
            class="elevation-1"
          >
            <v-icon
              :icon="icon"
              size="24"
              color="white"
            />
          </v-avatar>
        </div>
      </div>
      
      <!-- 趋势指示器 -->
      <div 
        v-if="trend !== undefined"
        class="d-flex align-center mt-3"
      >
        <v-icon
          :icon="trend_icon"
          :color="trend_color"
          size="16"
          class="mr-1"
        />
        <span
          :class="`text-caption font-weight-medium ${trend_color}--text`"
        >
          {{ Math.abs(trend) }}%
        </span>
        <span class="text-caption text-grey-darken-2 ml-1">
          较昨日
        </span>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title: string
  value: number | string
  subtitle?: string
  icon: string
  icon_color?: string
  trend?: number // 正数表示上升，负数表示下降
  loading?: boolean
  clickable?: boolean
  formatter?: (value: number | string) => string
}

const props = withDefaults(defineProps<Props>(), {
  icon_color: 'primary',
  loading: false,
  clickable: false,
})

const emit = defineEmits<{
  click: []
}>()

// 格式化数值显示
const formatted_value = computed(() => {
  if (props.formatter) {
    return props.formatter(props.value)
  }
  
  if (typeof props.value === 'number') {
    // 大数值使用千分位分隔符
    if (props.value >= 1000) {
      return props.value.toLocaleString()
    }
  }
  
  return props.value.toString()
})

// 趋势图标
const trend_icon = computed(() => {
  if (props.trend === undefined) return ''
  
  if (props.trend > 0) {
    return 'mdi-trending-up'
  } else if (props.trend < 0) {
    return 'mdi-trending-down'
  } else {
    return 'mdi-minus'
  }
})

// 趋势颜色
const trend_color = computed(() => {
  if (props.trend === undefined) return 'grey'
  
  if (props.trend > 0) {
    return 'success'
  } else if (props.trend < 0) {
    return 'error'
  } else {
    return 'grey'
  }
})

// 点击处理
const handle_click = () => {
  if (props.clickable) {
    emit('click')
  }
}
</script>

<style scoped>
.metric-card {
  border-radius: 20px;
  transition: all 350ms cubic-bezier(0.4, 0, 0.2, 1);
  
  /* 使用新配色方案的玻璃拟态效果 */
  backdrop-filter: blur(16px) saturate(180%);
  background: linear-gradient(135deg, 
    rgba(37, 40, 65, 0.8) 0%, 
    rgba(61, 63, 91, 0.6) 100%);
  border: 1px solid rgba(231, 209, 187, 0.15);
  
  position: relative;
  overflow: hidden;
  color: #A096A2;
  
  box-shadow: 
    0 8px 32px rgba(21, 25, 49, 0.3),
    0 2px 8px rgba(21, 25, 49, 0.2),
    inset 0 1px 0 rgba(231, 209, 187, 0.08);
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(135deg, #E7D1BB 0%, #A096A5 50%, #c8b39e 100%);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 350ms ease;
}

.metric-card--clickable {
  cursor: pointer;
}

.metric-card--clickable:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow: 
    0 12px 40px rgba(231, 209, 187, 0.15),
    0 4px 16px rgba(21, 25, 49, 0.3),
    inset 0 1px 0 rgba(231, 209, 187, 0.12);
  border-color: rgba(231, 209, 187, 0.25);
  background: linear-gradient(135deg, 
    rgba(37, 40, 65, 0.9) 0%, 
    rgba(231, 209, 187, 0.08) 100%);
}

.metric-card--clickable:hover::before {
  transform: scaleX(1);
}

.metric-card .metric-icon .v-avatar {
  transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(21, 25, 49, 0.3);
}

.metric-card:hover .metric-icon .v-avatar {
  transform: scale(1.08) rotate(3deg);
  box-shadow: 0 6px 16px rgba(231, 209, 187, 0.3);
}

/* 文字颜色优化 - 使用新配色方案 */
.metric-card .metric-title {
  color: #A096A2;
}

.metric-card .metric-value {
  color: #E7D1BB;
}

.metric-card .metric-subtitle {
  color: #847a86;
}

.metric-content {
  flex: 1;
}

.metric-value {
  line-height: 1.2;
}

.metric-icon {
  flex-shrink: 0;
}
</style>