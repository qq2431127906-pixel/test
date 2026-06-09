# 学术论文辅助写作智能体

基于通义千问大模型的学术写作辅助工具，六大功能模块 + iOS 液态玻璃界面 + 自动更新。

## 快速开始（方式一：源码运行）

### 环境要求
- Python 3.9+
- Windows / macOS / Linux

### 安装

```bash
git clone <你的仓库地址>
cd 学术论文辅助写作智能体
python -m venv venv
# Windows: venv\Scripts\activate   macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env，填入 DashScope API Key（https://dashscope.console.aliyun.com/apiKey）
streamlit run app.py
```

浏览器自动打开 `http://localhost:8501`。

---

## 快速开始（方式二：桌面安装包 .exe）

### 下载

从 [GitHub Releases](../../releases) 下载最新 `学术论文辅助写作智能体_Setup_vX.X.X.exe`。

### 安装

1. 双击 Setup.exe → 安装到默认路径
2. 桌面出现快捷方式
3. 双击快捷方式 → 浏览器自动弹出
4. 首次运行会自动创建 `.env`，用记事本填入 API Key 后重启即可

**不需要装 Python、不需要 pip、不需要配环境。**

### 自动更新

启动时自动检查 GitHub Releases，有新版本时弹出下载链接。  
需要在 `.env` 中配置：
```
UPDATE_REPO=你的GitHub用户名/仓库名
```

---

## 方式三：CI/CD 自动打包

推送 tag 即可触发 GitHub Actions 自动打包 + 发布：

```bash
git tag v1.0.1
git push origin v1.0.1
```

5 分钟后，Releases 页面出现新的 Setup.exe。

### 首次配置 GitHub Actions

1. Fork 此仓库
2. 在仓库 Settings → Actions → General → 允许 Actions
3. 推送代码 + tag 即可

---

## 功能模块

| 功能 | 说明 |
|---|---|
| 📑 文献摘要梳理 | 上传 PDF/DOCX，逐篇结构化摘要 + 综合研究脉络/对比/热点/大纲 |
| 📝 论文框架生成 | 题目/学科/类型 → 完整章节框架、写作要点、进度建议 |
| ✍️ 论文内容润色 | 粘贴/上传文档，三档润色，输出修改说明与替换建议 |
| 📐 格式校对 | GB/T 7714 参考文献生成；Word 标题/图表/公式编号检查 |
| ⚠️ 查重分析提醒 | 语义风险分析，风险等级/高风险句/降重策略/改写示例 |
| 🧮 公式识别与转换 | 截图粘贴/文件上传/手写板，一键复制 LaTeX/MathML |

## 技术栈

- **UI**：Streamlit + iOS 液态玻璃自定义主题
- **大模型**：通义千问（DashScope）qwen-turbo / qwen-vl-max
- **文档处理**：python-docx / pdfplumber / pypdf
- **打包**：PyInstaller + NSIS + GitHub Actions

## 注意事项

- 查重分析为语义相似度判断，不是知网/万方数据库级正式查重
- 公式识别需确保 API Key 有 qwen-vl-max 权限
- 首次运行文献模块会自动下载 HuggingFace Embedding 模型（约 400MB）
- 打包体积约 350MB（含 Python 运行时 + 全部依赖）
