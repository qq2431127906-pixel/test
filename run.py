# 学术论文辅助写作智能体
# PyInstaller 启动脚本 — 双击 .exe 后自动启动 Streamlit 并打开浏览器

import os
import sys
import subprocess
import time
import threading
import webbrowser


def resource_path(relative_path):
    """获取打包后资源文件的路径（PyInstaller _MEIPASS 兼容）"""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


def main():
    # 确保 .env 文件存在
    env_path = resource_path(".env")
    if not os.path.exists(env_path):
        # 检查同目录下的 .env.example，提示用户改名
        example_path = resource_path(".env.example")
        if os.path.exists(example_path):
            print("=" * 60)
            print("  首次运行！请将 .env.example 复制为 .env 并填入 API Key")
            print("  获取 DashScope API Key: https://dashscope.console.aliyun.com/apiKey")
            print("=" * 60)
            # 在 Windows 上用记事本打开 .env.example
            if sys.platform == "win32":
                os.startfile(example_path)
        else:
            print("错误：找不到 .env 文件，请设置环境变量 DASHSCOPE_API_KEY")
        input("按回车键退出...")
        sys.exit(1)

    # Streamlit 启动参数
    app_path = resource_path("app.py")
    host = "127.0.0.1"
    port = 8501

    cmd = [
        sys.executable, "-m", "streamlit", "run",
        app_path,
        "--server.headless", "true",
        "--server.address", host,
        "--server.port", str(port),
        "--browser.serverAddress", f"{host}:{port}",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
    ]

    # 启动 Streamlit
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    # 等 Streamlit 启动后自动打开浏览器
    def open_browser():
        time.sleep(3)
        webbrowser.open(f"http://{host}:{port}")

    threading.Thread(target=open_browser, daemon=True).start()

    print("=" * 60)
    print("  学术论文辅助写作智能体 已启动")
    print(f"  浏览器中打开: http://{host}:{port}")
    print("  关闭此窗口即可停止服务")
    print("=" * 60)

    # 打印 Streamlit 输出直到退出
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
