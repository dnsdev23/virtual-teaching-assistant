@echo off
echo 正在建立知識庫索引...
echo.
echo 請確認 data/ 資料夾中已放入 PDF 文件
echo.
pause
E:\coding\vta6\.venv\Scripts\python.exe index_documents.py
echo.
echo 知識庫建立完成！
pause
