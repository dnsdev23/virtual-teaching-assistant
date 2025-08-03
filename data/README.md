# 資料夾結構說明 / Data Folder Structure

本系統現在支援章節化的知識庫管理。請按照以下結構組織您的課程資料：

## 資料夾結構 / Folder Structure

```
data/
├── chapter1/                    # 第一章
│   ├── materials/              # 教材資料夾
│   │   ├── lecture1.pdf
│   │   ├── slides1.pdf
│   │   └── ...
│   └── question_bank/          # 題庫資料夾
│       ├── quiz1.pdf
│       ├── exercises1.pdf
│       └── ...
├── chapter2/                    # 第二章
│   ├── materials/
│   └── question_bank/
└── ...
```

## 使用說明 / Usage Instructions

1. **創建章節資料夾**: 每個章節應該有自己的資料夾，命名建議使用 `chapter1`, `chapter2` 等格式
2. **添加教材**: 將課程講義、投影片等教材 PDF 檔案放入 `materials/` 資料夾
3. **添加題庫**: 將練習題、測驗題等 PDF 檔案放入 `question_bank/` 資料夹
4. **執行索引**: 運行 `python index_documents.py` 來建立向量資料庫
5. **使用 API**: 在調用 `/api/ask` 和 `/api/quiz/generate` 時指定 `chapter` 參數

## API 使用範例 / API Usage Examples

### 獲取章節列表
```
GET /api/chapters
```

### 章節化問答
```
POST /api/ask?chapter=chapter1
{
  "question": "什麼是機器學習？"
}
```

### 章節化測驗生成
```
POST /api/quiz/generate?chapter=chapter1
{
  "topic": "機器學習基礎",
  "num_questions": 5
}
```

## 支援的檔案格式 / Supported File Formats

- PDF 檔案 (`.pdf`)
- 系統會自動掃描各章節資料夾中的所有 PDF 檔案

## 注意事項 / Important Notes

- 資料夾名稱建議使用英文，避免特殊字符
- 每次添加新檔案後，需要重新執行 `index_documents.py`
- 系統會為每個章節建立獨立的向量資料庫，存儲在 `chroma_db/` 資料夾中
