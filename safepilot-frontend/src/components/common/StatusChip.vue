<!--
  状态芯片组件
  统一的状态指示器：🟢正常 🟡警告 🔴危险 ⚫离线
-->
<template>
  <v-chip
    :color="chip_color"
    :variant="variant"
    :size="size"
    :prepend-icon="chip_icon"
    class="status-chip"
  >
    {{ display_text }}
  </v-chip>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  status: 'online' | 'warning' | 'danger' | 'offline' | 'normal'
  text?: string
  size?: 'x-small' | 'small' | 'default' | 'large' | 'x-large'
  variant?: 'flat' | 'elevated' | 'tonal' | 'outlined' | 'text' | 'plain'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'default',
  variant: 'flat',
})

// 状态颜色映射
const chip_color = computed(() => {
  switch (props.status) {
    case 'online':
    case 'normal':
      return 'success' // 绿色
    case 'warning':
      return 'warning' // 橙色
    case 'danger':
      return 'error'   // 红色
    case 'offline':
      return 'grey-darken-2' // 深灰
    default:
      return 'grey'
  }
})

// 状态图标映射
const chip_icon = computed(() => {
  switch (props.status) {
    case 'online':
    case 'normal':
      return 'mdi-check-circle'
    case 'warning':
      return 'mdi-alert-circle'
    case 'danger':
      return 'mdi-close-circle'
    case 'offline':
      return 'mdi-minus-circle'
    default:
      return 'mdi-help-circle'
  }
})

// 显示文本
const display_text = computed(() => {
  if (props.text) return props.text
  
  switch (props.status) {
    case 'online':
      return '在线'
    case 'normal':
      return '正常'
    case 'warning':
      return '警告'
    case 'danger':
      return '危险'
    case 'offline':
      return '离线'
    default:
      return '未知'
  }
})
</script>

<style scoped>
.status-chip {
  font-weight: 500;
}
</style>