<template>
  <div class="ai-chat-overlay" v-if="visible" @click.self="close">
    <div class="ai-chat-dialog">
      <!-- 头部 -->
      <header class="chat-header">
        <div class="header-left">
          <span class="ai-icon">🤖</span>
          <h3>AI 新闻助手</h3>
          <span class="streaming-indicator" v-if="isStreaming">
            <span class="pulse"></span>
            AI 思考中...
          </span>
        </div>
        <button class="close-btn" @click="close">×</button>
      </header>

      <!-- 新闻信息 -->
      <div class="news-info" v-if="newsTitle">
        <span class="news-label">正在分析：</span>
        <span class="news-title">{{ newsTitle }}</span>
      </div>

      <!-- 消息区域 -->
      <div class="chat-messages" ref="messagesContainer">
        <!-- 欢迎消息 -->
        <div v-if="messages.length === 0 && !isLoading" class="welcome-message">
          <div class="welcome-icon">📰</div>
          <p>点击下方按钮，AI 将为您总结新闻要点</p>
          <button class="summarize-btn" @click="summarizeNews" :disabled="isLoading">
            <span v-if="isLoading" class="loading-spinner"></span>
            <span v-else>🚀 AI 总结</span>
          </button>
        </div>

        <!-- 消息列表 -->
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message', msg.role]"
        >
          <div class="message-avatar">
            {{ msg.role === 'user' ? '👤' : '🤖' }}
          </div>
          <div class="message-content">
            <div class="message-text" v-html="formatMessage(msg.content)"></div>
          </div>
        </div>

        <!-- 加载中 -->
        <div v-if="isLoading && currentStreamingText !== ''" class="message assistant">
          <div class="message-avatar">🤖</div>
          <div class="message-content">
            <div class="message-text streaming" v-html="formatMessage(currentStreamingText)"></div>
          </div>
        </div>

        <!-- 加载动画（打字指示器） -->
        <div v-if="isLoading && currentStreamingText === ''" class="message assistant">
          <div class="message-avatar">🤖</div>
          <div class="message-content">
            <div class="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 快捷问题 -->
      <div class="quick-questions" v-if="showQuickQuestions && !isLoading">
        <span class="quick-label">试试问：</span>
        <button
          v-for="q in quickQuestions"
          :key="q"
          class="quick-btn"
          @click="sendQuickQuestion(q)"
          :disabled="isLoading"
        >
          {{ q }}
        </button>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input-area">
        <textarea
          v-model="inputMessage"
          placeholder="输入您的问题..."
          rows="1"
          @keydown.enter.exact.prevent="sendMessage"
          @input="autoResize"
          ref="inputArea"
          :disabled="isLoading"
        ></textarea>
        <button class="send-btn" @click="sendMessage" :disabled="!inputMessage.trim() || isLoading">
          发送
        </button>
        <button class="clear-btn" @click="clearHistory" title="清除历史">
          🗑️
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  newsId: {
    type: Number,
    default: null
  },
  newsTitle: {
    type: String,
    default: ''
  },
  newsContent: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'update:visible'])

// 状态
const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)
const isStreaming = ref(false)
const currentStreamingText = ref('')
const sessionId = ref(generateSessionId())
const messagesContainer = ref(null)
const inputArea = ref(null)
const showQuickQuestions = ref(false)

// 快捷问题
const quickQuestions = [
  '总结一下主要内容',
  '这件事的背景是什么？',
  '有哪些关键人物？',
  '这会产生什么影响？'
]

// 生成会话ID
function generateSessionId() {
  return 'news_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
}

// 关闭弹窗
function close() {
  emit('close')
  emit('update:visible', false)
}

// 滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 自动调整输入框高度
function autoResize(e) {
  const textarea = e.target
  textarea.style.height = 'auto'
  textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
}

