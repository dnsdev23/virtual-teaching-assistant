@echo off
echo 正在啟動虛擬助教 API 伺服器...
echo.
echo 請確認你已經完成以下步驟：
echo 1. 設定 .env 檔案中的 API 金鑰
echo 2. 將 PDF 文件放入 data/ 資料夾
echo 3. 執行過 index_documents.py 建立知識庫
echo.
echo 伺服器將在 http://127.0.0.1:8000 上運行
echo API 文件可在 http://127.0.0.1:8000/docs 查看
echo.
pause
E:\coding\vta6\.venv\Scripts\python.exe -m uvicorn main:app --reload
