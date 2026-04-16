<template>
  <div class="home-page">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="container header-content">
        <h1 class="logo">新闻头条</h1>
        <nav class="nav">
          <router-link to="/home" class="nav-item active">首页</router-link>
          <router-link v-if="isLoggedIn" to="/favorites" class="nav-item">收藏</router-link>
          <router-link v-if="isLoggedIn" to="/history" class="nav-item">历史</router-link>
          <router-link v-if="isLoggedIn" to="/profile" class="nav-item">个人中心</router-link>
          <router-link v-if="!isLoggedIn" to="/login" class="nav-item">登录</router-link>
          <a v-if="isLoggedIn" @click="handleLogout" class="nav-item logout">退出</a>
        </nav>
      </div>
    </header>

    <main class="main">
      <div class="container">
        <!-- 分类导航 -->
        <div class="category-bar">
          <button 
            v-for="cat in categories" 
            :key="cat.id"
            :class="['category-btn', { active: currentCategory === cat.id }]"
            @click="selectCategory(cat.id)"
          >
            {{ cat.name }}
          </button>
        </div>

        <!-- 新闻列表 -->
        <div class="news-list" v-loading="loading">
          <div v-if="!loading && newsList.length === 0" class="empty">
            暂无新闻
          </div>
          
          <div 
            v-for="news in newsList" 
            :key="news.id" 
            class="news-item"
            @click="goToDetail(news.id)"
          >
            <div class="news-image" v-if="news.image">
              <img :src="news.image" :alt="news.title" />
            </div>
            <div class="news-content">
              <h3 class="news-title">{{ news.title }}</h3>
              <p class="news-desc" v-if="news.description">{{ news.description }}</p>
              <div class="news-meta">
                <span class="author" v-if="news.author">{{ news.author }}</span>
                <span class="time">{{ formatTime(news.publish_time) }}</span>
                <span class="views">{{ news.views || 0 }} 阅读</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 加载更多 -->
        <div class="load-more" v-if="hasMore && !loading">
          <button class="btn btn-default" @click="loadMore">加载更多</button>
        </div>
        
        <div class="loading" v-if="loadingMore">
          加载中...
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getCategories, getNewsList } from '@/services/api'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()

const categories = ref([])
const currentCategory = ref(null)
const newsList = ref([])
const loading = ref(false)
const loadingMore = ref(false)
const page = ref(1)
const pageSize = ref(10)
const hasMore = ref(false)

const isLoggedIn = computed(() => userStore.isLoggedIn)

function formatTime(time) {
  if (!time) return ''
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}

async function fetchCategories() {
  try {
    const res = await getCategories()
    categories.value = res.data || []
    if (categories.value.length > 0) {
      currentCategory.value = categories.value[0].id
    }
  } catch (error) {
    console.error('获取分类失败:', error)
  }
}

async function fetchNewsList(reset = false) {
  if (!currentCategory.value) return
  
  if (reset) {
    page.value = 1
    newsList.value = []
    loading.value = true
  } else {
    loadingMore.value = true
  }
  
  try {
    const res = await getNewsList({
      categoryId: currentCategory.value,
      page: page.value,
      pageSize: pageSize.value
    })
    
    const list = res.data.list || []
    if (reset) {
      newsList.value = list
    } else {
      newsList.value = [...newsList.value, ...list]
    }
    hasMore.value = res.data.hasMore
  } catch (error) {
    console.error('获取新闻列表失败:', error)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

function selectCategory(categoryId) {
  if (currentCategory.value === categoryId) return
  currentCategory.value = categoryId
  fetchNewsList(true)
}

function loadMore() {
  page.value++
  fetchNewsList(false)
}

function goToDetail(id) {
  router.push(`/news/${id}`)
}

async function handleLogout() {
  userStore.logout()
  router.push('/login')
}

onMounted(async () => {
  await fetchCategories()
  if (currentCategory.value) {
    fetchNewsList(true)
  }
})
</script>

<style scoped>
.home-page {
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

.logo {
  font-size: 24px;
  color: #1890ff;
  font-weight: bold;
}

.nav {
  display: flex;
  gap: 24px;
}

.nav-item {
  color: #666;
  font-size: 15px;
  transition: color 0.3s;
  cursor: pointer;
}

.nav-item:hover,
.nav-item.active {
  color: #1890ff;
}

.logout {
  color: #ff4d4f;
}

.main {
  padding: 20px 0;
}

.category-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  background: #fff;
  padding: 16px;
  border-radius: 8px;
}

.category-btn {
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 20px;
  font-size: 14px;
  color: #666;
  background: #fff;
  transition: all 0.3s;
}

.category-btn:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.category-btn.active {
  background: #1890ff;
  border-color: #1890ff;
  color: #fff;
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.news-item {
  display: flex;
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: box-shadow 0.3s;
}

.news-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.news-image {
  width: 160px;
  height: 120px;
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
  display: flex;
  flex-direction: column;
}

.news-title {
  font-size: 18px;
  color: #333;
  margin-bottom: 8px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-desc {
  font-size: 14px;
  color: #999;
  line-height: 1.6;
  flex: 1;
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
  margin-top: 8px;
}

.load-more {
  text-align: center;
  margin-top: 20px;
}

.loading,
.empty {
  text-align: center;
  padding: 40px;
  color: #999;
}
</style>
