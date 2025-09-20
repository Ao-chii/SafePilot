<!--
  用户登录页面 - 完整版本
-->
<template>
  <div class="login-form">
    <!-- Logo和标题 -->
    <div class="text-center mb-8">
      <!-- 使用Unicode符号作为backup -->
      <div class="logo-icon mb-4">
        🚗
      </div>
      <h1 class="text-h4 font-weight-bold mb-2">
        SafePilot
      </h1>
      <p class="text-subtitle-1 text-medium-emphasis">
        驾驶员安全监控系统
      </p>
    </div>
    
    <v-card class="pa-6" elevation="2" rounded="lg">
      <v-form
        ref="form_ref"
        v-model="form_valid"
        @submit.prevent="handle_login"
      >
        <!-- 用户名输入 -->
        <v-text-field
          v-model="form_data.username"
          :rules="username_rules"
          label="用户名"
          prepend-inner-icon="👤"
          variant="outlined"
          :disabled="loading"
          autocomplete="username"
          class="mb-4"
          clearable
        />
        
        <!-- 密码输入 -->
        <v-text-field
          v-model="form_data.password"
          :rules="password_rules"
          :type="show_password ? 'text' : 'password'"
          label="密码"
          prepend-inner-icon="🔒"
          :append-inner-icon="show_password ? '👁️' : '🙈'"
          variant="outlined"
          :disabled="loading"
          autocomplete="current-password"
          class="mb-4"
          @click:append-inner="show_password = !show_password"
        />
        
        <!-- 记住密码选项 -->
        <v-checkbox
          v-model="form_data.remember"
          label="记住密码"
          color="primary"
          class="mb-4"
          hide-details
        />
        
        <!-- 错误提示 -->
        <v-alert
          v-if="error_message"
          type="error"
          variant="tonal"
          class="mb-4"
          :text="error_message"
          closable
          @click:close="error_message = ''"
        />
        
        <!-- 登录按钮 -->
        <v-btn
          :loading="loading"
          :disabled="!form_valid || loading"
          type="submit"
          color="primary"
          size="large"
          block
          class="mb-4"
        >
          <span style="margin-right: 8px;">🔑</span>
          {{ loading ? '登录中...' : '登录' }}
        </v-btn>
        
        <!-- 忘记密码链接 -->
        <div class="text-center">
          <v-btn
            variant="text"
            color="primary"
            size="small"
            @click="handle_forgot_password"
          >
            忘记密码？
          </v-btn>
        </div>
      </v-form>
      
      <!-- 开发提示 -->
      <v-divider class="my-4" />
      <v-alert
        type="info"
        variant="outlined"
        density="compact"
        text="开发模式：默认账户 admin/admin123"
      />
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { auth_api } from '../../api'

const router = useRouter()
const auth_store = useAuthStore()

// 表单引用和验证状态
const form_ref = ref()
const form_valid = ref(false)
const loading = ref(false)
const show_password = ref(false)
const error_message = ref('')

// 表单数据 - 开发环境默认值
const form_data = reactive({
  username: 'admin',
  password: 'admin123',
  remember: false,
})

// 验证规则
const username_rules = [
  (v: string) => !!v || '请输入用户名',
  (v: string) => v.length >= 3 || '用户名至少3个字符',
]

const password_rules = [
  (v: string) => !!v || '请输入密码',
  (v: string) => v.length >= 6 || '密码至少6个字符',
]

// 登录处理
const handle_login = async () => {
  if (!form_valid.value) return
  
  loading.value = true
  error_message.value = ''
  
  try {
    // 临时处理：如果没有后端，直接跳转
    if (form_data.username === 'admin' && form_data.password === 'admin123') {
      // 模拟登录成功
      const mock_user = {
        id: 1,
        username: 'admin',
        email: 'admin@safepilot.com',
        first_name: '管理员',
        is_admin: true
      }
      
      auth_store.login('mock-token-12345', mock_user)
      
      // 如果选择记住密码，则保存到本地存储
      if (form_data.remember && typeof Storage !== 'undefined') {
        localStorage.setItem('remembered_username', form_data.username)
        localStorage.setItem('remember_password', 'true')
      } else {
        localStorage.removeItem('remembered_username')
        localStorage.removeItem('remember_password')
      }
      
      router.push('/dashboard')
      return
    }
    
    // 正常API调用
    const response = await auth_api.login(
      form_data.username,
      form_data.password
    )
    
    const { access_token, user } = response.data
    
    // 保存认证信息
    auth_store.login(access_token, user)
    
    // 如果选择记住密码，则保存到本地存储
    if (form_data.remember && typeof Storage !== 'undefined') {
      localStorage.setItem('remembered_username', form_data.username)
      localStorage.setItem('remember_password', 'true')
    }
    
    // 跳转到仪表板
    router.push('/dashboard')
    
  } catch (error: any) {
    // 如果是网络错误，给出友好提示
    if (error.message.includes('Network Error') || error.code === 'ERR_NETWORK') {
      error_message.value = '无法连接到服务器，请检查网络连接或使用默认账户：admin/admin123'
    } else {
      error_message.value = error.message || '登录失败，请检查用户名和密码'
    }
  } finally {
    loading.value = false
  }
}

// 忘记密码处理
const handle_forgot_password = () => {
  // TODO: 实现忘记密码功能
  alert('忘记密码功能暂未实现，请联系管理员重置密码')
}

// 页面加载时检查是否有记住的用户名
if (typeof Storage !== 'undefined') {
  const remembered_username = localStorage.getItem('remembered_username')
  const remember_password = localStorage.getItem('remember_password')
  
  if (remembered_username && remember_password === 'true') {
    form_data.username = remembered_username
    form_data.remember = true
  }
}
</script>

<style scoped>
.logo-icon {
  font-size: 72px;
  line-height: 1;
}

.login-form {
  width: 100%;
  max-width: 450px;
  margin: 0 auto;
  padding: 2rem;
}

/* 响应式设计 */
@media (max-width: 600px) {
  .login-form {
    max-width: 400px;
    padding: 1rem;
  }

}
</style>