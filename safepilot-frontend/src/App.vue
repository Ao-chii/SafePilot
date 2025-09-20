<script setup lang="ts">
import { ref, onMounted } from 'vue'

// 页面加载状态
const loading = ref(true)

// 页面加载完成后隐藏加载指示器
onMounted(() => {
  setTimeout(() => {
    loading.value = false
  }, 800) // 给一个短暂的加载时间
})
</script>

<template>
  <v-app>
    <!-- 全局加载指示器 -->
    <v-fade-transition>
      <div 
        v-if="loading" 
        class="loading-overlay"
      >
        <div class="loading-content">
          <div class="loading-logo">
            <v-avatar
              size="80"
              class="elevation-8 mb-4"
            >
              <v-icon
                size="48"
                color="white"
              >
                mdi-shield-car
              </v-icon>
            </v-avatar>
          </div>
          
          <h2 class="text-h4 font-weight-bold text-white mb-4">
            SafePilot
          </h2>
          
          <v-progress-circular
            indeterminate
            color="secondary"
            size="48"
            width="4"
          />
          
          <p class="text-subtitle-1 text-white-lighten-2 mt-4">
            正在初始化系统...
          </p>
        </div>
      </div>
    </v-fade-transition>
    
    <!-- 主应用内容 -->
    <router-view v-if="!loading" />
  </v-app>
</template>

<style>
/* 全局样式 */
.v-application {
  font-family: 'Roboto', sans-serif;
}

/* 根据新配色方案定义 CSS 变量 */
:root {
  --primary-100: #E7D1BB;
  --primary-200: #c8b39e;
  --primary-300: #84725e;
  --accent-100: #A096A5;
  --accent-200: #463e4b;
  --text-100: #A096A2;
  --text-200: #847a86;
  --bg-100: #151931;
  --bg-200: #252841;
  --bg-300: #3d3f5b;
}

/* 加载覆盖层 - 使用新配色方案的深邃渐变 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(180deg, #151931 0%, #252841 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  overflow: hidden;
}

.loading-overlay::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 30%, rgba(231, 209, 187, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(160, 150, 165, 0.06) 0%, transparent 50%),
    radial-gradient(circle at 40% 60%, rgba(200, 179, 158, 0.05) 0%, transparent 45%);
  animation: backgroundShift 20s ease-in-out infinite;
}

/* 微妙的几何装饰 */
.loading-overlay::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(45deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(-45deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 60px 60px;
  opacity: 0.3;
  animation: geometricFloat 15s ease-in-out infinite;
}

@keyframes backgroundShift {
  0%, 100% {
    transform: scale(1) rotate(0deg);
    opacity: 0.3;
  }
  50% {
    transform: scale(1.05) rotate(0.5deg);
    opacity: 0.4;
  }
}

@keyframes geometricFloat {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-10px) rotate(1deg);
  }
}

.loading-content {
  text-align: center;
  position: relative;
  z-index: 1;
  animation: fadeInUp 0.8s ease-out;
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

.loading-logo .v-avatar {
  background: linear-gradient(135deg, #252841 0%, #E7D1BB 100%);
  box-shadow: 
    0 8px 32px rgba(21, 25, 49, 0.4),
    0 0 0 4px rgba(231, 209, 187, 0.2),
    0 0 0 8px rgba(160, 150, 165, 0.1);
  animation: float 3s ease-in-out infinite, gentlePulse 2s ease-in-out infinite alternate;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-8px);
  }
}

@keyframes gentlePulse {
  from {
    box-shadow: 
      0 8px 32px rgba(21, 25, 49, 0.4),
      0 0 0 4px rgba(231, 209, 187, 0.2),
      0 0 0 8px rgba(160, 150, 165, 0.1);
  }
  to {
    box-shadow: 
      0 12px 40px rgba(21, 25, 49, 0.5),
      0 0 0 6px rgba(231, 209, 187, 0.3),
      0 0 0 12px rgba(160, 150, 165, 0.15);
  }
}

/* 流畅动画 */
.page-transition-enter-active,
.page-transition-leave-active {
  transition: all 250ms ease-out;
}

.page-transition-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.page-transition-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* 按钮交互动画 */
.v-btn {
  transition: all 180ms cubic-bezier(0.4, 0, 0.2, 1) !important;
  transform-origin: center;
}

.v-btn:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.v-btn:active {
  transform: translateY(0) scale(0.98);
  transition: all 100ms cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* 卡片层次感和动画 */
.v-card {
  transition: all 250ms cubic-bezier(0.4, 0, 0.2, 1);
  transform-origin: center;
}

.v-card:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12), 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* 输入框焦点动画 */
.v-field {
  transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.v-field:hover {
  transform: translateY(-1px);
}

.v-field--focused {
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2) !important;
}

/* 确保在所有设备上都有正确的高度 */
html, body {
  height: 100%;
  overflow-x: hidden;
}

#app {
  height: 100%;
  min-height: 100vh;
}
</style>
