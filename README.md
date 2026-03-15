# Integrated Data Service

這是一個整合型的數據服務系統，包含 Web IDE 和即時數據流圖表功能。

## 功能特色

### 1. Web IDE (整合式網頁開發環境)
- 瀏覽伺服器上的檔案系統
- 建立、讀取、寫入、刪除檔案與資料夾
- 內建文字編輯器
- 終端機模擬器，可執行 Shell 命令

### 2. 即時數據流圖表
- 顯示時間序列數據的互動式圖表
- 支援多組數據同時顯示
- 即時數據串流處理

## 技術架構

### 後端技術
- Python 3.x
- FastAPI (高效能 Web 框架)
- Uvicorn (ASGI 伺服器)
- Pydantic (數據驗證)

### 前端技術
- HTML5/CSS3/JavaScript
- Chart.js (圖表繪製)

### 安全性
- HTTP Basic 認證
- 環境變數配置認證資訊

## 安裝與設定

### 環境需求
- Python 3.7+
- pip (Python 套件管理工具)

### 安裝步驟

1. 克隆專案或下載原始碼
2. 安裝依賴套件：
```bash
pip install fastapi uvicorn python-multipart
```

### 環境變數設定

| 變數名稱 | 預設值 | 說明 |
|---------|--------|------|
| `IDE_USERNAME` | `admin` | Web IDE 登入帳號 |
| `IDE_PASSWORD` | `password123` | Web IDE 登入密碼 |

設定環境變數範例：
```bash
export IDE_USERNAME=myuser
export IDE_PASSWORD=mypassword
```

## 使用方法

### 啟動服務

#### 主服務 (整合所有功能)
```bash
python main.py
```

#### 僅啟動數據流圖表服務
```bash
python data_server.py
```

#### 僅啟動 Web IDE 服務
```bash
python dev_server.py
```

預設啟動在 `http://127.0.0.1:8000`

### Web IDE 使用

1. 瀏覽至 `http://127.0.0.1:8000/docs/gui`
2. 使用設定的帳號密碼登入
3. 功能操作：
   - 左側為檔案瀏覽器，雙擊資料夾可進入，雙擊檔案可編輯
   - 上方工具列可建立檔案/資料夾、儲存、刪除
   - 下方終端機可執行命令

### 數據流圖表使用

1. 瀏覽至 `http://127.0.0.1:8000/docs/chart`
2. 輸入參數：
   - `dataNames`: 資料名稱，多個以逗號分隔 (如: Sensor1,Sensor2)
   - `start`: 起始時間 (格式: YYYY-MM-DD HH:MM:SS)
   - `end`: 結束時間 (格式: YYYY-MM-DD HH:MM:SS)
3. 點擊「開始繪圖」即可顯示圖表

## API 端點說明

### Web IDE API

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/api/list` | 列出目錄內容 |
| GET | `/api/read` | 讀取檔案內容 |
| POST | `/api/write` | 寫入檔案內容 |
| POST | `/api/create_dir` | 建立資料夾 |
| DELETE | `/api/delete` | 刪除檔案或資料夾 |
| POST | `/api/cmd` | 執行 Shell 命令 |

### 數據流圖表 API

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/api/data` | 取得時間序列數據 (支援串流) |

### 文件與介面

| 路徑 | 說明 |
|------|------|
| `/docs/gui` | Web IDE 介面 |
| `/docs/chart` | 數據流圖表介面 |
| `/docs` | FastAPI 自動生成的 API 文件 |

## 安全注意事項

1. 預設認證資訊非常弱，請務必在生產環境中更改
2. 建議透過 HTTPS 提供服務
3. 不要在公開網路環境中暴露此服務
4. 建議在防火牆層限制存取來源

## 專案結構

```
.
├── main.py          # 整合型主服務
├── data_server.py   # 數據流圖表服務
├── dev_server.py    # Web IDE 服務
└── README.md        # 此文件
```
