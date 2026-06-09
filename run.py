# 学术论文辅助写作智能体
# 启动器 + 自动更新

import os
import sys
import json
import shutil
import subprocess
import time
import threading
import webbrowser
import urllib.request
import urllib.error

from dotenv import load_dotenv

# 加载 .env（应用目录下）
_app_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
load_dotenv(os.path.join(_app_dir, ".env"))


# ============================================================
# 配置
# ============================================================
GITHUB_REPO = os.getenv("UPDATE_REPO", "")  # 例如 "yourname/yourrepo"
APP_NAME = "学术论文辅助写作智能体"
HOST = "127.0.0.1"
PORT = 8501


# ============================================================
# 工具函数
# ============================================================
def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


def get_local_version():
    vpath = resource_path("version.txt")
    if os.path.exists(vpath):
        with open(vpath, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "0.0.0"


# ============================================================
# 自动更新
# ============================================================
def check_update():
    """后台线程：访问 GitHub Releases API，比对版本。有新版本则提示。"""
    local_ver = get_local_version()
    if not GITHUB_REPO:
        return  # 未配置仓库，跳过

    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    try:
        req = urllib.request.Request(api_url, headers={"User-Agent": APP_NAME})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
        remote_ver = data.get("tag_name", "").lstrip("v")
        if not remote_ver:
            return
        if remote_ver == local_ver:
            print(f"[更新] 已是最新版本 v{local_ver}")
            return

        # 有新版本
        assets = data.get("assets", [])
        download_url = ""
        for a in assets:
            name = a.get("name", "")
            if name.endswith(".exe") and "Setup" in name:
                download_url = a.get("browser_download_url", "")
                break
        if not download_url:
            download_url = data.get("html_url", "")

        print("=" * 60)
        print(f"  🆕 发现新版本 v{remote_ver}（当前：v{local_ver}）")
        if download_url:
            print(f"  下载地址：{download_url}")
        else:
            print(f"  查看：{data.get('html_url', '')}")
        print("=" * 60)
        print("")

    except urllib.error.HTTPError as e:
        if e.code == 403:
            print("[更新] GitHub API 限流，跳过更新检查")
        elif e.code == 404:
            print("[更新] 仓库未找到，请检查 UPDATE_REPO 环境变量")
        else:
            print(f"[更新] 检查失败：HTTP {e.code}")
    except Exception as e:
        print(f"[更新] 检查失败：{e}")


# ============================================================
# 主逻辑
# ============================================================
def main():
    # .env 检测
    app_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
    env_path = os.path.join(app_dir, ".env")
    if not os.path.exists(env_path):
        example_path = resource_path(".env.example")
        print("=" * 60)
        print("  首次运行！")
        print("  请先配置 DashScope API Key：")
        print("  1. 访问 https://dashscope.console.aliyun.com/apiKey 获取 Key")
        print("  2. 在应用目录下找到 .env.example，复制为 .env")
        print(f"  3. 用记事本打开 .env，将 Key 填入 DASHSCOPE_API_KEY=")
        print("=" * 60)
        if os.path.exists(example_path):
            shutil.copy(example_path, env_path)
            print(f"  已自动创建 .env 文件：{env_path}")
            if sys.platform == "win32":
                os.startfile(env_path)
        input("  按回车键退出...")
        sys.exit(1)

    # 后台更新检查（不自动打开浏览器）
    threading.Thread(target=check_update, daemon=True).start()

    # 启动 Streamlit
    app_path = resource_path("app.py")
    cmd = [
        sys.executable, "-m", "streamlit", "run", app_path,
        "--server.headless", "true",
        "--server.address", HOST,
        "--server.port", str(PORT),
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")

    print("=" * 60)
    print(f"  {APP_NAME} v{get_local_version()}")
    print(f"  浏览器打开: http://{HOST}:{PORT}")
    print("  关闭此窗口即可停止服务")
    print("=" * 60)

    # 3 秒后自动打开浏览器（只开一次）
    def _open():
        time.sleep(3)
        webbrowser.open(f"http://{HOST}:{PORT}")
    threading.Thread(target=_open, daemon=True).start()

    try:
        for line in proc.stdout:
            print(line, end="")
    except KeyboardInterrupt:
        print("\n正在关闭...")
    finally:
        proc.terminate()
        proc.wait()
        print("已停止")


if __name__ == "__main__":
    main()
