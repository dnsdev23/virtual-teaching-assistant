# 故障排除指南

## CSS 警告：Unknown at rule @tailwind

### 問題描述
VS Code 的 CSS 語言服務器會顯示 `@tailwind` 和 `@apply` 指令的警告：
- `Unknown at rule @tailwind`
- `Unknown at rule @apply`

### 這是正常的嗎？
**是的，這些警告是正常的！** 這些並不是真正的錯誤：

1. **VS Code 不認識 Tailwind 指令**：VS Code 的內建 CSS 語言服務器不理解 Tailwind CSS 的特殊指令
2. **應用仍然正常運行**：儘管有這些警告，您的應用會正常編譯和運行
3. **Vite + PostCSS 處理**：構建工具會正確處理這些指令

### 解決方案

#### 方案 1：忽略警告（推薦）
我們已經在 `.vscode/settings.json` 中配置了忽略這些警告：
```json
{
  "css.validate": false,
  "css.lint.unknownAtRules": "ignore"
}
```

#### 方案 2：使用 PostCSS 語言模式
將文件關聯設置為 PostCSS：
```json
{
  "files.associations": {
    "*.css": "postcss"
  }
}
```

#### 方案 3：安裝 Tailwind CSS IntelliSense
我們已經安裝了 `Tailwind CSS IntelliSense` 擴展，它提供：
- 自動完成
- 語法高亮
- 錯誤檢測
- 懸停預覽

## 其他常見問題

### 1. 樣式不生效
確保：
- Tailwind CSS 正確安裝：`npm list tailwindcss`
- PostCSS 配置正確：檢查 `postcss.config.js`
- 內容路徑配置：檢查 `tailwind.config.js` 中的 `content` 數組

### 2. 開發服務器錯誤
如果看到 PostCSS 錯誤：
```bash
# 重新安裝依賴
npm install

# 清除緩存
npm run dev -- --force
```

### 3. 構建錯誤
```bash
# 清除構建緩存
rm -rf dist
npm run build
```

## 驗證安裝

### 檢查 Tailwind 是否工作
1. 開發服務器正常啟動 ✅
2. 瀏覽器中可以看到樣式 ✅
3. 熱重載正常工作 ✅

### 終端輸出應該顯示：
```
VITE v7.0.6  ready in 220 ms
➜  Local:   http://localhost:5174/
```

### 瀏覽器檢查：
按 F12 打開開發者工具，檢查元素是否有 Tailwind 樣式類。

## 最佳實踐

1. **保持 VS Code 設置**：不要刪除 `.vscode/settings.json` 文件
2. **使用 Tailwind IntelliSense**：依賴擴展提供的智能提示
3. **忽略 CSS 警告**：專注於實際的功能錯誤
4. **定期更新**：保持 Tailwind CSS 和相關工具的更新

---

**結論**：`@tailwind` 警告是 VS Code 的限制，不是您的代碼問題。應用運行正常，可以繼續開發！
