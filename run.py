# run.py — 启动器（单进程，直接调 streamlit）
import os, sys, shutil, webbrowser
from dotenv import load_dotenv

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
        print("\n填好 Key 后，重新双击 run.exe 启动")
        input()
        return

    # 显式注入环境变量（防止子模块 load_dotenv 路径不对）
    from dotenv import dotenv_values
    env_vars = dotenv_values(env_path)
    for k, v in env_vars.items():
        os.environ.setdefault(k, v)

    app_path = resource_path("app.py")
    sys.argv = [
        "streamlit", "run", app_path,
        "--server.port", "8501",
        "--server.address", "127.0.0.1",
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
        "--server.fileWatcherType", "none",
        "--browser.gatherUsageStats", "false",
    ]

    webbrowser.open("http://127.0.0.1:8501")

    from streamlit.web import cli as stcli
    stcli.main()


if __name__ == "__main__":
    main()
