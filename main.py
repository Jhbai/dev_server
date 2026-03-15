import asyncio
import json
import random
import os
import subprocess
import shutil
from datetime import datetime, timedelta
from fastapi import FastAPI, Query, HTTPException, Depends, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn

# 初始化 FastAPI 應用
app = FastAPI(title="Integrated Data Service")

# HTTP Basic 認證設定
security = HTTPBasic()

# 設定認證用戶名和密碼（建議使用環境變數）
USERNAME = os.environ.get("IDE_USERNAME", "admin")
PASSWORD = os.environ.get("IDE_PASSWORD", "password123")


# --- 認證函數 ---
def verify_credentials(credentials: HTTPBasicCredentials = Security(security)) -> str:
    """驗證用戶名和密碼"""
    if credentials.username != USERNAME or credentials.password != PASSWORD:
        raise HTTPException(
            status_code=401,
            detail="認證失敗",
            headers={"WWW-Authenticate": "Basic"}
        )
    return credentials.username


# --- 資料模型定義 ---
class FileRequest(BaseModel):
    path: str
    content: str = ""


class CmdRequest(BaseModel):
    command: str
    cwd: str = "."


# --- Web IDE API 端點實作 ---
@app.get("/api/list", tags=["system"])
def list_files(path: str = ".", user: str = Depends(verify_credentials)):
    """列出目錄內容"""
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Directory not found")
    try:
        items = os.listdir(path)
        result = []
        for item in items:
            full_path = os.path.join(path, item)
            result.append({
                "name": item,
                "is_dir": os.path.isdir(full_path),
                "path": full_path
            })
        return sorted(result, key=lambda x: (not x["is_dir"], x["name"]))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/read", tags=["system"])
def read_file(path: str, user: str = Depends(verify_credentials)):
    """讀取文件內容"""
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return {"content": f.read()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/write", tags=["system"])
def write_file(req: FileRequest, user: str = Depends(verify_credentials)):
    """寫入文件內容"""
    try:
        with open(req.path, "w", encoding="utf-8") as f:
            f.write(req.content)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/create_dir", tags=["system"])
def create_dir(req: FileRequest, user: str = Depends(verify_credentials)):
    """創建目錄"""
    try:
        os.makedirs(req.path, exist_ok=True)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/delete", tags=["system"])
def delete_file(path: str, user: str = Depends(verify_credentials)):
    """刪除文件或目錄"""
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cmd", tags=["system"])
def run_cmd(req: CmdRequest, user: str = Depends(verify_credentials)):
    """執行 Shell 命令"""
    try:
        result = subprocess.run(
            req.command, shell=True, cwd=req.cwd,
            capture_output=True, text=True
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- 前端 GUI 端點 ---
@app.get("/docs/gui", response_class=HTMLResponse, dependencies=[Depends(verify_credentials)])
def get_gui():
    html_content = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>Web IDE</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            display: flex;
            height: 100vh;
            background-color: #1e1e1e;
            color: #d4d4d4;
        }
        #sidebar {
            width: 250px;
            background-color: #252526;
            border-right: 1px solid #3c3c3c;
            display: flex;
            flex-direction: column;
        }
        #sidebar-header {
            padding: 10px;
            background-color: #333333;
            font-weight: bold;
            font-size: 14px;
        }
        #file-list {
            flex: 1;
            overflow-y: auto;
            list-style: none;
            padding: 0;
            margin: 0;
            font-size: 13px;
        }
        #file-list li {
            padding: 5px 10px;
            cursor: pointer;
            user-select: none;
        }
        #file-list li:hover {
            background-color: #37373d;
        }
        .is-dir::before {
            content: '📁 ';
        }
        .is-file::before {
            content: '📄 ';
        }
        #main {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        #toolbar {
            height: 40px;
            background-color: #333333;
            display: flex;
            align-items: center;
            padding: 0 10px;
            gap: 10px;
        }
        button {
            background-color: #0e639c;
            color: white;
            border: none;
            padding: 5px 10px;
            cursor: pointer;
            border-radius: 3px;
            font-size: 12px;
        }
        button:hover {
            background-color: #1177bb;
        }
        #editor-container {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        #editor {
            flex: 1;
            background-color: #1e1e1e;
            color: #d4d4d4;
            border: none;
            padding: 10px;
            font-family: monospace;
            font-size: 14px;
            resize: none;
            outline: none;
        }
        #terminal-container {
            height: 250px;
            background-color: #1e1e1e;
            border-top: 1px solid #3c3c3c;
            display: flex;
            flex-direction: column;
        }
        #terminal-output {
            flex: 1;
            padding: 10px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 13px;
            white-space: pre-wrap;
            margin: 0;
            color: #cccccc;
        }
        #terminal-input-container {
            display: flex;
            border-top: 1px solid #3c3c3c;
        }
        #terminal-prompt {
            padding: 5px 10px;
            background-color: #252526;
            font-family: monospace;
        }
        #terminal-input {
            flex: 1;
            background-color: #1e1e1e;
            color: #d4d4d4;
            border: none;
            padding: 5px;
            font-family: monospace;
            outline: none;
        }
    </style>
