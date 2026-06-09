# build_release.py — 打包发布（写入说明 + ZIP）
import sys, os, shutil
sys.stdout.reconfigure(encoding='utf-8', errors='replace') if hasattr(sys.stdout, 'reconfigure') else None

version = sys.argv[1]
src = "dist\\assistant"
name = f"学术论文辅助写作_v{version}"

# 使用说明
readme = f"""学术论文辅助写作智能体 v{version}
================================

【安装步骤】（30 秒搞定）
1. 解压 ZIP 到一个固定文件夹（不要直接在压缩包内运行）
2. 双击 assistant.exe 启动
3. 首次运行会自动弹出记事本，请在 .env 文件中填入 DashScope API Key
4. API Key 免费获取：https://dashscope.console.aliyun.com/apiKey
5. 保存 .env 后关闭记事本，重新双击 assistant.exe
6. 手动打开浏览器访问 http://127.0.0.1:8501 → 开始使用

【如果没有看到 assistant.exe】
请确认已完整解压 ZIP，并进入解压后的文件夹根目录。不要打开 _internal 文件夹里的文件。

【关闭方法】
关闭命令行窗口即可停止服务

【创建桌面快捷方式（可选）】
右键 assistant.exe → 发送到 → 桌面快捷方式

【注意事项】
- 不需要安装 Python，也不需要手动运行 pip
- .env 文件必须和 assistant.exe 在同一个文件夹
- 查重分析为语义判断，非知网/万方数据库级正式查重
- 公式识别需 API Key 有 qwen-vl-max 权限
"""
with open(os.path.join(src, "使用说明.txt"), "w", encoding="utf-8") as f:
    f.write(readme)
print("README written")

# ZIP
shutil.make_archive(name, 'zip', src)
mb = os.path.getsize(name + ".zip") / 1024 / 1024
print(f"CREATED: {name}.zip ({mb:.1f} MB)")
