<!--
  密码修改页面 - 已登录用户使用
-->
<template>
  <div class="change-password-container">
    <v-container class="pa-4">
      <v-row justify="center">
        <v-col cols="12" sm="8" md="6" lg="5">
          <v-card class="pa-6" elevation="2" rounded="lg">
            <!-- 页面标题 -->
            <div class="text-center mb-6">
              <div class="password-icon mb-4">
                <v-icon size="72" color="primary">mdi-lock-reset</v-icon>
              </div>
              <h1 class="text-h4 font-weight-bold mb-2">
                修改密码
              </h1>
              <p class="text-subtitle-1 text-medium-emphasis">
                为了您的账户安全，请定期更换密码
              </p>
            </div>

            <v-form
              ref="form_ref"
              v-model="form_valid"
              @submit.prevent="change_password"
            >
              <!-- 当前密码 -->
              <v-text-field
                v-model="form_data.current_password"
                :rules="current_password_rules"
                :type="show_current_password ? 'text' : 'password'"
                label="当前密码"
                prepend-inner-icon="mdi-lock"
                :append-inner-icon="show_current_password ? 'mdi-eye' : 'mdi-eye-off'"
                variant="outlined"
                :disabled="loading"
                autocomplete="current-password"
                class="mb-4"
                @click:append-inner="show_current_password = !show_current_password"
              />

              <!-- 新密码 -->
              <v-text-field
                v-model="form_data.new_password"
                :rules="new_password_rules"
                :type="show_new_password ? 'text' : 'password'"
                label="新密码"
                prepend-inner-icon="mdi-lock-plus"
                :append-inner-icon="show_new_password ? 'mdi-eye' : 'mdi-eye-off'"
                variant="outlined"
                :disabled="loading"
                autocomplete="new-password"
                class="mb-4"
                @click:append-inner="show_new_password = !show_new_password"
              />

              <!-- 确认新密码 -->
              <v-text-field
                v-model="form_data.confirm_password"
                :rules="confirm_password_rules"
                :type="show_confirm_password ? 'text' : 'password'"
                label="确认新密码"
                prepend-inner-icon="mdi-lock-plus"
                :append-inner-icon="show_confirm_password ? 'mdi-eye' : 'mdi-eye-off'"
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

              <!-- 密码要求提示 -->
              <v-alert
                type="info"
                variant="outlined"
                density="compact"
                class="mb-4"
              >
                <div class="text-caption">
                  <strong>密码要求：</strong>
                  <ul class="ml-4 mt-1">
                    <li>至少8个字符</li>
                    <li>包含大写字母</li>
                    <li>包含小写字母</li>
                    <li>包含数字</li>
                  </ul>
                </div>
              </v-alert>

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

              <!-- 修改密码按钮 -->
              <v-btn
                :loading="loading"
                :disabled="!form_valid || loading || password_strength.score < 75"
                type="submit"
                color="primary"
                size="large"
                block
                class="mb-4"
              >
                <v-icon class="mr-2">mdi-lock-reset</v-icon>
                {{ loading ? '修改中...' : '修改密码' }}
              </v-btn>

              <!-- 取消按钮 -->
              <div class="text-center">
                <v-btn
                  variant="text"
                  color="primary"
                  size="small"
                  @click="$router.back()"
                >
                  取消
                </v-btn>
              </div>
            </v-form>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { auth_api } from '../../api'

const router = useRouter()
const auth_store = useAuthStore()

// 表单引用和验证状态
const form_ref = ref()
const form_valid = ref(false)
const loading = ref(false)
const show_current_password = ref(false)
const show_new_password = ref(false)
const show_confirm_password = ref(false)
const error_message = ref('')
const success_message = ref('')

// 表单数据
const form_data = reactive({
  current_password: '',
  new_password: '',
  confirm_password: '',
})

// 验证规则
const current_password_rules = [
  (v: string) => !!v || '请输入当前密码',
]

const new_password_rules = [
  (v: string) => !!v || '请输入新密码',
  (v: string) => v.length >= 8 || '密码至少8个字符',
  (v: string) => /[A-Z]/.test(v) || '密码必须包含大写字母',
  (v: string) => /[a-z]/.test(v) || '密码必须包含小写字母',
  (v: string) => /\d/.test(v) || '密码必须包含数字',
  (v: string) => v !== form_data.current_password || '新密码不能与当前密码相同',
]

const confirm_password_rules = [
  (v: string) => !!v || '请确认新密码',
  (v: string) => v === form_data.new_password || '两次输入的密码不一致',
]

// 密码强度计算
const password_strength = computed(() => {
  const password = form_data.new_password
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

// 修改密码
const change_password = async () => {
  if (!form_valid.value) return

  loading.value = true
  error_message.value = ''
  success_message.value = ''

  try {
    await auth_api.change_password({
      current_password: form_data.current_password,
      new_password: form_data.new_password,
    })

    success_message.value = '密码修改成功！'
    
    // 清空表单
    form_data.current_password = ''
    form_data.new_password = ''
    form_data.confirm_password = ''
    
    // 3秒后返回
    setTimeout(() => {
      router.back()
    }, 3000)
    
  } catch (error: any) {
    if (error.message.includes('Network Error') || error.code === 'ERR_NETWORK') {
      error_message.value = '无法连接到服务器，请检查网络连接'
    } else if (error.status === 400) {
      error_message.value = '当前密码错误，请重新输入'
    } else {
      error_message.value = error.message || '密码修改失败'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.password-icon {
  font-size: 72px;
  line-height: 1;
}

.change-password-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #151931 0%, #252841 100%);
  display: flex;
  align-items: center;
}

/* 统一配色方案 */
:deep(.v-card) {
  backdrop-filter: blur(16px);
  background: linear-gradient(135deg, rgba(37, 40, 65, 0.8), rgba(61, 63, 91, 0.6));
  border: 1px solid rgba(231, 209, 187, 0.15);
  transition: all 300ms ease;
  color: #A096A2;
  box-shadow: 0 8px 32px rgba(21, 25, 49, 0.3);
}

/* 主标题样式优化 */
h1 {
  background: linear-gradient(135deg, #E7D1BB 0%, #A096A5 50%, #c8b39e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 2px 8px rgba(231, 209, 187, 0.2);
}

/* 按钮优化 */
:deep(.v-btn) {
  border-radius: 12px;
  font-weight: 500;
  letter-spacing: 0.3px;
  transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.v-btn--variant-outlined) {
  border: 2px solid;
}

:deep(.v-btn:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(231, 209, 187, 0.3);
}

/* 响应式设计 */
@media (max-width: 600px) {
  .change-password-container .v-container {
    padding: 1rem;
  }
}
</style>