# 虛擬教學助理 - 前端應用

## 項目概述

這是一個基於 React + Vite + Tailwind CSS 構建的現代化虛擬教學助理前端應用。該應用提供智能問答、個性化學習建議和完整的學習分析功能。

## 技術棧

- **React 19** - 前端框架
- **Vite** - 構建工具和開發服務器
- **Tailwind CSS** - 原子化 CSS 框架
- **Axios** - HTTP 客戶端
- **React Router DOM** - 路由管理

## 功能特性

### 🔐 用戶認證
- Google OAuth 2.0 登入
- JWT Token 管理
- 自動登入狀態維護

### 💬 智能對話
- 實時 AI 問答
- 打字動畫效果
- 消息歷史記錄
- 響應式聊天界面

### 📊 個性化體驗
- 用戶個人資料顯示
- 學習進度追蹤
- 個性化推薦系統

### 🎨 現代化 UI
- 響應式設計
- 暗色/亮色主題支持
- 流暢動畫效果
- 無障礙訪問支持

## 項目結構

```
src/
├── components/          # 可重用組件
│   ├── LoadingSpinner.jsx
│   ├── Toast.jsx
│   └── Modal.jsx
├── services/           # API 服務
│   └── api.js
├── utils/             # 工具函數
│   └── helpers.js
├── App.jsx            # 主應用組件
├── main.jsx           # 應用入口
├── index.css          # 全局樣式
└── ...
```

## 安裝和運行

### 前置要求
- Node.js 18+ 
- npm 或 yarn

### 安裝依賴
```bash
npm install
```

### 開發模式
```bash
npm run dev
```
應用將在 http://localhost:5173 運行

### 構建生產版本
```bash
npm run build
```

### 預覽生產版本
```bash
npm run preview
```

## 環境配置

在 `.env` 文件中配置以下變數：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_APP_NAME=虛擬教學助理
VITE_APP_VERSION=1.0.0
VITE_DEV_MODE=true
VITE_ENABLE_LOGGING=true
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_RECOMMENDATIONS=true
```

## API 集成

### 認證端點
- `GET /api/users/me` - 獲取當前用戶信息
- `GET /auth/login` - Google OAuth 登入

### 聊天端點
- `POST /api/ask` - 發送問題到 AI 助教

### 用戶數據端點
- `GET /api/users/quiz-history` - 獲取測驗歷史
- `GET /api/users/recommendations` - 獲取個性化推薦
- `GET /api/users/analytics` - 獲取學習分析

## 組件說明

### App.jsx
主應用組件，包含：
- 用戶認證邏輯
- 聊天界面
- 狀態管理

### LoadingSpinner.jsx
可配置的加載動畫組件，支持不同尺寸。

### Toast.jsx
通知組件，支持多種類型（成功、錯誤、警告、信息）。

### Modal.jsx
模態框組件，支持不同尺寸和自定義內容。

## 樣式系統

使用 Tailwind CSS 提供：
- 響應式設計工具
- 自定義顏色方案
- 動畫效果
- 組件樣式類

### 自定義 CSS 類
- `.btn-primary` - 主要按鈕樣式
- `.btn-secondary` - 次要按鈕樣式
- `.btn-outline` - 邊框按鈕樣式
- `.card` - 卡片樣式
- `.input-field` - 輸入框樣式
- `.gradient-bg` - 漸變背景
- `.text-gradient` - 漸變文字

## 開發指南

### 代碼規範
- 使用 ES6+ 語法
- 組件採用函數式組件 + Hooks
- 遵循 React 最佳實踐
- 保持組件單一職責

### 狀態管理
- 使用 React 內建狀態管理（useState, useEffect）
- LocalStorage 用於持久化認證狀態
- API 狀態通過 React Query 或類似工具管理（可選）

### 錯誤處理
- API 錯誤統一處理
- 用戶友好的錯誤消息
- 優雅降級處理

## 性能優化

- Vite 快速構建和熱重載
- Tailwind CSS 生產構建時的 CSS 清理
- 組件懶加載（按需實現）
- 圖片優化和懶加載

## 瀏覽器支持

- Chrome (最新版)
- Firefox (最新版)
- Safari (最新版)
- Edge (最新版)

## 部署

### Vercel 部署
```bash
npm i -g vercel
vercel
```

### Netlify 部署
```bash
npm run build
# 上傳 dist/ 目錄到 Netlify
```

### 自定義服務器
```bash
npm run build
# 將 dist/ 目錄內容部署到 Web 服務器
```

## 貢獻指南

1. Fork 本項目
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing-feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 創建 Pull Request

## 許可證

本項目採用 MIT 許可證 - 查看 [LICENSE](LICENSE) 文件了解詳情。

## 聯繫方式

如有問題或建議，請通過以下方式聯繫：
- 項目 Issues: [GitHub Issues](https://github.com/your-username/vta6/issues)
- 郵箱: your-email@example.com

---

**🚀 讓學習變得更智能！**+ Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
