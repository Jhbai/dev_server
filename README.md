# Web IDE 後端服務

這是一個基於 **FastAPI** 構建的 Web IDE 後端服務，提供文件管理、目錄瀏覽和命令執行等功能，並內建一個簡單的前端 GUI 介面。

---

## 📋 功能特點

- **文件管理**：讀取、寫入、創建、刪除文件和目錄
- **目錄瀏覽**：列出目錄內容，支援導航
- **命令執行**：在伺服器上執行 Shell 命令
- **內建 GUI**：提供類似 VS Code 的網頁介面
- **基本認證**：使用 HTTP Basic Authentication 進行安全驗證

---

## 🚀 啟動方法

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數（可選）

預設用戶名和密碼為 `admin` / `password123`，可以透過環境變數自訂：

```bash
export IDE_USERNAME="your_username"
export IDE_PASSWORD="your_password"
```

### 3. 啟動服務

```bash
python main.py
```

服務預設啟動在 `http://127.0.0.1:8000`

---

## 📡 API 端點介紹

所有 API 端點都需要 **HTTP Basic Authentication** 認證。

### 1. 列出目錄內容

| 方法 | 端點 | 說明 |
|------|------|------|
| GET | `/api/list` | 列出指定路徑下的所有文件和目錄 |

**查詢參數：**
- `path` (string, 預設 "."): 要列出的目錄路徑

**回應範例：**
```json
[
  {"name": "src", "is_dir": true, "path": "/path/to/src"},
  {"name": "main.py", "is_dir": false, "path": "/path/to/main.py"}
]
```

---

### 2. 讀取文件

| 方法 | 端點 | 說明 |
|------|------|------|
| GET | `/api/read` | 讀取指定文件的內容 |

**查詢參數：**
- `path` (string, 必填): 要讀取的文件路徑

**回應範例：**
```json
{
  "content": "文件內容..."
}
```

---

### 3. 寫入文件

| 方法 | 端點 | 說明 |
|------|------|------|
| POST | `/api/write` | 寫入內容到指定文件 |

**請求體 (JSON)：**
```json
{
  "path": "/path/to/file.txt",
  "content": "要寫入的內容"
}
```

**回應範例：**
```json
{"status": "success"}
```

---

### 4. 創建目錄

| 方法 | 端點 | 說明 |
|------|------|------|
| POST | `/api/create_dir` | 創建新的目錄 |

**請求體 (JSON)：**
```json
{
  "path": "/path/to/new_directory"
}
```

**回應範例：**
```json
{"status": "success"}
```

---

### 5. 刪除文件或目錄

| 方法 | 端點 | 說明 |
|------|------|------|
| DELETE | `/api/delete` | 刪除指定的文件或目錄 |

**查詢參數：**
- `path` (string, 必填): 要刪除的文件或目錄路徑

**回應範例：**
```json
{"status": "success"}
```

---

### 6. 執行 Shell 命令

| 方法 | 端點 | 說明 |
|------|------|------|
| POST | `/api/cmd` | 在伺服器上執行 Shell 命令 |

**請求體 (JSON)：**
```json
{
  "command": "ls -la",
  "cwd": "."
}
```

**參數說明：**
- `command` (string, 必填): 要執行的命令
- `cwd` (string, 預設 "."): 命令執行的工作目錄

**回應範例：**
```json
{
  "stdout": "命令標準輸出",
  "stderr": "命令錯誤輸出",
  "returncode": 0
}
```

---

### 7. 內建 GUI 介面

| 方法 | 端點 | 說明 |
|------|------|------|
| GET | `/docs/gui` | 訪問內建的 Web IDE 圖形介面 |

這個端點提供一個類似 VS Code 的網頁介面，包含：
- 左側檔案瀏覽器
- 中央程式碼編輯器
- 底部終端機

---

### 8. API 文件

| 方法 | 端點 | 說明 |
|------|------|------|
| GET | `/docs` | FastAPI 自動生成的 API 文件（需要認證） |

---

## 🔐 認證方式

所有 API 端點都使用 **HTTP Basic Authentication**。

### cURL 範例：
```bash
curl -u admin:password123 http://127.0.0.1:8000/api/list?path=.
```

### JavaScript Fetch 範例：
```javascript
fetch('/api/list?path=.', {
  headers: {
    'Authorization': 'Basic ' + btoa('admin:password123')
  }
});
```

---

## 📦 依賴項目

- **FastAPI** >= 0.104.0 - Web 框架
- **Uvicorn** >= 0.24.0 - ASGI 伺服器
- **Pydantic** >= 2.0.0 - 數據驗證

---

## ⚠️ 安全注意事項

1. 生產環境中請務必修改預設的用戶名和密碼
2. 建議使用環境變數儲存認證資訊
3. 考慮使用 HTTPS 加密傳輸
4. 命令執行功能具有潛在風險，請謹慎使用

---

## 🛠️ 技術棧

- **後端框架**: FastAPI
- **伺服器**: Uvicorn
- **數據驗證**: Pydantic
- **認證**: HTTP Basic Authentication
- **前端**: 原生 HTML/CSS/JavaScript
