<template>
  <div class="detail-page">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="container header-content">
        <router-link to="/home" class="back-btn">
          <span class="back-icon">&lt;</span> 返回
        </router-link>
        <h1 class="logo">新闻头条</h1>
        <div class="user-area">
          <router-link v-if="!isLoggedIn" to="/login" class="nav-link">登录</router-link>
          <router-link v-else to="/profile" class="nav-link">{{ userInfo?.username }}</router-link>
        </div>
      </div>
    </header>

    <!-- AI 助手悬浮按钮 -->
    <div class="ai-float-btn" @click="openAiChat" title="AI 智能总结">
      <span class="ai-icon">🤖</span>
      <span class="ai-text">AI总结</span>
    </div>

    <!-- AI 聊天弹窗 -->
    <AiChat
      v-model:visible="aiChatVisible"
      :newsId="newsDetail?.id"
      :newsTitle="newsDetail?.title"
      :newsContent="newsDetail?.content"
    />

    <main class="main" v-loading="loading">
      <div class="container">
        <div v-if="!loading && !newsDetail" class="empty">
          新闻不存在或已被删除
        </div>
        
        <article v-if="newsDetail" class="article">
          <h1 class="article-title">{{ newsDetail.title }}</h1>
          
          <div class="article-meta">
            <span class="author" v-if="newsDetail.author">{{ newsDetail.author }}</span>
            <span class="time">{{ formatTime(newsDetail.publishTime) }}</span>
            <span class="views">{{ newsDetail.views || 0 }} 阅读</span>
          </div>
          
          <div v-if="newsDetail.image" class="article-image">
            <img :src="newsDetail.image" :alt="newsDetail.title" />
          </div>
          
          <div class="article-content" v-html="newsDetail.content"></div>
          
          <div class="article-actions">
            <button 
              class="action-btn" 
              :class="{ active: isFavorited }"
              @click="toggleFavorite"
            >
              {{ isFavorited ? '已收藏' : '收藏' }}
            </button>
            <router-link to="/home" class="action-btn">返回首页</router-link>
          </div>
        </article>

        <!-- 相关推荐 -->
        <section v-if="relatedNews.length > 0" class="related-section">
          <h3 class="section-title">相关推荐</h3>
          <div class="related-list">
            <div 
              v-for="item in relatedNews" 
              :key="item.id" 
              class="related-item"
              @click="goToDetail(item.id)"
            >
              <div class="related-image" v-if="item.image">
                <img :src="item.image" :alt="item.title" />
              </div>
              <div class="related-content">
                <h4 class="related-title">{{ item.title }}</h4>
                <span class="related-time">{{ formatTime(item.publish_time) }}</span>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getNewsDetail, checkFavorite, addFavorite, removeFavorite, addHistory } from '@/services/api'
import dayjs from 'dayjs'
import AiChat from './AiChat.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const newsDetail = ref(null)
const relatedNews = ref([])
const isFavorited = ref(false)
const aiChatVisible = ref(false)

const isLoggedIn = computed(() => userStore.isLoggedIn)
const userInfo = computed(() => userStore.userInfo)

function formatTime(time) {
  if (!time) return ''
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}

async function fetchDetail() {
  loading.value = true
  const newsId = route.params.id
  
  try {
    const res = await getNewsDetail(newsId)
    newsDetail.value = res.data
    relatedNews.value = res.data.relatedNews || []
    
    // 记录浏览历史
    if (isLoggedIn.value) {
      try {
        await addHistory(newsId)
      } catch (e) {
        console.error('记录历史失败:', e)
      }
    }
    
    // 检查收藏状态
    if (isLoggedIn.value) {
      checkFavoriteStatus(newsId)
    }
  } catch (error) {
    console.error('获取新闻详情失败:', error)
  } finally {
    loading.value = false
  }
}

async function checkFavoriteStatus(newsId) {
  try {
    const res = await checkFavorite(newsId)
    isFavorited.value = res.data?.isFavorite || false
  } catch (e) {
    console.error('检查收藏状态失败:', e)
  }
}

async function toggleFavorite() {
  if (!isLoggedIn.value) {
    router.push('/login')
    return
  }
  
  const newsId = newsDetail.value.id
  
  try {
    if (isFavorited.value) {
      await removeFavorite(newsId)
      isFavorited.value = false
    } else {
      await addFavorite(newsId)
      isFavorited.value = true
    }
  } catch (error) {
    console.error('操作收藏失败:', error)
  }
}

function goToDetail(id) {
  router.push(`/news/${id}`)
  window.scrollTo(0, 0)
}

function openAiChat() {
  aiChatVisible.value = true
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped>
.detail-page {
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

.user-area {
  min-width: 100px;
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

.article {
  background: #fff;
  border-radius: 8px;
  padding: 30px;
  margin-bottom: 20px;
}

.article-title {
  font-size: 28px;
  color: #333;
  line-height: 1.4;
  margin-bottom: 16px;
}

.article-meta {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #999;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.article-image {
  margin-bottom: 24px;
  border-radius: 8px;
  overflow: hidden;
}

.article-image img {
  width: 100%;
  max-height: 500px;
  object-fit: cover;
}

.article-content {
  font-size: 16px;
  line-height: 1.8;
  color: #333;
  white-space: pre-wrap;
}

.article-content :deep(p) {
  margin-bottom: 16px;
}

.article-actions {
  display: flex;
  gap: 16px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.action-btn {
  padding: 10px 24px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  color: #666;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.action-btn.active {
  background: #fff1f0;
  border-color: #ff4d4f;
  color: #ff4d4f;
}

.related-section {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.section-title {
  font-size: 18px;
  color: #333;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #1890ff;
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.related-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

.related-item:hover {
  background: #f5f5f5;
}

.related-image {
  width: 100px;
  height: 70px;
  flex-shrink: 0;
  border-radius: 4px;
  overflow: hidden;
}

.related-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.related-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.related-title {
  font-size: 15px;
  color: #333;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.related-time {
  font-size: 13px;
  color: #999;
}

.empty {
  text-align: center;
  padding: 60px;
  background: #fff;
  border-radius: 8px;
  color: #999;
}

/* AI 悬浮按钮 */
.ai-float-btn {
  position: fixed;
  right: 30px;
  bottom: 100px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  padding: 14px 20px;
  border-radius: 30px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  transition: all 0.3s;
  z-index: 100;
  font-weight: 600;
}

.ai-float-btn:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.5);
}

.ai-float-btn .ai-icon {
  font-size: 20px;
}

.ai-float-btn .ai-text {
  font-size: 15px;
}
</style>
