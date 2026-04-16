<template>
  <div class="register-page">
    <div class="register-box">
      <h1 class="title">新闻头条</h1>
      <div class="subtitle">创建新账户</div>
      
      <form @submit.prevent="handleRegister" class="form">
        <div class="form-item">
          <label>用户名</label>
          <input 
            v-model="formData.username" 
            type="text" 
            placeholder="请输入用户名（至少3个字符）"
            required
            minlength="3"
          />
        </div>
        
        <div class="form-item">
          <label>密码</label>
          <input 
            v-model="formData.password" 
            type="password" 
            placeholder="请输入密码（至少6个字符）"
            required
            minlength="6"
          />
        </div>
        
        <div class="form-item">
          <label>确认密码</label>
          <input 
            v-model="formData.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
            required
          />
        </div>
        
        <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>
        
        <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      
      <div class="footer">
        已有账号？<router-link to="/login">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const formData = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const loading = ref(false)
const errorMsg = ref('')

async function handleRegister() {
  errorMsg.value = ''
  
  if (formData.password !== formData.confirmPassword) {
    errorMsg.value = '两次输入的密码不一致'
    return
  }
  
  if (formData.username.length < 3) {
    errorMsg.value = '用户名至少需要3个字符'
    return
  }
  
  if (formData.password.length < 6) {
    errorMsg.value = '密码至少需要6个字符'
    return
  }
  
  loading.value = true
  
  try {
    await userStore.register({
      username: formData.username,
      password: formData.password
    })
    router.push('/home')
  } catch (error) {
    errorMsg.value = error.message || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-box {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.title {
  text-align: center;
  font-size: 28px;
  color: #333;
  margin-bottom: 8px;
}

.subtitle {
  text-align: center;
  color: #999;
  margin-bottom: 30px;
}

.form-item {
  margin-bottom: 20px;
}

.form-item label {
  display: block;
  margin-bottom: 8px;
  color: #666;
  font-size: 14px;
}

.form-item input {
  width: 100%;
  padding: 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-item input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.btn-block {
  width: 100%;
  padding: 12px;
  font-size: 16px;
}

.error-msg {
  color: #f5222d;
  font-size: 14px;
  margin-bottom: 16px;
  text-align: center;
}

.footer {
  text-align: center;
  margin-top: 20px;
  color: #666;
  font-size: 14px;
}

.footer a {
  color: #667eea;
  font-weight: 500;
}

.footer a:hover {
  text-decoration: underline;
}
</style>
