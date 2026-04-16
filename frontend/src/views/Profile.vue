<template>
  <div class="profile-page">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="container header-content">
        <router-link to="/home" class="back-btn">
          <span class="back-icon">&lt;</span> 返回
        </router-link>
        <h1 class="logo">新闻头条</h1>
        <div class="placeholder"></div>
      </div>
    </header>

    <main class="main">
      <div class="container">
        <div class="profile-card">
          <div class="profile-header">
            <div class="avatar">
              <img v-if="userInfo?.avatar" :src="userInfo.avatar" alt="头像" />
              <span v-else class="avatar-placeholder">{{ userInfo?.username?.[0]?.toUpperCase() || 'U' }}</span>
            </div>
            <div class="user-info">
              <h2 class="username">{{ userInfo?.username }}</h2>
              <p class="bio" v-if="userInfo?.bio">{{ userInfo.bio }}</p>
              <p class="bio" v-else>这个人很懒，什么都没写</p>
            </div>
          </div>
          
          <div class="quick-nav">
            <router-link to="/favorites" class="nav-item">
              <span class="nav-icon">★</span>
              <span>我的收藏</span>
            </router-link>
            <router-link to="/history" class="nav-item">
              <span class="nav-icon">⏱</span>
              <span>浏览历史</span>
            </router-link>
          </div>
        </div>

        <!-- 编辑个人资料 -->
        <div class="section">
          <h3 class="section-title">编辑资料</h3>
          <div class="form-card">
            <form @submit.prevent="handleUpdateProfile">
              <div class="form-item">
                <label>昵称</label>
                <input 
                  v-model="profileForm.nickname" 
                  type="text" 
                  placeholder="请输入昵称"
                />
              </div>
              
              <div class="form-item">
                <label>头像 URL</label>
                <input 
                  v-model="profileForm.avatar" 
                  type="text" 
                  placeholder="请输入头像图片地址"
                />
              </div>
              
              <div class="form-item">
                <label>性别</label>
                <select v-model="profileForm.gender">
                  <option value="">未选择</option>
                  <option value="male">男</option>
                  <option value="female">女</option>
                  <option value="other">其他</option>
                </select>
              </div>
              
              <div class="form-item">
                <label>个人简介</label>
                <textarea 
                  v-model="profileForm.bio" 
                  rows="3"
                  placeholder="请输入个人简介"
                ></textarea>
              </div>
              
              <div class="form-actions">
                <button type="submit" class="btn btn-primary" :disabled="updating">
                  {{ updating ? '保存中...' : '保存修改' }}
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- 修改密码 -->
        <div class="section">
          <h3 class="section-title">修改密码</h3>
          <div class="form-card">
            <form @submit.prevent="handleChangePassword">
              <div class="form-item">
                <label>旧密码</label>
                <input 
                  v-model="passwordForm.oldPassword" 
                  type="password" 
                  placeholder="请输入旧密码"
                  required
                />
              </div>
              
              <div class="form-item">
                <label>新密码</label>
                <input 
                  v-model="passwordForm.newPassword" 
                  type="password" 
                  placeholder="请输入新密码（至少6位）"
                  required
                  minlength="6"
                />
              </div>
              
              <div class="form-item">
                <label>确认新密码</label>
                <input 
                  v-model="passwordForm.confirmPassword" 
                  type="password" 
                  placeholder="请再次输入新密码"
                  required
                />
              </div>
              
              <div v-if="passwordError" class="error-msg">{{ passwordError }}</div>
              
              <div class="form-actions">
                <button type="submit" class="btn btn-primary" :disabled="changingPassword">
                  {{ changingPassword ? '修改中...' : '修改密码' }}
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- 退出登录 -->
        <div class="section">
          <button class="btn btn-danger btn-block" @click="handleLogout">
            退出登录
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const profileForm = reactive({
  nickname: '',
  avatar: '',
  gender: '',
  bio: ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const updating = ref(false)
const changingPassword = ref(false)
const passwordError = ref('')

const userInfo = computed(() => userStore.userInfo)

function initProfileForm() {
  if (userInfo.value) {
    profileForm.nickname = userInfo.value.nickname || ''
    profileForm.avatar = userInfo.value.avatar || ''
    profileForm.gender = userInfo.value.gender || ''
    profileForm.bio = userInfo.value.bio || ''
  }
}

async function handleUpdateProfile() {
  updating.value = true
  try {
    await userStore.updateUser({
      nickname: profileForm.nickname || undefined,
      avatar: profileForm.avatar || undefined,
      gender: profileForm.gender || undefined,
      bio: profileForm.bio || undefined
    })
    alert('资料更新成功')
  } catch (error) {
    alert(error.message || '更新失败')
  } finally {
    updating.value = false
  }
}

async function handleChangePassword() {
  passwordError.value = ''
  
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordError.value = '两次输入的新密码不一致'
    return
  }
  
  if (passwordForm.newPassword.length < 6) {
    passwordError.value = '新密码至少需要6位'
    return
  }
  
  changingPassword.value = true
  try {
    await userStore.changePassword({
      oldPassword: passwordForm.oldPassword,
      newPassword: passwordForm.newPassword
    })
    alert('密码修改成功')
    passwordForm.oldPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
  } catch (error) {
    passwordError.value = error.message || '修改密码失败'
  } finally {
    changingPassword.value = false
  }
}

function handleLogout() {
  if (!confirm('确定要退出登录吗？')) return
  userStore.logout()
  router.push('/login')
}

onMounted(async () => {
  await userStore.fetchUserInfo()
  initProfileForm()
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
  font-size: 14px;
  min-width: 80px;
}

.back-btn:hover {
  color: #1890ff;
}

.back-icon {
  font-size: 18px;
}

.logo {
  font-size: 24px;
  color: #1890ff;
  font-weight: bold;
}

.placeholder {
  min-width: 80px;
}

.main {
  padding: 20px 0;
}

.profile-card {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 20px;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  background: #1890ff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 32px;
  color: #fff;
  font-weight: bold;
}

.username {
  font-size: 20px;
  color: #333;
  margin-bottom: 4px;
}

.bio {
  font-size: 14px;
  color: #999;
}

.quick-nav {
  display: flex;
  gap: 20px;
  border-top: 1px solid #f0f0f0;
  padding-top: 16px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #f5f5f5;
  border-radius: 20px;
  font-size: 14px;
  color: #666;
  transition: all 0.3s;
}

.nav-item:hover {
  background: #e6f7ff;
  color: #1890ff;
}

.nav-icon {
  font-size: 16px;
}

.section {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.section-title {
  font-size: 16px;
  color: #333;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.form-card {
  max-width: 500px;
}

.form-item {
  margin-bottom: 20px;
}

.form-item label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #666;
}

.form-item input,
.form-item select,
.form-item textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-item input:focus,
.form-item select:focus,
.form-item textarea:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.form-actions {
  margin-top: 20px;
}

.btn-block {
  width: 100%;
  padding: 12px;
  font-size: 16px;
}

.btn-danger {
  background-color: #fff;
  border: 1px solid #ff4d4f;
  color: #ff4d4f;
}

.btn-danger:hover {
  background-color: #ff4d4f;
  color: #fff;
}

.error-msg {
  color: #f5222d;
  font-size: 14px;
  margin-bottom: 16px;
}
</style>
