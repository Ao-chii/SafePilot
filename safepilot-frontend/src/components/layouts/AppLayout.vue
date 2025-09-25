<!--
  主应用布局
  包含导航栏、侧边栏和主内容区域
-->
<template>
  <v-layout>
    <!-- 应用栏 -->
    <v-app-bar
      :elevation="3"
      color="primary"
      dark
      app
      class="app-header"
    >
      <v-app-bar-nav-icon
        @click="drawer = !drawer"
      />
      
      <v-toolbar-title class="font-weight-bold">
        {{ app_title }}
      </v-toolbar-title>
      
      <v-spacer />
      
      <!-- 用户菜单 -->
      <v-menu offset-y>
        <template #activator="{ props }">
          <v-btn
            icon
            v-bind="props"
          >
            <v-avatar size="32">
              <v-icon>mdi-account</v-icon>
            </v-avatar>
          </v-btn>
        </template>
        
        <v-list>
          <v-list-item>
            <v-list-item-title class="font-weight-medium">
              {{ user_display_name }}
            </v-list-item-title>
            <v-list-item-subtitle>
              {{ user?.email }}
            </v-list-item-subtitle>
          </v-list-item>
          
          <v-divider />
          
          <v-list-item
            prepend-icon="mdi-account-circle"
            title="个人资料"
            @click="go_to_profile"
          />
          
          <v-list-item
            prepend-icon="mdi-cog"
            title="设置"
            @click="go_to_settings"
          />
          
          <v-divider />
          
          <v-list-item
            prepend-icon="mdi-logout"
            title="退出登录"
            @click="handle_logout"
          />
        </v-list>
      </v-menu>
    </v-app-bar>
    
    <!-- 侧边导航栏 -->
    <v-navigation-drawer
      v-model="drawer"
      :rail="rail"
      permanent
      app
    >
      <template #prepend>
        <div class="nav-header">
          <v-btn
            variant="text"
            :icon="rail ? 'mdi-chevron-right' : 'mdi-chevron-left'"
            class="nav-toggle-btn"
            @click="rail = !rail"
          />
        </div>
      </template>
      
      <v-divider />
      
      <v-list density="compact" nav>
        <v-list-item
          v-for="item in nav_items"
          :key="item.path"
          :prepend-icon="item.icon"
          :title="item.title"
          :value="item.path"
          :to="item.path"
          :active="$route.path === item.path"
        />
      </v-list>
    </v-navigation-drawer>
    
    <!-- 主内容区域 -->
    <v-main>
      <v-container fluid class="pa-4 full-width-container">
        <transition
          name="page-transition"
          mode="out-in"
        >
          <router-view />
        </transition>
      </v-container>
    </v-main>
  </v-layout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const auth_store = useAuthStore()

// 应用标题
const app_title = import.meta.env.VITE_APP_TITLE || 'SafePilot'

// 抽屉和边栏状态
const drawer = ref(true)
const rail = ref(false)

// 用户信息
const user = computed(() => auth_store.user)
const user_display_name = computed(() => auth_store.user_display_name)

// 用户头像
const user_avatar = computed(() => {
  // 可以后续添加用户头像逻辑
  return undefined
})

// 导航菜单项
const nav_items = [
  {
    title: '仪表板',
    icon: 'mdi-view-dashboard',
    path: '/dashboard',
  },
  {
    title: '实时监控',
    icon: 'mdi-video-box',
    path: '/monitor',
  },
  {
    title: '设备管理',
    icon: 'mdi-cellphone-link',
    path: '/devices',
  },
  {
    title: '驾驶员管理',
    icon: 'mdi-account-group',
    path: '/drivers',
  },
  {
    title: '事件记录',
    icon: 'mdi-alert-circle-outline',
    path: '/events',
  },
  {
    title: '统计分析',
    icon: 'mdi-chart-line',
    path: '/stats',
  },
]

// 导航方法
const go_to_profile = () => {
  router.push('/profile')
}

const go_to_settings = () => {
  router.push('/settings')
}

// 退出登录
const handle_logout = () => {
  auth_store.logout()
  router.push('/auth/login')
}
</script>

<style scoped>
:deep(.v-navigation-drawer__content) {
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #252841 0%, #E7D1BB 100%) !important;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(231, 209, 187, 0.2);
  box-shadow: 0 2px 8px rgba(21, 25, 49, 0.3);
}

:deep(.v-navigation-drawer) {
  border-right: 1px solid rgba(231, 209, 187, 0.15);
  background: linear-gradient(180deg, #252841 0%, #151931 100%);
  box-shadow: 2px 0 8px rgba(21, 25, 49, 0.2);
}

:deep(.v-list-item) {
  border-radius: 12px;
  margin: 4px 8px;
  transition: all 250ms ease;
  color: #A096A2;
}

:deep(.v-list-item:hover) {
  background: rgba(231, 209, 187, 0.12);
  transform: translateX(4px);
  color: #E7D1BB;
  box-shadow: 0 2px 8px rgba(231, 209, 187, 0.2);
}

:deep(.v-list-item--active) {
  background: linear-gradient(135deg, rgba(231, 209, 187, 0.2), rgba(160, 150, 165, 0.1));
  color: #E7D1BB;
  border-left: 3px solid #E7D1BB;
  box-shadow: 0 2px 8px rgba(231, 209, 187, 0.3);
}

:deep(.v-main) {
  background: linear-gradient(135deg, #151931 0%, #252841 100%);
  overflow-y: auto;
}

.full-width-container {
  width: 100%;
  max-width: 100%;
}

.nav-header {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 12px;
  min-height: 56px;
}

.nav-toggle-btn {
  color: #E7D1BB !important;
  transition: all 250ms ease;
}

.nav-toggle-btn:hover {
  background: rgba(231, 209, 187, 0.12) !important;
  transform: scale(1.1);
}
</style>