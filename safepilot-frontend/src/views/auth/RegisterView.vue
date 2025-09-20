<!--
  用户注册页面
-->
<template>
  <div class="register-form">
    <!-- Logo和标题 -->
    <div class="text-center mb-8">
      <div class="logo-icon mb-4">
        📝
      </div>
      <h1 class="text-h4 font-weight-bold mb-2">
        用户注册
      </h1>
      <p class="text-subtitle-1 text-medium-emphasis">
        创建您的SafePilot账户
      </p>
    </div>
    
    <v-card class="pa-6" elevation="2" rounded="lg">
      <v-form
        ref="form_ref"
        v-model="form_valid"
        @submit.prevent="handle_register"
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

        <!-- 邮箱输入 -->
        <v-text-field
          v-model="form_data.email"
          :rules="email_rules"
          label="邮箱地址"
          prepend-inner-icon="📧"
          variant="outlined"
          :disabled="loading"
          autocomplete="email"
          class="mb-4"
          clearable
        />

        <!-- 姓名输入 -->
        <v-row class="mb-4">
          <v-col cols="6">
            <v-text-field
              v-model="form_data.first_name"
              :rules="first_name_rules"
              label="姓"
              prepend-inner-icon="🏷️"
              variant="outlined"
              :disabled="loading"
              autocomplete="given-name"
            />
          </v-col>
          <v-col cols="6">
            <v-text-field
              v-model="form_data.last_name"
              label="名"
              variant="outlined"
              :disabled="loading"
              autocomplete="family-name"
            />
          </v-col>
        </v-row>

        <!-- 手机号输入 -->
        <v-text-field
          v-model="form_data.phone"
          :rules="phone_rules"
          label="手机号码"
          prepend-inner-icon="📱"
          variant="outlined"
          :disabled="loading"
          autocomplete="tel"
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
          autocomplete="new-password"
          class="mb-4"
          @click:append-inner="show_password = !show_password"
        />

        <!-- 确认密码输入 -->
        <v-text-field
          v-model="form_data.confirm_password"
          :rules="confirm_password_rules"
          :type="show_confirm_password ? 'text' : 'password'"
          label="确认密码"
          prepend-inner-icon="🔒"
          :append-inner-icon="show_confirm_password ? '👁️' : '🙈'"
          variant="outlined"
          :disabled="loading"
          autocomplete="new-password"
          class="mb-4"
          @click:append-inner="show_confirm_password = !show_confirm_password"
        />

        <!-- 密码强度指示器 -->
        <div class="mb-4">
          <div class="d-flex align-center justify-space-between mb-2">
            <span class="text-caption">密码强度</span>
            <span class="text-caption" :class="password_strength.color">
              {{ password_strength.text }}
            </span>
          </div>
          <v-progress-linear
            :model-value="password_strength.score"
            :color="password_strength.color"
            height="4"
          />
        </div>

        <!-- 用户角色选择 -->
        <v-select
          v-model="form_data.role"
          :items="role_options"
          label="用户角色"
          prepend-inner-icon="🎭"
          variant="outlined"
          :disabled="loading"
          class="mb-4"
        />

        <!-- 服务条款同意 -->
        <v-checkbox
          v-model="form_data.agree_terms"
          :rules="terms_rules"
          color="primary"
          class="mb-4"
        >
          <template #label>
            <span class="text-body-2">
              我已阅读并同意
              <a href="#" class="text-primary text-decoration-none" @click.prevent="show_terms = true">
                《服务条款》
              </a>
              和
              <a href="#" class="text-primary text-decoration-none" @click.prevent="show_privacy = true">
                《隐私政策》
              </a>
            </span>
          </template>
        </v-checkbox>
        
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

        <!-- 成功提示 -->
        <v-alert
          v-if="success_message"
          type="success"
          variant="tonal"
          class="mb-4"
          :text="success_message"
        />
        
        <!-- 注册按钮 -->
        <v-btn
          :loading="loading"
          :disabled="!form_valid || loading || password_strength.score < 75"
          type="submit"
          color="primary"
          size="large"
          block
          class="mb-4"
        >
          <span style="margin-right: 8px;">📝</span>
          {{ loading ? '注册中...' : '注册账户' }}
        </v-btn>
        
        <!-- 登录链接 -->
        <div class="text-center">
          <span class="text-body-2 text-grey-darken-2">
            已有账户？
          </span>
          <v-btn
            variant="text"
            color="primary"
            size="small"
            @click="$router.push('/auth/login')"
          >
            立即登录
          </v-btn>
        </div>
      </v-form>
    </v-card>

    <!-- 服务条款对话框 -->
    <v-dialog v-model="show_terms" max-width="600">
      <v-card>
        <v-card-title>服务条款</v-card-title>
        <v-card-text class="pa-4" style="max-height: 400px; overflow-y: auto;">
          <div class="text-body-2">
            <h3>1. 服务说明</h3>
            <p>SafePilot驾驶员安全监控系统为用户提供实时驾驶行为监测和分析服务。</p>
            
            <h3>2. 用户责任</h3>
            <p>用户应合法使用本系统，不得进行任何违法违规活动。</p>
            
            <h3>3. 隐私保护</h3>
            <p>我们承诺保护用户隐私，详见隐私政策。</p>
            
            <h3>4. 免责声明</h3>
            <p>本系统仅作为辅助工具，不能替代驾驶员的安全责任。</p>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="primary" @click="show_terms = false">我已了解</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 隐私政策对话框 -->
    <v-dialog v-model="show_privacy" max-width="600">
      <v-card>
        <v-card-title>隐私政策</v-card-title>
        <v-card-text class="pa-4" style="max-height: 400px; overflow-y: auto;">
          <div class="text-body-2">
            <h3>1. 信息收集</h3>
            <p>我们仅收集必要的用户信息和驾驶行为数据。</p>
            
            <h3>2. 信息使用</h3>
            <p>收集的信息仅用于提供服务和改进系统功能。</p>
            
            <h3>3. 信息保护</h3>
            <p>我们采用业界标准的安全措施保护用户数据。</p>
            
            <h3>4. 信息共享</h3>
            <p>除法律要求外，我们不会与第三方分享用户个人信息。</p>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="primary" @click="show_privacy = false">我已了解</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { auth_api } from '../../api'