// 格式化消息（Markdown 简单转换）
function formatMessage(text) {
  if (!text) return ''

  return text
    // 代码块
    .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
    // 行内代码
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // 粗体
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // 斜体
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // 标题
    .replace(/^### (.+)$/gm, '<h4>$1</h4>')
    .replace(/^## (.+)$/gm, '<h3>$1</h3>')
    .replace(/^# (.+)$/gm, '<h2>$1</h2>')
    // 列表
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>')
    // 段落
    .replace(/\n\n/g, '</p><p>')
    // 换行
    .replace(/\n/g, '<br>')
    // 包装
    .replace(/^/, '<p>')
    .replace(/$/, '</p>')
}

// 处理 SSE 流式响应
function parseSSEMessage(data) {
  try {
    return JSON.parse(data)
  } catch {
    return null
  }
}

// 总结新闻（使用流式 API）
async function summarizeNews() {
  if (!props.newsId) return

  isLoading.value = true
  isStreaming.value = true
  messages.value = []
  showQuickQuestions.value = false
  currentStreamingText.value = ''

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: '请总结这篇新闻的主要内容'
  })

  // 添加空的消息占位（用于流式更新）
  const assistantMsgIndex = messages.value.length
  messages.value.push({
    role: 'assistant',
    content: ''
  })

  scrollToBottom()

  try {
    const response = await fetch('/api/ai/summarize/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        news_id: props.newsId,
        session_id: sessionId.value
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      // 处理 SSE 数据
      const lines = buffer.split('\n')
      buffer = lines.pop() // 保留未完成的行

      for (const line of lines) {
        if (line.startsWith('event:')) {
          const eventType = line.slice(6).trim()
          continue
        }

        if (line.startsWith('data:')) {
          const data = line.slice(5).trim()
          const parsed = parseSSEMessage(data)

          if (parsed) {
            if (parsed.type === 'token') {
              currentStreamingText.value += parsed.content
              messages.value[assistantMsgIndex].content = currentStreamingText.value
              scrollToBottom()
            } else if (parsed.type === 'end') {
              // 流式结束，更新最终内容
              messages.value[assistantMsgIndex].content = parsed.summary

              // 添加关键点
              if (parsed.key_points && parsed.key_points.length > 0) {
                messages.value[assistantMsgIndex].content +=
                  '\n\n**关键要点：**\n' +
                  parsed.key_points.map((p, i) => `${i + 1}. ${p}`).join('\n')
              }

              sessionId.value = parsed.session_id || sessionId.value
              showQuickQuestions.value = true
            } else if (parsed.type === 'error') {
              throw new Error(parsed.error)
            }
          }
        }
      }
    }

  } catch (error) {
    messages.value[assistantMsgIndex].content =
      `抱歉，总结失败：${error.message}\n\n请稍后重试。`
  } finally {
    isLoading.value = false
    isStreaming.value = false
    currentStreamingText.value = ''
    scrollToBottom()
  }
}

// 发送消息（使用流式 API）
async function sendMessage() {
  const text = inputMessage.value.trim()
  if (!text || isLoading.value) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: text
  })
  inputMessage.value = ''
  showQuickQuestions.value = false
  currentStreamingText.value = ''

  // 添加助手消息占位
  const assistantMsgIndex = messages.value.length
  messages.value.push({
    role: 'assistant',
    content: ''
  })

  scrollToBottom()
  isLoading.value = true
  isStreaming.value = true

  try {
    const response = await fetch('/api/ai/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: text,
        session_id: sessionId.value,
        news_id: props.newsId,
        news_summary: getLastSummary(),
        news_content: props.newsContent,
        news_title: props.newsTitle
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      const lines = buffer.split('\n')
      buffer = lines.pop()

      for (const line of lines) {
        if (line.startsWith('event:')) continue

        if (line.startsWith('data:')) {
          const data = line.slice(5).trim()
          const parsed = parseSSEMessage(data)

          if (parsed) {
            if (parsed.type === 'token') {
              currentStreamingText.value += parsed.content
              messages.value[assistantMsgIndex].content = currentStreamingText.value
              scrollToBottom()
            } else if (parsed.type === 'end') {
              messages.value[assistantMsgIndex].content = parsed.response
              showQuickQuestions.value = true
            } else if (parsed.type === 'error') {
              throw new Error(parsed.error)
            }
          }
        }
      }
    }

  } catch (error) {
    messages.value[assistantMsgIndex].content =
      `抱歉，发生了错误：${error.message}\n\n请稍后重试。`
  } finally {
    isLoading.value = false
    isStreaming.value = false
    currentStreamingText.value = ''
    scrollToBottom()
  }
}