</head>
<body>
    <div id="sidebar">
        <div id="sidebar-header">目錄：<span id="current-path">.</span></div>
        <ul id="file-list"></ul>
    </div>
    <div id="main">
        <div id="toolbar">
            <button onclick="createFile()">創建檔案</button>
            <button onclick="createDir()">創建資料夾</button>
            <button onclick="saveFile()" style="margin-left: auto; background-color: #238636;">儲存當前檔案</button>
            <button onclick="deleteCurrent()" style="background-color: #da3633;">刪除選定項目</button>
        </div>
        <div id="editor-container">
            <div style="padding: 5px 10px; background-color: #2d2d2d; font-size: 12px;">當前編輯：<span id="active-file">無</span></div>
            <textarea id="editor" spellcheck="false" placeholder="請雙擊左側檔案開始編輯..."></textarea>
        </div>
        <div id="terminal-container">
            <pre id="terminal-output"></pre>
            <div id="terminal-input-container">
                <span id="terminal-prompt">></span>
                <input type="text" id="terminal-input" placeholder="輸入 shell 參數並按 Enter...">
            </div>
        </div>
    </div>
    <script>
        let currentPath = ".";
        let activeFilePath = null;

        async function loadFiles(path) {
            const res = await fetch(`/api/list?path=${encodeURIComponent(path)}`);
            if (res.ok) {
                currentPath = path;
                document.getElementById('current-path').innerText = currentPath;
                const files = await res.json();
                const list = document.getElementById('file-list');
                list.innerHTML = '';

                // Add parent directory option
                if (currentPath !== "." && currentPath !== "/") {
                    const li = document.createElement('li');
                    li.className = 'is-dir';
                    li.innerText = '..';
                    li.ondblclick = () => {
                        const parentPath = currentPath.substring(0, currentPath.lastIndexOf('/')) || '.';
                        loadFiles(parentPath);
                    };
                    list.appendChild(li);
                }

                files.forEach(f => {
                    const li = document.createElement('li');
                    li.className = f.is_dir ? 'is-dir' : 'is-file';
                    li.innerText = f.name;
                    li.ondblclick = () => {
                        if (f.is_dir) {
                            loadFiles(f.path.replace(/\\\\/g, '/'));
                        } else {
                            openFile(f.path.replace(/\\\\/g, '/'));
                        }
                    };
                    list.appendChild(li);
                });
            } else {
                alert('無法讀取目錄');
            }
        }

        async function openFile(path) {
            const res = await fetch(`/api/read?path=${encodeURIComponent(path)}`);
            if (res.ok) {
                const data = await res.json();
                document.getElementById('editor').value = data.content;
                activeFilePath = path;
                document.getElementById('active-file').innerText = path;
            } else {
                alert('無法讀取檔案');
            }
        }

        async function saveFile() {
            if (!activeFilePath) return alert('沒有開啟的檔案');
            const content = document.getElementById('editor').value;
            const res = await fetch('/api/write', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({path: activeFilePath, content: content})
            });
            if (res.ok) alert('儲存成功');
            else alert('儲存失敗');
        }

        async function createFile() {
            const name = prompt('請輸入新檔案名稱:');
            if (!name) return;
            const path = currentPath === "." ? name : `${currentPath}/${name}`;
            await fetch('/api/write', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({path: path, content: ''})
            });
            loadFiles(currentPath);
        }

        async function createDir() {
            const name = prompt('請輸入新資料夾名稱:');
            if (!name) return;
            const path = currentPath === "." ? name : `${currentPath}/${name}`;
            await fetch('/api/create_dir', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({path: path})
            });
            loadFiles(currentPath);
        }

        async function deleteCurrent() {
            const target = prompt(`請輸入要刪除的完整路徑 (當前目錄為 ${currentPath}):`);
            if (!target) return;
            if (confirm(`確定要刪除 ${target} 嗎？`)) {
                await fetch(`/api/delete?path=${encodeURIComponent(target)}`, {
                    method: 'DELETE'
                });
                loadFiles(currentPath);
                if (target === activeFilePath) {
                    document.getElementById('editor').value = '';
                    activeFilePath = null;
                    document.getElementById('active-file').innerText = '無';
                }
            }
        }

        document.getElementById('terminal-input').addEventListener('keypress', async function (e) {
            if (e.key === 'Enter') {
                const cmd = this.value;
                this.value = '';
                const outputBox = document.getElementById('terminal-output');
                outputBox.innerText += `\\n${currentPath}> ${cmd}\\n`;
                const res = await fetch('/api/cmd', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({command: cmd, cwd: currentPath})
                });
                if (res.ok) {
                    const data = await res.json();
                    if (data.stdout) outputBox.innerText += data.stdout;
                    if (data.stderr) outputBox.innerText += data.stderr;
                } else {
                    outputBox.innerText += '命令執行失敗\\n';
                }
                outputBox.scrollTop = outputBox.scrollHeight;
            }
        });

        // 初始化載入
        loadFiles(currentPath);
    </script>
