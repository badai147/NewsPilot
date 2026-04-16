# 新闻头条 - Vue3 前端

基于 Vue3 构建的新闻阅读应用前端，使用 Vite 作为构建工具。

## 功能特性

- **新闻浏览**: 支持多分类新闻列表和详情查看
- **用户认证**: 注册、登录、个人信息管理
- **收藏功能**: 收藏/取消收藏新闻，查看收藏列表
- **浏览历史**: 自动记录浏览历史，查看和删除历史记录
- **用户资料**: 修改个人资料和密码

## 技术栈

- Vue 3 (Composition API)
- Vue Router 4
- Pinia (状态管理)
- Axios (HTTP 请求)
- Dayjs (日期处理)
- Vite (构建工具)

## 项目结构

```
frontend/
├── src/
│   ├── views/           # 页面组件
│   │   ├── Home.vue         # 首页
│   │   ├── Login.vue        # 登录页
│   │   ├── Register.vue      # 注册页
│   │   ├── NewsDetail.vue    # 新闻详情
│   │   ├── Profile.vue       # 个人中心
│   │   ├── Favorites.vue     # 收藏列表
│   │   └── History.vue       # 浏览历史
│   ├── services/        # API 服务
│   │   └── api.js           # 接口定义
│   ├── stores/          # Pinia 状态管理
│   │   └── user.js          # 用户状态
│   ├── router/          # 路由配置
│   │   └── index.js
│   ├── utils/           # 工具函数
│   │   └── request.js       # Axios 封装
│   ├── App.vue
│   ├── main.js
│   └── style.css
├── index.html
├── package.json
└── vite.config.js
```

## 安装与运行

```bash
# 安装依赖
npm install

# 开发模式运行
npm run dev

# 构建生产版本
npm run build
```

## 配置说明

前端默认访问 `/api` 开头的请求会自动代理到 `http://localhost:8000`（后端地址）。
如需修改，请编辑 `vite.config.js` 中的 `server.proxy` 配置。

## 依赖后端 API

项目需要后端服务运行在 `http://localhost:8000`，确保后端已完成启动。

后端项目位于 `../backend/`，启动方式请参考后端 README。
