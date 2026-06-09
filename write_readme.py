# write_readme.py — 生成使用说明
import sys, os

# GitHub Actions Windows 终端编码修复
sys.stdout.reconfigure(encoding='utf-8', errors='replace') if hasattr(sys.stdout, 'reconfigure') else None

version = sys.argv[1]
dist = sys.argv[2]

readme = f"""学术论文辅助写作智能体 v{version}

【使用方法】
1. 双击 run.exe 启动
2. 首次运行会自动创建 .env 并弹出记事本，请填入 DashScope API Key
3. API Key 获取：https://dashscope.console.aliyun.com/apiKey
4. 浏览器自动打开 http://127.0.0.1:8501

【关闭方法】关闭命令行窗口即可停止
【注意】首次文献模块运行需下载约 400MB 模型
"""
with open(os.path.join(dist, "使用说明.txt"), "w", encoding="utf-8") as f:
    f.write(readme)
print("README written to dist")
