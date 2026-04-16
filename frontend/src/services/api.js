import request from '@/utils/request'

// ==================== 新闻模块 ====================

// 获取新闻分类
export function getCategories() {
  return request({
    url: '/news/categories',
    method: 'get'
  })
}

// 获取新闻列表
export function getNewsList({ categoryId, page = 1, pageSize = 10 }) {
  return request({
    url: '/news/list',
    method: 'get',
    params: { categoryId, page, pageSize }
  })
}

// 获取新闻详情
export function getNewsDetail(id) {
  return request({
    url: '/news/detail',
    method: 'get',
    params: { id }
  })
}

// ==================== 用户模块 ====================

// 用户注册
export function register({ username, password }) {
  return request({
    url: '/users/register',
    method: 'post',
    data: { username, password }
  })
}

// 用户登录
export function login({ username, password }) {
  return request({
    url: '/users/login',
    method: 'post',
    data: { username, password }
  })
}

// 获取用户信息
export function getUserInfo() {
  return request({
    url: '/users/info',
    method: 'get'
  })
}

// 更新用户信息
export function updateUser(data) {
  return request({
    url: '/users/update',
    method: 'put',
    data
  })
}

// 修改密码
export function changePassword({ oldPassword, newPassword }) {
  return request({
    url: '/users/password',
    method: 'put',
    data: { oldPassword, newPassword }
  })
}

// ==================== 收藏模块 ====================

// 检查收藏状态
export function checkFavorite(newsId) {
  return request({
    url: '/favorite/check',
    method: 'post',
    params: { news_id: newsId }
  })
}

// 添加收藏
export function addFavorite(newsId) {
  return request({
    url: '/favorite/add',
    method: 'post',
    data: { news_id: newsId }
  })
}

// 取消收藏
export function removeFavorite(newsId) {
  return request({
    url: '/favorite/remove',
    method: 'post',
    params: { news_id: newsId }
  })
}

// 获取收藏列表
export function getFavoriteList({ page = 1, pageSize = 10 }) {
  return request({
    url: '/favorite/list',
    method: 'get',
    params: { page, pageSize }
  })
}

// 清空收藏
export function clearFavorite() {
  return request({
    url: '/favorite/clear',
    method: 'get'
  })
}

// ==================== 历史记录模块 ====================

// 添加历史记录
export function addHistory(newsId) {
  return request({
    url: '/history/add',
    method: 'post',
    data: { news_id: newsId }
  })
}

// 获取历史记录列表
export function getHistoryList({ page = 1, pageSize = 10 }) {
  return request({
    url: '/history/list',
    method: 'get',
    params: { page, pageSize }
  })
}

// 删除单条历史记录
export function deleteHistory(historyId) {
  return request({
    url: `/history/delete/${historyId}`,
    method: 'delete'
  })
}

// 清空历史记录
export function clearHistory() {
  return request({
    url: '/history/clear',
    method: 'delete'
  })
}
