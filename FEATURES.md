# 虛擬助教系統功能清單

## 🎯 核心功能

### 1. 身份驗證與授權
- **Google OAuth 2.0 登入**: 使用 Google 帳號快速登入
- **JWT Token 管理**: 安全的存取權杖機制
- **角色權限控制**: 支援 admin 和 user 兩種角色
- **管理員權限**: 基於環境變數 `ADMIN_EMAILS` 自動分配管理員權限

### 2. RAG 問答系統
- **智能問答**: 基於課程內容的問題回答
- **向量資料庫**: 使用 ChromaDB 儲存文件嵌入
- **文件檢索**: 結合相關文件內容生成答案
- **外部資源整合**: 自動搜尋並引用相關外部資源

### 3. AI 自動出題測驗系統
- **動態出題**: AI 根據課程內容自動生成測驗題目
- **多選題支援**: 支援 3-4 個選項的單選題
- **測驗管理**: 完整的測驗建立、提交、評分流程
- **答題記錄**: 保存學生的答題歷史和成績

### 4. 外部資源管理 (管理員功能)
- **資源新增**: 管理員可新增外部學習資源
- **標籤搜尋**: 支援基於標籤的資源搜尋功能
- **資源列表**: 查看所有外部資源
- **資源刪除**: 管理員可刪除不需要的資源

## 🏗️ 技術架構

### 後端技術棧
- **FastAPI**: 現代 Python Web 框架
- **SQLAlchemy**: ORM 資料庫操作
- **SQLite**: 輕量級關聯式資料庫
- **Google Gemini AI**: 大語言模型和嵌入模型
- **LangChain**: RAG 系統框架
- **ChromaDB**: 向量資料庫

### 安全機制
- **環境變數**: 敏感資訊通過 .env 檔案管理
- **JWT 加密**: 使用 HMAC SHA256 算法
- **CORS 支援**: 跨域請求處理
- **角色驗證**: 基於裝飾器的權限控制

## 📊 資料庫模型

### User (使用者)
- 基本資訊：email, name, picture
- 角色管理：role (admin/user)
- 關聯：測驗記錄

### QuizAttempt (測驗嘗試)
- 測驗資訊：score, created_at
- 使用者關聯：user_id
- 問題關聯：questions

### Question (問題)
- 問題內容：question_text
- 答案資訊：correct_answer_index, user_answer_index
- 狀態：is_correct (correct/incorrect/unanswered)

### Choice (選項)
- 選項內容：choice_text
- 問題關聯：question_id

### ExternalResource (外部資源)
- 資源資訊：url, title, description
- 搜尋支援：tags

## 🔌 API 端點

### 身份驗證
- `GET /auth/login` - Google OAuth 登入
- `GET /auth/callback` - OAuth 回調處理
- `GET /api/users/me` - 獲取當前使用者資訊

### RAG 問答
- `POST /api/ask` - 提交問題並獲取答案

### 測驗系統
- `POST /api/quiz/generate` - 生成測驗
- `POST /api/quiz/submit/{attempt_id}` - 提交測驗答案

### 管理員功能
- `GET /api/admin/status` - 管理員狀態檢查
- `POST /api/admin/resources` - 新增外部資源
- `GET /api/admin/resources` - 列出所有資源
- `DELETE /api/admin/resources/{resource_id}` - 刪除資源

### 系統資訊
- `GET /` - 系統歡迎頁面
- `GET /docs` - API 文件 (Swagger UI)
- `GET /openapi.json` - OpenAPI 規格

## 🚀 部署需求

### 環境變數
```env
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
ADMIN_EMAILS=admin@example.com,admin2@example.com
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 目錄結構
```
project/
├── main.py              # 主應用程式
├── auth.py              # 身份驗證模組
├── crud.py              # 資料庫操作
├── models.py            # 資料模型
├── schemas.py           # API 結構定義
├── database.py          # 資料庫設定
├── index_documents.py   # 知識庫建立
├── .env                 # 環境變數
├── data/                # 課程文件目錄
├── chroma_db/           # 向量資料庫
└── virtual_ta.db        # SQLite 資料庫
```

## 🎓 使用流程

1. **管理員設定**: 透過 `ADMIN_EMAILS` 指定管理員
2. **知識庫建立**: 執行 `index_documents.py` 建立課程知識庫
3. **系統啟動**: 運行 FastAPI 應用程式
4. **Google 登入**: 使用者透過 Google OAuth 登入
5. **問答互動**: 學生提問，系統提供基於課程內容的答案
6. **測驗練習**: AI 自動出題，學生作答並獲得即時回饋
7. **資源管理**: 管理員可新增和管理外部學習資源

## 🔮 未來擴展

- 多語言支援
- 更多檔案格式支援 (Word, PowerPoint 等)
- 學習進度追蹤
- 討論區功能
- 即時通知系統
- 移動端應用程式
- 批量匯入測驗題目
- 學習分析儀表板
