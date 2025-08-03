# 虛擬助教系統使用指南

## 🚀 快速開始

### 1. 環境準備
```bash
# 建立虛擬環境
python -m venv .venv

# 啟動虛擬環境 (Windows)
.venv\Scripts\activate

# 安裝相依套件
pip install -r requirements.txt
```

### 2. 環境變數設定
複製 `.env.example` 為 `.env` 並填入您的 API 金鑰：

```env
# Google AI API Key for Gemini
GOOGLE_API_KEY="your_gemini_api_key_here"

# Google OAuth 2.0 Credentials
GOOGLE_CLIENT_ID="your_google_client_id_here"
GOOGLE_CLIENT_SECRET="your_google_client_secret_here"

# Admin Email Addresses
ADMIN_EMAILS="your.email@example.com,another.admin@example.com"

# JWT Secret Key
SECRET_KEY="your_strong_random_secret_key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. 建立知識庫
將課程文件（PDF、TXT、MD 格式）放入 `data/` 資料夾，然後執行：

```bash
python index_documents.py
```

### 4. 啟動系統
```bash
uvicorn main:app --reload
```

系統將在 `http://127.0.0.1:8000` 啟動。

## 📚 功能使用指南

### 🔐 身份驗證

#### Google 登入
1. 訪問 `http://127.0.0.1:8000/auth/login`
2. 系統會重新導向到 Google OAuth 頁面
3. 使用 Google 帳號登入
4. 登入成功後獲得 JWT Token

#### 管理員權限
- 在 `.env` 檔案的 `ADMIN_EMAILS` 中指定的 email 將自動獲得管理員權限
- 管理員可以訪問所有 `/api/admin/` 路徑的端點

### 🤖 RAG 問答系統

#### 提問方式
```bash
curl -X POST "http://127.0.0.1:8000/api/ask" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"question": "什麼是機器學習？"}'
```

#### Python 客戶端範例
```python
import requests

headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN",
    "Content-Type": "application/json"
}

response = requests.post(
    "http://127.0.0.1:8000/api/ask",
    headers=headers,
    json={"question": "解釋深度學習的概念"}
)

answer = response.json()["answer"]
print(answer)
```

### 📝 測驗系統

#### 1. 生成測驗
```python
import requests

# 生成測驗
response = requests.post(
    "http://127.0.0.1:8000/api/quiz/generate",
    headers={"Authorization": "Bearer YOUR_JWT_TOKEN"},
    json={
        "topic": "機器學習基礎",
        "num_questions": 5
    }
)

quiz = response.json()
quiz_id = quiz["id"]
```

#### 2. 提交答案
```python
# 提交測驗答案
answers = {
    "answers": [
        {"question_id": 1, "answer_index": 0},
        {"question_id": 2, "answer_index": 2},
        {"question_id": 3, "answer_index": 1}
    ]
}

response = requests.post(
    f"http://127.0.0.1:8000/api/quiz/submit/{quiz_id}",
    headers={"Authorization": "Bearer YOUR_JWT_TOKEN"},
    json=answers
)

result = response.json()
print(f"測驗成績: {result['score']}%")
```

### 🔧 管理員功能

#### 新增外部資源
```python
import requests

resource_data = {
    "url": "https://example.com/tutorial",
    "title": "機器學習入門教學",
    "description": "適合初學者的機器學習教學影片",
    "tags": "機器學習,教學,入門,影片"
}

response = requests.post(
    "http://127.0.0.1:8000/api/admin/resources",
    headers={"Authorization": "Bearer ADMIN_JWT_TOKEN"},
    json=resource_data
)
```

#### 列出所有資源
```python
response = requests.get(
    "http://127.0.0.1:8000/api/admin/resources",
    headers={"Authorization": "Bearer ADMIN_JWT_TOKEN"}
)

resources = response.json()
for resource in resources:
    print(f"{resource['title']}: {resource['url']}")
```

#### 刪除資源
```python
resource_id = 1
response = requests.delete(
    f"http://127.0.0.1:8000/api/admin/resources/{resource_id}",
    headers={"Authorization": "Bearer ADMIN_JWT_TOKEN"}
)
```

## 🛠️ API 測試

### 使用 Swagger UI
訪問 `http://127.0.0.1:8000/docs` 來使用互動式 API 文件：

1. 點擊 "Authorize" 按鈕
2. 輸入您的 JWT Token (格式：`Bearer YOUR_TOKEN`)
3. 嘗試各種 API 端點

### 使用 curl 測試

#### 測試系統狀態
```bash
curl -X GET "http://127.0.0.1:8000/"
```

#### 測試問答功能
```bash
curl -X POST "http://127.0.0.1:8000/api/ask" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"question": "什麼是 Python？"}'
```

#### 測試管理員功能
```bash
curl -X GET "http://127.0.0.1:8000/api/admin/status" \
     -H "Authorization: Bearer ADMIN_JWT_TOKEN"
```

## ⚠️ 常見問題

### Q: 如何獲得 Google OAuth 憑證？
A: 
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google+ API 和 People API
4. 建立 OAuth 2.0 用戶端 ID
5. 設定授權重新導向 URI 為 `http://127.0.0.1:8000/auth/callback`

### Q: 如何獲得 Google Gemini API 金鑰？
A:
1. 前往 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 建立新的 API 金鑰
3. 將金鑰複製到 `.env` 檔案中

### Q: 知識庫如何更新？
A: 
1. 將新的文件放入 `data/` 資料夾
2. 重新執行 `python index_documents.py`
3. 重新啟動 FastAPI 應用程式

### Q: 如何重設資料庫？
A:
```bash
# 刪除現有資料庫
rm virtual_ta.db

# 重新啟動應用程式，資料庫會自動建立
python main.py
```

### Q: 測驗題目品質不佳怎麼辦？
A:
- 檢查課程文件的品質和完整性
- 調整 AI 提示詞的參數
- 增加更多相關的課程內容

## 📊 系統監控

### 檢查系統狀態
```python
# 檢查資料庫連線
from database import SessionLocal
from models import User

db = SessionLocal()
user_count = db.query(User).count()
print(f"系統中有 {user_count} 位使用者")
db.close()
```

### 檢查知識庫
```python
import os
if os.path.exists("chroma_db"):
    files = os.listdir("chroma_db")
    print(f"知識庫包含 {len(files)} 個檔案")
```

## 🚀 生產部署建議

1. **安全性**:
   - 使用強密碼作為 `SECRET_KEY`
   - 限制 CORS 來源到特定網域
   - 使用 HTTPS

2. **效能**:
   - 使用 PostgreSQL 替代 SQLite
   - 設定資料庫連線池
   - 使用 Redis 快取

3. **監控**:
   - 添加日誌記錄
   - 設定錯誤追蹤
   - 監控 API 回應時間

4. **擴展性**:
   - 使用 Docker 容器化
   - 設定負載均衡
   - 使用雲端向量資料庫
