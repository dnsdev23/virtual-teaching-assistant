# 虛擬助教 API (Virtual Teaching Assistant)

這是一個基於 FastAPI 的虛擬助教系統，整合了 Google OAuth 認證、RAG (Retrieval-Augmented Generation) 問答系統，以及 Google Gemini AI。

## 功能特色

- **Google OAuth 登入**：使用 Google 帳戶進行用戶認證
- **JWT 權杖驗證**：安全的 API 存取控制
- **RAG 問答系統**：基於上傳的 PDF 文件回答問題
- **Google Gemini AI**：使用 Google 最新的生成式 AI 模型
- **向量資料庫**：使用 ChromaDB 儲存文件嵌入向量
- **RESTful API**：完整的 API 文件與互動介面

## 安裝步驟

### 1. 安裝 Python 依賴套件

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

編輯 `.env` 檔案，填入你的 API 金鑰：

```bash
# Google AI API Key for Gemini
GOOGLE_API_KEY="your_actual_gemini_api_key"

# Google OAuth 2.0 Credentials
GOOGLE_CLIENT_ID="your_actual_google_client_id"
GOOGLE_CLIENT_SECRET="your_actual_google_client_secret"

# JWT Secret Key (可以用 Python 生成)
SECRET_KEY="your_strong_random_secret_key"
```

#### 如何取得 API 金鑰：

**Google AI API Key:**
1. 前往 [Google AI Studio](https://aistudio.google.com/)
2. 註冊並登入
3. 建立新的 API 金鑰

**Google OAuth 憑證:**
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google+ API
4. 建立 OAuth 2.0 憑證
5. 設定重新導向 URI: `http://127.0.0.1:8000/auth/callback`

**生成 JWT Secret Key:**
```python
import os
print(os.urandom(32).hex())
```

### 3. 準備文件資料

將你的 PDF 教材放在 `data/` 資料夾中。

### 4. 建立向量資料庫

執行以下命令來處理 PDF 文件並建立知識庫：

```bash
python index_documents.py
```

### 5. 啟動 API 伺服器

```bash
uvicorn main:app --reload
```

伺服器將在 `http://127.0.0.1:8000` 上運行。

## API 端點

- `GET /` - 歡迎頁面
- `GET /docs` - API 文件 (Swagger UI)
- `GET /auth/login` - Google 登入
- `GET /auth/callback` - OAuth 回調
- `POST /api/ask` - 提問 (需要認證)
- `GET /api/users/me` - 取得使用者資料 (需要認證)

## 使用方式

1. 開啟 `http://127.0.0.1:8000/auth/login` 進行 Google 登入
2. 取得 JWT 權杖後，可以使用 `/api/ask` 端點提問
3. 系統會根據你上傳的 PDF 內容回答問題

## 專案結構

```
vta6/
├── .env                    # 環境變數
├── requirements.txt        # Python 依賴套件
├── database.py            # 資料庫設定
├── models.py              # 資料庫模型
├── schemas.py             # Pydantic 模型
├── crud.py                # 資料庫操作
├── auth.py                # 認證邏輯
├── index_documents.py     # 文件索引腳本
├── main.py                # 主應用程式
├── data/                  # PDF 文件資料夾
└── chroma_db/             # 向量資料庫 (自動生成)
```

## 注意事項

- 首次運行前請確實設定 `.env` 檔案中的所有參數
- PDF 文件必須放在 `data/` 資料夾中
- 向量資料庫會在首次執行 `index_documents.py` 時建立
- 生產環境請修改 CORS 設定以限制來源網域
