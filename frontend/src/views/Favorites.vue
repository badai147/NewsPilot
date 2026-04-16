<template>
  <div class="favorites-page">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="container header-content">
        <router-link to="/home" class="back-btn">
          <span class="back-icon">&lt;</span> 返回
        </router-link>
        <h1 class="logo">新闻头条</h1>
        <div class="user-area">
          <router-link to="/profile" class="nav-link">{{ userInfo?.username }}</router-link>
        </div>
      </div>
    </header>

    <main class="main">
      <div class="container">
        <div class="page-header">
          <h2 class="page-title">我的收藏</h2>
          <button 
            v-if="favoriteList.length > 0" 
            class="btn btn-default"
            @click="handleClearAll"
          >
            清空全部
          </button>
        </div>

        <div v-loading="loading" class="content">
          <div v-if="!loading && favoriteList.length === 0" class="empty">
            <p>暂无收藏内容</p>
            <router-link to="/home" class="btn btn-primary">去首页看看</router-link>
          </div>

          <div 
            v-for="item in favoriteList" 
            :key="item.favoriteId" 
            class="news-item"
            @click="goToDetail(item.id)"
          >
            <div class="news-image" v-if="item.image">
              <img :src="item.image" :alt="item.title" />
            </div>
            <div class="news-content">
              <h3 class="news-title">{{ item.title }}</h3>
              <div class="news-meta">
                <span class="author" v-if="item.author">{{ item.author }}</span>
                <span class="time">收藏于 {{ formatTime(item.favoriteTime) }}</span>
              </div>
            </div>
            <button 
              class="remove-btn" 
              @click.stop="handleRemove(item.favoriteId)"
              title="取消收藏"
            >
              &times;
            </button>
          </div>
        </div>

        <!-- 分页 -->
        <div class="pagination" v-if="total > pageSize">
          <button 
            :disabled="page === 1" 
            @click="changePage(page - 1)"
          >
            上一页
          </button>
          <span class="page-info">{{ page }} / {{ totalPages }}</span>
          <button 
            :disabled="page >= totalPages" 
            @click="changePage(page + 1)"
          >
            下一页
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getFavoriteList, removeFavorite, clearFavorite } from '@/services/api'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const favoriteList = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const userInfo = computed(() => userStore.userInfo)
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

function formatTime(time) {
  if (!time) return ''
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}

async function fetchFavorites() {
  loading.value = true
  try {
    const res = await getFavoriteList({ page: page.value, pageSize: pageSize.value })
    favoriteList.value = res.data?.list || []
    total.value = res.data?.total || 0
  } catch (error) {
    console.error('获取收藏列表失败:', error)
  } finally {
    loading.value = false
  }
}

async function handleRemove(favoriteId) {
  try {
    const newsId = favoriteList.value.find(f => f.favoriteId === favoriteId)?.news_id || favoriteList.value.find(f => f.favoriteId === favoriteId)?.id
    await removeFavorite(newsId || favoriteId)
    await fetchFavorites()
  } catch (error) {
    console.error('取消收藏失败:', error)
  }
}

async function handleClearAll() {
  if (!confirm('确定要清空所有收藏吗？')) return
  
  try {
    await clearFavorite()
    favoriteList.value = []
    total.value = 0
  } catch (error) {
    console.error('清空收藏失败:', error)
  }
}

function changePage(newPage) {
  page.value = newPage
  fetchFavorites()
  window.scrollTo(0, 0)
}

function goToDetail(id) {
  router.push(`/news/${id}`)
}

onMounted(async () => {
  if (userStore.isLoggedIn) {
    await userStore.fetchUserInfo()
  }
  fetchFavorites()
})
</script>

<style scoped>
.favorites-page {
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

.nav-link {
  color: #666;
  font-size: 14px;
}

.nav-link:hover {
  color: #1890ff;
}

.main {
  padding: 20px 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 22px;
  color: #333;
}

.content {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  min-height: 300px;
}

.news-item {
  display: flex;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  position: relative;
  transition: background 0.3s;
}

.news-item:last-child {
  border-bottom: none;
}

.news-item:hover {
  background: #fafafa;
}

.news-image {
  width: 120px;
  height: 90px;
  flex-shrink: 0;
  margin-right: 16px;
  border-radius: 6px;
  overflow: hidden;
}

.news-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.news-content {
  flex: 1;
}

.news-title {
  font-size: 16px;
  color: #333;
  margin-bottom: 8px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #999;
}

.remove-btn {
  position: absolute;
  right: 16px;
  top: 16px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #f5f5f5;
  color: #999;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}

.remove-btn:hover {
  background: #ff4d4f;
  color: #fff;
}

.empty {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.empty p {
  margin-bottom: 20px;
  font-size: 16px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-top: 20px;
}

.pagination button {
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s;
}

.pagination button:hover:not(:disabled) {
  border-color: #1890ff;
  color: #1890ff;
}

.pagination button:disabled {
  cursor: not-allowed;
  color: #d9d9d9;
}

.page-info {
  font-size: 14px;
  color: #666;
}
</style>
