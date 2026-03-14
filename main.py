import os
import subprocess
import shutil
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

# 初始化 FastAPI 應用
app = FastAPI(title="Web IDE API")

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


# --- API 端點實作 ---
@app.get("/api/list")
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


@app.get("/api/read")
def read_file(path: str, user: str = Depends(verify_credentials)):
    """讀取文件內容"""
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return {"content": f.read()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/write")
def write_file(req: FileRequest, user: str = Depends(verify_credentials)):
    """寫入文件內容"""
    try:
        with open(req.path, "w", encoding="utf-8") as f:
            f.write(req.content)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/create_dir")
def create_dir(req: FileRequest, user: str = Depends(verify_credentials)):
    """創建目錄"""
    try:
        os.makedirs(req.path, exist_ok=True)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/delete")
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


@app.post("/api/cmd")
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


if __name__ == "__main__":
    # 預設啟動在 port 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)