</body>
</html>
"""
    return html_content


# --- 數據流圖表功能 ---
# HTML 與 JavaScript 前端整合碼
chart_html_content = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>Time Series Stream Chart</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            padding: 20px; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            background-attachment: fixed;
            color: #e0e0e0;
            min-height: 100vh;
            margin: 0;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: rgba(30, 30, 46, 0.8);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
        }
        
        h1 {
            text-align: center;
            color: #64b5f6;
            margin-top: 0;
            text-shadow: 0 0 10px rgba(100, 181, 246, 0.3);
            font-weight: 300;
        }
        
        .controls { 
            margin-bottom: 25px; 
            display: flex; 
            gap: 15px; 
            flex-wrap: wrap;
            background: rgba(25, 25, 35, 0.7);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid rgba(100, 181, 246, 0.2);
        }
        
        input { 
            padding: 10px 15px; 
            width: 220px; 
            border: 1px solid #4a4a6a;
            border-radius: 8px;
            background-color: #1e1e2e;
            color: #e0e0e0;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        input:focus {
            outline: none;
            border-color: #64b5f6;
            box-shadow: 0 0 8px rgba(100, 181, 246, 0.4);
        }
        
        button { 
            padding: 10px 20px; 
            cursor: pointer;
            background: linear-gradient(135deg, #64b5f6 0%, #2196f3 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(33, 150, 243, 0.2);
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(33, 150, 243, 0.4);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .chart-box { 
            width: 100%; 
            max-width: 100%; 
            height: 500px; 
            border: 1px solid rgba(100, 181, 246, 0.3);
            padding: 15px; 
            border-radius: 12px;
            background-color: rgba(25, 25, 35, 0.7);
            box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.3);
        }
        
        .chart-container {
            position: relative;
            height: 100%;
        }
    </style>
</head>
<body>
    <div class="controls">
        <input type="text" id="dataNames" placeholder="dataName (ex: A,B,C)" value="Sensor1,Sensor2">
        <input type="text" id="start" placeholder="YYYY-MM-DD HH:MM:SS" value="2026-03-15 00:00:00">
        <input type="text" id="end" placeholder="YYYY-MM-DD HH:MM:SS" value="2026-03-15 05:00:00">
        <button onclick="startStream()">開始繪圖</button>
    </div>
    
    <div class="chart-box">
        <canvas id="myChart"></canvas>
    </div>

    <script>
        let chart;
        const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'];

        async function startStream() {
            const dataNames = document.getElementById('dataNames').value;
            const start = document.getElementById('start').value;
            const end = document.getElementById('end').value;
            
            // 初始化或重置圖表
            if(chart) chart.destroy();
            const ctx = document.getElementById('myChart').getContext('2d');
            chart = new Chart(ctx, {
                type: 'line',
                data: { labels: [], datasets: [] },
                options: { 
                    animation: false, // 關閉動畫以利串流效能
                    responsive: true,
                    maintainAspectRatio: false
                }
            });

            const datasetMap = {};
            let colorIdx = 0;

            const url = `/api/data?dataNames=${encodeURIComponent(dataNames)}&start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`;
            
            try {
                const response = await fetch(url);
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = "";

                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;
                    
                    buffer += decoder.decode(value, { stream: true });
                    const parts = buffer.split('\\n');
                    buffer = parts.pop(); // 保留不完整的 JSON 字串等待下一次讀取

                    let timeSet = new Set(chart.data.labels);

                    for (const part of parts) {
                        if (!part.trim()) continue;
                        const dataBatch = JSON.parse(part);
                        
                        dataBatch.forEach(point => {
                            // 處理 X 軸時間標籤
                            if (!timeSet.has(point.dateTime)) {
                                chart.data.labels.push(point.dateTime);
                                timeSet.add(point.dateTime);
                            }
                            
                            // 處理 Y 軸資料集
                            if (!datasetMap[point.dataName]) {
                                datasetMap[point.dataName] = {
                                    label: point.dataName,
                                    data: [],
                                    borderColor: colors[colorIdx++ % colors.length],
                                    fill: false,
                                    tension: 0.1
                                };
                                chart.data.datasets.push(datasetMap[point.dataName]);
                            }
                            datasetMap[point.dataName].data.push(point.value);
                        });
                    }
                    chart.update(); // 每一批資料載入後更新一次圖表
                }
            } catch (e) {
                console.error("Stream error:", e);
            }
        }
    </script>
</body>
</html>
"""

