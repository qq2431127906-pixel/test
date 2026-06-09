# 学术论文辅助写作智能体

基于通义千问大模型的学术写作辅助工具，提供文献摘要梳理、论文框架生成、内容润色、格式校对、查重分析、公式识别六大功能。

## 快速开始（方式一：源码运行）

### 环境要求
- Python 3.9+
- Windows / macOS / Linux

### 安装步骤

```bash
# 1. 克隆仓库
git clone <你的仓库地址>
cd 学术论文辅助写作智能体

# 2. 创建虚拟环境（推荐）
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置 API Key
cp .env.example .env
# 编辑 .env 文件，填入你的 DashScope API Key
# 获取地址：https://dashscope.console.aliyun.com/apiKey

# 5. 启动
streamlit run app.py
```

浏览器自动打开 `http://localhost:8501`。

## 快速开始（方式二：桌面应用）

### 打包为 .exe

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包
pyinstaller --onedir --name "学术论文辅助写作" `
    --add-data "app.py;." `
    --add-data "literature_module.py;." `
    --add-data "outline_module.py;." `
    --add-data "polish_module.py;." `
    --add-data "plagiarism_module.py;." `
    --add-data "format_module.py;." `
    --add-data "formula_module.py;." `
    --add-data "shared_utils.py;." `
    --add-data "ui_theme.py;." `
    --add-data "prompt_templates.py;." `
    --add-data "paste_image_component;paste_image_component" `
    --add-data "drawing_component;drawing_component" `
    --add-data ".env.example;." `
    --console `
    run.py
```

打包完成后，将 `.env.example` 复制为 `.env` 并填入 API Key，放入 `dist/学术论文辅助写作/` 目录中，双击 `run.exe` 即可启动。

## 功能模块

| 功能 | 说明 |
|---|---|
| 📑 文献摘要梳理 | 上传 PDF/DOCX，逐篇生成结构化摘要 + 综合研究脉络/对比/热点/大纲 |
| 📝 论文框架生成 | 基于题目/学科/类型生成完整章节框架、写作要点、进度建议 |
| ✍️ 论文内容润色 | 粘贴或上传文档，轻度/标准/深度三档润色，输出修改说明与替换建议 |
| 📐 格式校对 | 自动生成 GB/T 7714 参考文献；检查 Word 标题层级/图表编号/公式编号 |
| ⚠️ 查重分析提醒 | 语义风险分析，输出风险等级/高风险句/降重策略/改写示例 |
| 🧮 公式识别与转换 | 截图粘贴/文件上传/手写板三种输入，识别后一键复制 LaTeX/MathML |

## 技术栈

- **UI 框架**：Streamlit + iOS 液态玻璃自定义主题
- **大模型**：通义千问（DashScope）qwen-turbo / qwen-vl-max
- **文档处理**：python-docx / pdfplumber / pypdf
- **向量检索（文献模块预留）**：llama-index + HuggingFace Embedding

## 注意事项

- 查重分析为语义相似度判断，不是知网/万方数据库级正式查重
- 公式识别使用 DashScope 多模态接口，需确保 API Key 有 qwen-vl-max 权限
- 首次运行文献模块时会自动下载 HuggingFace Embedding 模型（约 400MB）
