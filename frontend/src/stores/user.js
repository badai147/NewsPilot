import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getUserInfo, login as apiLogin, register as apiRegister, updateUser as apiUpdateUser, changePassword as apiChangePassword } from '@/services/api'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)
  const isLoading = ref(false)

  const isLoggedIn = computed(() => !!token.value)

  async function login(credentials) {
    isLoading.value = true
    try {
      const res = await apiLogin(credentials)
      token.value = res.data.token
      userInfo.value = res.data.userInfo
      localStorage.setItem('token', res.data.token)
      return res
    } finally {
      isLoading.value = false
    }
  }

  async function register(credentials) {
    isLoading.value = true
    try {
      const res = await apiRegister(credentials)
      token.value = res.data.token
      userInfo.value = res.data.userInfo
      localStorage.setItem('token', res.data.token)
      return res
    } finally {
      isLoading.value = false
    }
  }

  async function fetchUserInfo() {
    if (!token.value) return
    isLoading.value = true
    try {
      const res = await getUserInfo()
      userInfo.value = res.data
      return res
    } catch (error) {
      logout()
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function updateUser(data) {
    const res = await apiUpdateUser(data)
    userInfo.value = res.data
    return res
  }

  async function changePassword(passwords) {
    return await apiChangePassword(passwords)
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  return {
    token,
    userInfo,
    isLoading,
    isLoggedIn,
    login,
    register,
    fetchUserInfo,
    updateUser,
    changePassword,
    logout
  }
})
