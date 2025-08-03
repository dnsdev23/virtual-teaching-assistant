@echo off
echo 正在重建虛擬助教資料庫...
echo.
echo 注意：這將刪除所有現有的使用者資料！
echo.
pause
echo.
echo 刪除舊資料庫檔案...
if exist "virtual_ta.db" (
    del "virtual_ta.db"
    echo 已刪除舊資料庫檔案
) else (
    echo 資料庫檔案不存在
)
echo.
echo 建立新資料庫...
E:\coding\vta6\.venv\Scripts\python.exe recreate_db.py
echo.
echo 資料庫重建完成！
echo.
pause
