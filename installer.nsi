; 学术论文辅助写作智能体 — NSIS 安装脚本
; 将 PyInstaller --onedir 产物打包为单个 Setup.exe

Unicode true
!define APP_NAME "学术论文辅助写作智能体"
!define APP_EXE "run.exe"
!define VERSION "1.0.0"
!define PUBLISHER "Academic Writing Assistant"

Name "${APP_NAME}"
OutFile "${APP_NAME}_Setup_v${VERSION}.exe"
InstallDir "$PROGRAMFILES\${APP_NAME}"
RequestExecutionLevel admin

; 默认安装目录也支持用户自选
InstallDirRegKey HKLM "Software\${APP_NAME}" "InstallDir"

; ----- 页面 -----
Page directory
Page instfiles

; ----- 安装 -----
Section "Install"
  SetOutPath $INSTDIR

  ; 复制所有文件
  File /r "dist\学术论文辅助写作\*.*"

  ; 写入注册表
  WriteRegStr HKLM "Software\${APP_NAME}" "InstallDir" "$INSTDIR"
  WriteRegStr HKLM "Software\${APP_NAME}" "Version" "${VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${PUBLISHER}"

  ; 创建卸载程序
  WriteUninstaller "$INSTDIR\uninstall.exe"

  ; 桌面快捷方式
  CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0

  ; 开始菜单
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\卸载.lnk" "$INSTDIR\uninstall.exe"
SectionEnd

; ----- 卸载 -----
Section "Uninstall"
  Delete "$INSTDIR\*.*"
  RMDir /r "$INSTDIR\_internal"
  RMDir /r "$INSTDIR\paste_image_component"
  RMDir /r "$INSTDIR\drawing_component"
  Delete "$DESKTOP\${APP_NAME}.lnk"
  RMDir /r "$SMPROGRAMS\${APP_NAME}"
  DeleteRegKey HKLM "Software\${APP_NAME}"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
  RMDir "$INSTDIR"
SectionEnd
