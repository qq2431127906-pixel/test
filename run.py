# run.py — 极简启动器
import os, sys, subprocess
from dotenv import load_dotenv

_app_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
load_dotenv(os.path.join(_app_dir, ".env"))

HOST = "127.0.0.1"
PORT = 8501

def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(_app_dir, relative_path)

def main():
    env_path = os.path.join(_app_dir, ".env")
    if not os.path.exists(env_path):
        example = resource_path(".env.example")
        if os.path.exists(example):
            import shutil
            shutil.copy(example, env_path)
            print("已创建 .env，请在记事本填入 DashScope API Key")
            print(f"文件: {env_path}")
            print("获取: https://dashscope.console.aliyun.com/apiKey")
            if sys.platform == "win32":
                os.startfile(env_path)
        print("\n填好 Key 后，重新双击 run.exe 启动")
        input()
        sys.exit(0)

    app_path = resource_path("app.py")

    # --server.headless true 禁止 Streamlit 自己开浏览器
    # --server.fileWatcherType none 禁止热重载
    proc = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", app_path,
        "--server.headless", "true",
        "--server.port", str(PORT),
        "--server.address", HOST,
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
        "--server.fileWatcherType", "none",
        "--browser.gatherUsageStats", "false",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    import webbrowser
    webbrowser.open(f"http://{HOST}:{PORT}")

    print(f"\n  学术论文辅助写作智能体 已启动")
    print(f"  浏览器访问: http://{HOST}:{PORT}")
    print(f"  关闭此窗口即可停止\n")

    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()
