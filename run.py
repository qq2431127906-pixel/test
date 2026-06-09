import os, sys, subprocess, time, threading, webbrowser, shutil
from dotenv import load_dotenv

_app_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
load_dotenv(os.path.join(_app_dir, ".env"))

HOST = "127.0.0.1"
PORT = 8501

# 彻底禁止 Streamlit 开浏览器（环境变量比命令行更可靠）
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ["STREAMLIT_SERVER_PORT"] = str(PORT)
os.environ["STREAMLIT_SERVER_ADDRESS"] = HOST


def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(_app_dir, relative_path)


def main():
    # 首次运行：创建 .env
    env_path = os.path.join(_app_dir, ".env")
    if not os.path.exists(env_path):
        example = resource_path(".env.example")
        if os.path.exists(example):
            shutil.copy(example, env_path)
            print("已创建 .env，请在记事本填入 DashScope API Key")
            print(f"文件: {env_path}")
            print("获取: https://dashscope.console.aliyun.com/apiKey")
            if sys.platform == "win32":
                os.startfile(env_path)
        print("\n填好 Key 后，重新双击 run.exe 启动")
        input()
        return

    app_path = resource_path("app.py")

    # 子进程启动 Streamlit
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.port", str(PORT),
            "--server.address", HOST,
            "--server.headless", "true",
            "--server.fileWatcherType", "none",
            "--browser.gatherUsageStats", "false",
            "--global.developmentMode", "false",
        ],
        env=os.environ.copy(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # 单次打开浏览器（3 秒延迟等服务器就绪）
    def _open():
        time.sleep(3)
        webbrowser.open(f"http://{HOST}:{PORT}")
    threading.Thread(target=_open, daemon=True).start()

    print(f"\n  学术论文辅助写作智能体 已启动")
    print(f"  浏览器访问: http://{HOST}:{PORT}")
    print(f"  关闭此窗口即可停止\n")

    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()


if __name__ == "__main__":
    main()
