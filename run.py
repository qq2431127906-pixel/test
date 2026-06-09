# run.py — 启动器（精简版，不开重复浏览器）
import os, sys, subprocess, time, threading, webbrowser
from dotenv import load_dotenv

_app_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
load_dotenv(os.path.join(_app_dir, ".env"))

APP_NAME = "学术论文辅助写作智能体"
HOST = "127.0.0.1"
PORT = 8501
_OPENED = False
_LOCK = threading.Lock()

def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(_app_dir, relative_path)

def open_browser_once():
    global _OPENED
    with _LOCK:
        if _OPENED:
            return
        _OPENED = True
    time.sleep(4)
    print("Opening browser...")
    webbrowser.open(f"http://{HOST}:{PORT}")

def main():
    env_path = os.path.join(_app_dir, ".env")
    if not os.path.exists(env_path):
        example = resource_path(".env.example")
        if os.path.exists(example):
            import shutil
            shutil.copy(example, env_path)
            print("已创建 .env 文件，请用记事本打开填入 DashScope API Key")
            print(f"文件位置: {env_path}")
            print("获取 Key: https://dashscope.console.aliyun.com/apiKey")
            if sys.platform == "win32":
                os.startfile(env_path)
        input("\n填好 Key 后保存文件，按回车重新启动...")
        sys.exit(0)

    app_path = resource_path("app.py")
    cmd = [
        sys.executable, "-m", "streamlit", "run", app_path,
        "--server.headless", "true",
        "--server.port", str(PORT),
        "--server.address", HOST,
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
        "--server.fileWatcherType", "none",
        "--browser.gatherUsageStats", "false",
        "--global.developmentMode", "false",
    ]

    threading.Thread(target=open_browser_once, daemon=True).start()

    proc = subprocess.Popen(cmd, text=True, encoding="utf-8", errors="replace",
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    print(f"\n{APP_NAME} 已启动")
    print(f"浏览器访问: http://{HOST}:{PORT}")
    print("关闭此窗口即可停止\n")

    try:
        for line in proc.stdout:
            print(line, end="")
    except KeyboardInterrupt:
        pass
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()
