import os, sys, shutil, webbrowser, subprocess
from dotenv import load_dotenv, dotenv_values

_app_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
load_dotenv(os.path.join(_app_dir, ".env"))


def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(_app_dir, relative_path)


def main():
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
        print("\n填好 Key 后，重新双击 assistant.exe 启动")
        input()
        return

    for k, v in dotenv_values(env_path).items():
        os.environ.setdefault(k, v)

    app_path = resource_path("app.py")

    frozen = getattr(sys, "frozen", False)
    python = os.path.join(sys._MEIPASS, "python.exe") if frozen else sys.executable

    cmd = [python, "-m", "streamlit", "run", app_path,
           "--server.port", "8501", "--server.address", "127.0.0.1",
           "--server.headless", "true", "--server.fileWatcherType", "none",
           "--browser.gatherUsageStats", "false"]

    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not frozen:
        webbrowser.open("http://127.0.0.1:8501")

    print(f"\n  学术论文辅助写作智能体 已启动")
    print(f"  请手动打开浏览器访问: http://127.0.0.1:8501")
    print(f"  关闭此窗口即可停止\n")

    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()


if __name__ == "__main__":
    main()
