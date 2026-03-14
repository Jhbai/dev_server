# Web IDE Backend API

這是一個基於 FastAPI 構建的 Web IDE 後端服務，提供文件管理、代碼編輯和命令執行等功能。

## 功能特點

- 📁 文件和目錄管理（列出、讀取、寫入、創建、刪除）
- 💻 內建 Web 界面進行代碼編輯
- 💾 執行 Shell 命令並查看輸出
- 🎨 類似 VS Code 的深色主題界面

## 依賴套件

請確保已安裝以下套件：

```bash
pip install -r requirements.txt
```

或手動安裝：

```bash
pip install fastapi uvicorn pydantic
```

## 啟動方法

### 方式一：直接運行

```bash
python main.py
```

### 方式二：使用 uvicorn 命令

```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

服務啟動後，可以訪問以下地址：

- **Web IDE 界面**: http://127.0.0.1:8000/docs/gui
- **API 文檔**: http://127.0.0.1:8000/docs

## API 端點說明

### 1. 列出目錄內容

**端點**: `GET /api/list`

**功能**: 列出指定目錄中的所有文件和子目錄

**參數**:
| 參數名稱 | 類型 | 必填 | 預設值 | 說明 |
|---------|------|------|--------|------|
| path | string | 否 | "." | 要列出的目錄路徑 |

**回應範例**:
```json
[
  {
    "name": "src",
    "is_dir": true,
    "path": "./src"
  },
  {
    "name": "main.py",
    "is_dir": false,
    "path": "./main.py"
  }
]
```

---

### 2. 讀取文件

**端點**: `GET /api/read`

**功能**: 讀取指定文件的內容

**參數**:
| 參數名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| path | string | 是 | 要讀取的文件路徑 |

**回應範例**:
```json
{
  "content": "print('Hello, World!')"
}
```

---

### 3. 寫入文件

**端點**: `POST /api/write`

**功能**: 創建或覆蓋指定文件

**請求體**:
```json
{
  "path": "example.txt",
  "content": "這是文件內容"
}
```

| 欄位名稱 | 類型 | 必填 | 預設值 | 說明 |
|---------|------|------|--------|------|
| path | string | 是 | - | 文件路徑 |
| content | string | 否 | "" | 文件內容 |

**回應範例**:
```json
{
  "status": "success"
}
```

---

### 4. 創建目錄

**端點**: `POST /api/create_dir`

**功能**: 創建指定路徑的目錄（包含父目錄）

**請求體**:
```json
{
  "path": "new_folder/subfolder"
}
```

| 欄位名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| path | string | 是 | 要創建的目錄路徑 |

**回應範例**:
```json
{
  "status": "success"
}
```

---

### 5. 刪除文件或目錄

**端點**: `DELETE /api/delete`

**功能**: 刪除指定的文件或目錄（目錄會递归刪除）

**參數**:
| 參數名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| path | string | 是 | 要刪除的文件或目錄路徑 |

**回應範例**:
```json
{
  "status": "success"
}
```

---

### 6. 執行命令

**端點**: `POST /api/cmd`

**功能**: 在指定目錄中執行 Shell 命令

**請求體**:
```json
{
  "command": "ls -la",
  "cwd": "."
}
```

| 欄位名稱 | 類型 | 必填 | 預設值 | 說明 |
|---------|------|------|--------|------|
| command | string | 是 | - | 要執行的命令 |
| cwd | string | 否 | "." | 命令執行的工作目錄 |

**回應範例**:
```json
{
  "stdout": "total 20\ndrwxr-xr-x 2 user user 4096 Jan 1 00:00 .\n",
  "stderr": "",
  "returncode": 0
}
```

---

### 7. 獲取 Web GUI

**端點**: `GET /docs/gui`

**功能**: 返回內建的 Web IDE 界面（HTML + JavaScript）

**回應**: 完整的 HTML 頁面，包含：
- 文件瀏覽器（側邊欄）
- 代碼編輯器（主區域）
- 終端模擬器（底部）

## 使用 Web IDE 界面

1. 啟動服務後，訪問 http://127.0.0.1:8000/docs/gui
2. **雙擊文件**：在側邊欄雙擊文件以打開編輯
3. **雙擊文件夾**：進入該目錄
4. **創建檔案/資料夾**：點擊對應按鈕
5. **儲存檔案**：編輯後點擊「儲存當前檔案」按鈕
6. **終端**：在底部輸入框輸入命令並按 Enter 執行

## 安全注意事項

⚠️ **警告**: 此服務包含執行任意命令的功能，請僅在可信賴的環境中使用。

- 避免在公共網絡上暴露此服務
- 執行命令的功能可能帶來安全風險
- 建議搭配身份驗證機制使用

## 技術棧

- **框架**: FastAPI
- **伺服器**: Uvicorn
- **數據驗證**: Pydantic
- **前端**: 原生 HTML/CSS/JavaScript
