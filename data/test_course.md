# 測試課程內容

## 第一章：Python 基礎

Python 是一種高階程式語言，具有簡潔易讀的語法。

### 1.1 變數與資料型別

在 Python 中，你可以輕鬆地建立變數：

```python
name = "小明"
age = 25
height = 175.5
is_student = True
```

### 1.2 條件控制

使用 if-elif-else 來進行條件判斷：

```python
if age >= 18:
    print("成年人")
else:
    print("未成年")
```

### 1.3 迴圈

Python 有兩種主要的迴圈：

1. for 迴圈：用於遍歷序列
2. while 迴圈：當條件為真時重複執行

## 第二章：函式

函式是可重複使用的程式碼區塊。

### 2.1 定義函式

```python
def greet(name):
    return f"Hello, {name}!"
```

### 2.2 參數類型

- 位置參數
- 關鍵字參數
- 預設參數

## 第三章：例外處理

使用 try-except 來處理例外：

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("不能除以零!")
```

## 總結

這份文件涵蓋了 Python 的基礎概念，包括變數、條件控制、迴圈、函式和例外處理。
