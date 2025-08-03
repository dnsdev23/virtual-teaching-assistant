# 如何使用此專案

## 重要提醒

在開始使用之前，請完成以下步驟：

### 1. 設定 API 金鑰

編輯 `.env` 檔案，將以下項目替換為你的實際金鑰：

```
GOOGLE_API_KEY="your_gemini_api_key_here"
GOOGLE_CLIENT_ID="your_google_client_id_here"
GOOGLE_CLIENT_SECRET="your_google_client_secret_here"
SECRET_KEY="your_strong_random_secret_key"
```

### 2. 準備 PDF 文件

將你想要用作知識庫的 PDF 文件放在 `data/` 資料夾中。

### 3. 建立知識庫

執行以下命令來處理 PDF 並建立向量資料庫：

```bash
E:/coding/vta6/.venv/Scripts/python.exe index_documents.py
```

### 4. 啟動伺服器

```bash
E:/coding/vta6/.venv/Scripts/python.exe -m uvicorn main:app --reload
```

### 5. 測試 API

開啟瀏覽器，前往：
- API 文件：http://127.0.0.1:8000/docs
- Google 登入：http://127.0.0.1:8000/auth/login

## 故障排除

如果遇到問題，請檢查：
1. `.env` 檔案是否設定正確
2. PDF 文件是否存在於 `data/` 資料夾
3. 是否已執行 `index_documents.py`
4. Google OAuth 設定是否正確

## 範例使用流程

1. 將課程資料（PDF 格式）放入 `data/` 資料夾
2. 執行 `index_documents.py` 建立知識庫
3. 啟動 FastAPI 伺服器
4. 透過 Google 登入取得權杖
5. 使用 `/api/ask` 端點提問
