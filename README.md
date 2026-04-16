# 新闻头条系统 (Headline)

[![标准 README 规范](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

一个现代化的新闻聚合平台，提供新闻浏览、AI智能总结、多轮对话以及个性化收藏等功能。

## 特性

- **新闻浏览**：支持多分类新闻列表、详情查看、无限滚动加载
- **AI 智能助手**：基于 LangChain + LLM 的新闻总结与智能问答
- **用户系统**：完整的注册、登录、个人中心功能
- **收藏管理**：收藏感兴趣的新闻，便捷管理收藏夹
- **浏览历史**：自动记录阅读历史，快速回顾阅读内容
- **流式响应**：AI 回答采用 SSE 流式输出，体验流畅

## 内容列表

- [项目简介](#项目简介)
- [技术栈](#技术栈)
- [前置要求](#前置要求)
- [安装部署](#安装部署)
- [配置说明](#配置说明)
- [使用说明](#使用说明)
- [API 文档](#api-文档)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 项目简介

本项目是一个前后端分离的全栈新闻应用，采用 Vue 3 + FastAPI 技术栈构建。后端提供 RESTful API 接口及 AI 流式服务，前端实现响应式新闻浏览体验。

### 项目结构

```
headline/
├── backend/                    # 后端服务
│   ├── agents/                 # AI Agent 模块
│   ├── config/                 # 配置文件
│   ├── crud/                   # 数据库操作
│   ├── models/                 # 数据模型
│   ├── routers/                # API 路由
│   ├── schemas/                # Pydantic 模型
│   ├── utils/                  # 工具函数
│   └── main.py                 # 应用入口
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   ├── stores/              # Pinia 状态管理
│   │   ├── services/           # API 服务
│   │   └── router/             # 路由配置
│   └── package.json
│
└── README.md
```

## 技术栈

### 前端

- **框架**：Vue 3 (Composition API)
- **路由**：Vue Router 4
- **状态管理**：Pinia
- **HTTP 客户端**：Axios
- **构建工具**：Vite 5
- **日期处理**：Day.js

### 后端

- **框架**：FastAPI
- **AI 能力**：LangChain + OpenAI
- **数据库**：MySQL + SQLAlchemy (异步)
- **服务器**：Uvicorn

## 前置要求

在开始之前，请确保已安装以下软件：

| 软件 | 版本要求 | 说明 |
|------|---------|------|
| Node.js | ≥ 18.0 | 前端开发环境 |
| npm / yarn | 最新稳定版 | 包管理工具 |
| Python | ≥ 3.10 | 后端运行环境 |
| pip | 最新稳定版 | Python 包管理 |
| MySQL | ≥ 8.0 | 数据库服务 |

## 安装部署

### 1. 克隆项目

```bash
git clone <repository-url>
cd headline
```

### 2. 后端部署

#### 2.1 创建虚拟环境

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

#### 2.2 安装依赖

```bash
pip install -r requirements.txt
```

#### 2.3 配置数据库

编辑 `backend/config/db_conf.py` 中的数据库连接配置：

```python
# 数据库配置
DATABASE_URL = "mysql+aiomysql://username:password@host:port/database"
```

#### 2.4 启动后端服务

```bash
python main.py
```

或使用 uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后访问 `http://localhost:8000/docs` 查看 API 文档。

### 3. 前端部署

#### 3.1 安装依赖

```bash
cd frontend
npm install
```

#### 3.2 配置 API 地址

如需修改后端 API 地址，编辑 `frontend/src/services/api.js`：

```javascript
const BASE_URL = 'http://localhost:8000'
```

#### 3.3 启动开发服务器

```bash
npm run dev
```

前端访问 `http://localhost:5173`

#### 3.4 构建生产版本

```bash
npm run build
```

构建产物位于 `dist/` 目录。

## 配置说明

### 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | `sk-xxxxx` |
| `DATABASE_URL` | 数据库连接字符串 | `mysql+aiomysql://...` |

### AI 功能配置

编辑 `backend/config/ai_conf.py` 配置 AI 模型参数：

```python
# AI 模型配置
llm_config = {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 2000,
}
```

## 使用说明

### 新闻浏览

1. 启动前后端服务后，在首页选择新闻分类
2. 点击新闻卡片进入详情页
3. 支持上拉加载更多新闻

### AI 智能助手

1. 在新闻详情页点击右下角 **AI 总结** 按钮
2. 系统自动生成新闻摘要
3. 可继续向 AI 提问，深入了解新闻内容
4. 支持多轮对话，AI 会记住上下文

### 用户功能

- **注册/登录**：点击导航栏登录入口
- **收藏新闻**：在新闻详情页点击收藏按钮
- **查看收藏**：在个人中心查看收藏列表
- **浏览历史**：自动记录，可随时回顾

## API 文档

启动后端服务后访问交互式 API 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 主要接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/news/categories` | 获取新闻分类 |
| GET | `/api/news/list` | 获取新闻列表 |
| GET | `/api/news/detail` | 获取新闻详情 |
| POST | `/api/ai/summarize` | AI 新闻总结 |
| POST | `/api/ai/chat` | AI 智能问答 |
| POST | `/api/users/register` | 用户注册 |
| POST | `/api/users/login` | 用户登录 |

## 贡献指南

欢迎提交 Pull Request 或创建 Issue！

### 开发流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发规范

- 遵循 ESLint 代码规范
- 提交信息使用中文，格式清晰
- 新功能需添加相应测试
- 更新文档说明

## 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

使用过程中如遇到问题，欢迎提交 Issue。
