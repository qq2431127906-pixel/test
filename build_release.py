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
1. 双击 run.exe 启动
2. 首次运行会自动弹出记事本，请在 .env 文件中填入 DashScope API Key
3. API Key 免费获取：https://dashscope.console.aliyun.com/apiKey
4. 保存 .env 后关闭记事本，重新双击 run.exe
5. 浏览器自动打开 http://127.0.0.1:8501 → 开始使用

【关闭方法】
关闭命令行窗口即可停止服务

【创建桌面快捷方式（可选）】
右键 run.exe → 发送到 → 桌面快捷方式

【注意事项】
- 首次运行文献模块会自动下载约 400MB 模型，请耐心等待
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