@app.get("/docs/chart", response_class=HTMLResponse)
async def get_chart_page(user: str = Depends(verify_credentials)):
    return chart_html_content

async def data_generator(data_names: list, start_dt: datetime, end_dt: datetime):
    current_dt = start_dt
    while current_dt < end_dt:
        batch = []
        # 一次生成一小時 (60個點) 的資料
        for i in range(60):
            point_time = current_dt + timedelta(minutes=i)
            if point_time >= end_dt:
                break
            for name in data_names:
                batch.append({
                    "dataName": name,
                    "value": round(random.uniform(10, 100), 2),  # 模擬真實數值
                    "dateTime": point_time.strftime("%Y-%m-%d %H:%M:%S")
                })
        
        # 轉為 JSON 字串並加上換行符號 (NDJSON 格式)
        yield json.dumps(batch) + "\n"
        
        current_dt += timedelta(hours=1)
        # 模擬 I/O 延遲，讓前端肉眼能看出逐步畫圖的效果
        await asyncio.sleep(0.5)

@app.get("/api/data", tags=["system"])
async def stream_data(
    dataNames: str = Query(..., description="以逗號分隔的 dataName"),
    start: str = Query(..., description="起始時間 YYYY-MM-DD HH:MM:SS"),
    end: str = Query(..., description="結束時間 YYYY-MM-DD HH:MM:SS"),
    user: str = Depends(verify_credentials)
):
    names_list = [name.strip() for name in dataNames.split(",")]
    start_dt = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
    end_dt = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
    
    # 採用 NDJSON 格式進行串流
    return StreamingResponse(
        data_generator(names_list, start_dt, end_dt), 
        media_type="application/x-ndjson"
    )

if __name__ == "__main__":
    # 預設啟動在 port 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)