const router = useRouter()

// 表单引用和验证状态
const form_ref = ref()
const form_valid = ref(false)
const loading = ref(false)
const show_password = ref(false)
const show_confirm_password = ref(false)
const show_terms = ref(false)
const show_privacy = ref(false)
const error_message = ref('')
const success_message = ref('')

// 表单数据
const form_data = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  phone: '',
  password: '',
  confirm_password: '',
  role: 'driver',
  agree_terms: false,
})

// 角色选项
const role_options = [
  { title: '驾驶员', value: 'driver' },
  { title: '管理员', value: 'admin' },
  { title: '监督员', value: 'supervisor' },
]

// 验证规则
const username_rules = [
  (v: string) => !!v || '请输入用户名',
  (v: string) => v.length >= 3 || '用户名至少3个字符',
  (v: string) => v.length <= 20 || '用户名最多20个字符',
  (v: string) => /^[a-zA-Z0-9_]+$/.test(v) || '用户名只能包含字母、数字和下划线',
]

const email_rules = [
  (v: string) => !!v || '请输入邮箱地址',
  (v: string) => /.+@.+\..+/.test(v) || '请输入有效的邮箱地址',
]

const first_name_rules = [
  (v: string) => !!v || '请输入姓氏',
  (v: string) => v.length >= 1 || '姓氏不能为空',
]

const phone_rules = [
  (v: string) => !!v || '请输入手机号码',
  (v: string) => /^1[3-9]\d{9}$/.test(v) || '请输入有效的手机号码',
]

const password_rules = [
  (v: string) => !!v || '请输入密码',
  (v: string) => v.length >= 8 || '密码至少8个字符',
  (v: string) => /[A-Z]/.test(v) || '密码必须包含大写字母',
  (v: string) => /[a-z]/.test(v) || '密码必须包含小写字母',
  (v: string) => /\d/.test(v) || '密码必须包含数字',
]

const confirm_password_rules = [
  (v: string) => !!v || '请确认密码',
  (v: string) => v === form_data.password || '两次输入的密码不一致',
]

const terms_rules = [
  (v: boolean) => !!v || '请阅读并同意服务条款',
]

// 密码强度计算
const password_strength = computed(() => {
  const password = form_data.password
  let score = 0
  let text = '很弱'
  let color = 'error'

  if (password.length >= 8) score += 25
  if (/[a-z]/.test(password)) score += 25
  if (/[A-Z]/.test(password)) score += 25
  if (/\d/.test(password)) score += 25

  if (score >= 100) {
    text = '很强'
    color = 'success'
  } else if (score >= 75) {
    text = '中等'
    color = 'warning'
  } else if (score >= 50) {
    text = '较弱'
    color = 'orange'
  }

  return { score, text, color }
})

// 注册处理
const handle_register = async () => {
  if (!form_valid.value) return
  
  loading.value = true
  error_message.value = ''
  success_message.value = ''
  
  try {
    const response = await auth_api.register({
      username: form_data.username,
      email: form_data.email,
      first_name: form_data.first_name,
      last_name: form_data.last_name,
      phone: form_data.phone,
      password: form_data.password,
      role: form_data.role,
    })
    
    success_message.value = '注册成功！3秒后自动跳转到登录页面'
    
    setTimeout(() => {
      router.push('/auth/login')
    }, 3000)
    
  } catch (error: any) {
    if (error.message.includes('Network Error') || error.code === 'ERR_NETWORK') {
      error_message.value = '无法连接到服务器，请检查网络连接'
    } else if (error.status === 409) {
      error_message.value = '用户名或邮箱已存在，请使用其他用户名或邮箱'
    } else {
      error_message.value = error.message || '注册失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.logo-icon {
  font-size: 72px;
  line-height: 1;
}

.register-form {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  padding: 2rem;
}

/* 响应式设计 */
@media (max-width: 600px) {
  .register-form {
    max-width: 400px;
    padding: 1rem;
  }
}
</style>