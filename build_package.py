# build_package.py — CI 打包脚本
# 由 GitHub Actions 调用：python build_package.py <version> <dist_dir>
import os, sys, subprocess

version = sys.argv[1]
dist = sys.argv[2]  # e.g. "dist\\assistant"

# --- 使用说明 ---
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

# --- NSIS 脚本 ---
app = "学术论文辅助写作智能体"
nsi = f'''Unicode true
!define APP_NAME "{app}"
!define APP_EXE "run.exe"
!define VERSION "{version}"
!define PUBLISHER "Academic Assistant"

Name "${{APP_NAME}}"
OutFile "{app}_Setup_v${{VERSION}}.exe"
InstallDir "$PROGRAMFILES\\${{APP_NAME}}"
RequestExecutionLevel admin
InstallDirRegKey HKLM "Software\\${{APP_NAME}}" "InstallDir"

Page directory
Page instfiles

Section "Install"
  SetOutPath $INSTDIR
  File /r "{dist}\\*.*"
  WriteRegStr HKLM "Software\\${{APP_NAME}}" "InstallDir" "$INSTDIR"
  WriteRegStr HKLM "Software\\${{APP_NAME}}" "Version" "${{VERSION}}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayName" "${{APP_NAME}}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "UninstallString" '"$INSTDIR\\uninstall.exe"'
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayVersion" "${{VERSION}}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "Publisher" "${{PUBLISHER}}"
  WriteUninstaller "$INSTDIR\\uninstall.exe"
  CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}" "" "$INSTDIR\\${{APP_EXE}}" 0
  CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
  CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}" "" "$INSTDIR\\${{APP_EXE}}" 0
  CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\卸载.lnk" "$INSTDIR\\uninstall.exe"
SectionEnd

Section "Uninstall"
  RMDir /r "$INSTDIR\\_internal"
  RMDir /r "$INSTDIR\\paste_image_component"
  RMDir /r "$INSTDIR\\drawing_component"
  Delete "$INSTDIR\\*.*"
  RMDir "$INSTDIR"
  Delete "$DESKTOP\\${{APP_NAME}}.lnk"
  RMDir /r "$SMPROGRAMS\\${{APP_NAME}}"
  DeleteRegKey HKLM "Software\\${{APP_NAME}}"
  DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}"
SectionEnd
'''
with open("installer.nsi", "w", encoding="utf-8") as f:
    f.write(nsi)
print(f"NSIS script written ({len(nsi)} chars)")

# --- 运行 NSIS ---
makensis = os.environ.get("MAKENSIS", ".\\nsis\\makensis.exe")
result = subprocess.run([makensis, "installer.nsi"], capture_output=True, text=True, encoding="utf-8", errors="replace")
# 只打结果行（英文），避免 Windows 终端编码问题
for line in result.stdout.replace('\r', '').split('\n'):
    if not line.strip():
        continue
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode('ascii', errors='replace').decode())
print(f"NSIS exit code: {result.returncode}")
if result.returncode != 0:
    try:
        print("NSIS ERROR:", result.stderr)
    except UnicodeEncodeError:
        pass
    # fallback: zip
    print("Falling back to ZIP...")
    import zipfile
    zip_name = f"学术论文辅助写作_v{version}.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(dist):
            for file in files:
                zf.write(os.path.join(root, file),
                         os.path.relpath(os.path.join(root, file), dist))
    mb = os.path.getsize(zip_name) / 1024 / 1024
    print(f"CREATED: {zip_name} ({mb:.1f} MB)")
    sys.exit(0)

# List ALL exe files in workspace
print("All .exe files in workspace:")
for f in os.listdir("."):
    if f.endswith(".exe"):
        print(f"  {f} ({os.path.getsize(f)} bytes)")

found = False
for f in os.listdir("."):
    if f.endswith(".exe") and "Setup" in f:
        mb = os.path.getsize(f) / 1024 / 1024
        print(f"CREATED: {f} ({mb:.1f} MB)")
        found = True

if not found:
    print("No Setup.exe found. Falling back to ZIP...")
    import zipfile
    zip_name = f"学术论文辅助写作_v{version}.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(dist):
            for file in files:
                zf.write(os.path.join(root, file),
                         os.path.relpath(os.path.join(root, file), dist))
    mb = os.path.getsize(zip_name) / 1024 / 1024
    print(f"CREATED: {zip_name} ({mb:.1f} MB)")