// 发送快捷问题
function sendQuickQuestion(question) {
  inputMessage.value = question
  sendMessage()
}

// 获取最后一条总结
function getLastSummary() {
  const summaries = messages.value.filter(m => m.role === 'assistant')
  return summaries.length > 0 ? summaries[summaries.length - 1].content : ''
}

// 清除历史
async function clearHistory() {
  if (!confirm('确定要清除对话历史吗？')) return

  try {
    await fetch('/api/ai/history/clear', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        session_id: sessionId.value
      })
    })
  } catch (e) {
    console.error('清除历史失败:', e)
  }

  messages.value = []
  showQuickQuestions.value = false
  sessionId.value = generateSessionId()
}

// 监听打开状态
watch(() => props.visible, (newVal) => {
  if (newVal) {
    sessionId.value = generateSessionId()
    messages.value = []
    showQuickQuestions.value = false
  }
})
</script>

<style scoped>
.ai-chat-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.ai-chat-dialog {
  width: 90%;
  max-width: 700px;
  height: 80vh;
  max-height: 700px;
  background: #fff;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

/* 头部 */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ai-icon {
  font-size: 24px;
}

.chat-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.streaming-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  opacity: 0.9;
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 10px;
  border-radius: 12px;
}

.pulse {
  width: 8px;
  height: 8px;
  background: #fff;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: #fff;
  font-size: 28px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 新闻信息 */
.news-info {
  padding: 12px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.news-label {
  color: #666;
}

.news-title {
  color: #333;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 消息区域 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f7fa;
}

/* 欢迎消息 */
.welcome-message {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.welcome-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.welcome-message p {
  margin: 0 0 20px;
  font-size: 15px;
}

.summarize-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
  padding: 14px 32px;
  border-radius: 30px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.summarize-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.summarize-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 消息样式 */
.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.message.assistant .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.message.user .message-avatar {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.message-content {
  max-width: 75%;
}

.message-text {
  padding: 12px 16px;
  border-radius: 16px;
  line-height: 1.6;
  font-size: 14px;
  word-break: break-word;
  white-space: pre-wrap;
}

.message-text :deep(pre) {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
}

.message-text :deep(code) {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Fira Code', monospace;
  font-size: 13px;
}

.message-text :deep(strong) {
  color: inherit;
}

.message.user .message-text {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.message.user .message-text :deep(code) {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.message.assistant .message-text {
  background: #fff;
  color: #333;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.message.assistant .message-text :deep(h2),
.message.assistant .message-text :deep(h3),
.message.assistant .message-text :deep(h4) {
  margin-top: 12px;
  margin-bottom: 8px;
  color: #333;
}

.message.assistant .message-text :deep(li) {
  margin-left: 20px;
  margin-bottom: 4px;
}

/* 加载动画 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #999;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-8px);
    opacity: 1;
  }
}

/* 快捷问题 */
.quick-questions {
  padding: 12px 20px;
  background: #fff;
  border-top: 1px solid #eee;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.quick-label {
  font-size: 13px;
  color: #999;
}

.quick-btn {
  background: #f0f2f5;
  border: none;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-btn:hover:not(:disabled) {
  background: #667eea;
  color: #fff;
}

.quick-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 输入区域 */
.chat-input-area {
  padding: 16px 20px;
  background: #fff;
  border-top: 1px solid #eee;
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.chat-input-area textarea {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 24px;
  font-size: 14px;
  resize: none;
  max-height: 120px;
  font-family: inherit;
  line-height: 1.5;
  transition: border-color 0.3s;
}

.chat-input-area textarea:focus {
  outline: none;
  border-color: #667eea;
}

.chat-input-area textarea:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.send-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
  padding: 12px 24px;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.clear-btn {
  background: transparent;
  border: 1px solid #ddd;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.clear-btn:hover {
  background: #f5f5f5;
  border-color: #ccc;
}
</style>
