# formula_module.py —— 公式识别与转换
import os
import base64
import requests
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import streamlit as st
import streamlit.components.v1 as components
from ui_theme import render_page_shell
from shared_utils import get_dashscope_api_key, get_llm, format_ai_error
from dotenv import load_dotenv
load_dotenv()

PASTE_COMPONENT_DIR = os.path.join(os.path.dirname(__file__), "paste_image_component")
paste_image_component = components.declare_component(
    "paste_image_component",
    path=PASTE_COMPONENT_DIR,
)

DRAWING_COMPONENT_DIR = os.path.join(os.path.dirname(__file__), "drawing_component")
drawing_component = components.declare_component(
    "drawing_component",
    path=DRAWING_COMPONENT_DIR,
)

def parse_pasted_image(component_value):
    if not component_value or not isinstance(component_value, dict):
        return None
    data_url = component_value.get("dataUrl", "")
    if not data_url.startswith("data:image/") or "," not in data_url:
        return None
    header, encoded = data_url.split(",", 1)
    mime_type = component_value.get("mimeType") or header.split(";")[0].replace("data:", "")
    image_bytes = base64.b64decode(encoded)
    return {
        "bytes": image_bytes,
        "mime_type": mime_type,
        "name": component_value.get("name", "clipboard.png"),
        "size": len(image_bytes),
        "updated_at": component_value.get("updatedAt"),
    }

def parse_drawing_image(component_value):
    if not component_value or not isinstance(component_value, dict):
        return None
    data_url = component_value.get("dataUrl", "")
    if not data_url.startswith("data:image/") or "," not in data_url:
        return None
    header, encoded = data_url.split(",", 1)
    mime_type = component_value.get("mimeType") or header.split(";")[0].replace("data:", "")
    image_bytes = base64.b64decode(encoded)
    return {
        "bytes": image_bytes,
        "mime_type": mime_type,
        "name": component_value.get("name", "handwritten.png"),
        "size": len(image_bytes),
        "updated_at": component_value.get("updatedAt"),
    }

def recognize_formula(image_bytes, mime_type="image/png"):
    try:
        api_key = get_dashscope_api_key()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        data = {
            "model": "qwen-vl-max",
            "input": {
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "image", "image": f"data:{mime_type};base64,{base64_image}"},
                        {"type": "text", "text": "请准确识别图片中的数学公式，只输出标准的LaTeX代码，不要任何解释、说明或额外内容。确保符号、上下标、分数、根号、指数完全正确。"}
                    ]
                }]
            },
            "parameters": {"temperature": 0.01, "max_tokens": 2048}
        }
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        latex_code = result["output"]["choices"][0]["message"]["content"][0]["text"].strip()
        latex_code = latex_code.replace("```latex", "").replace("```", "").strip()
        latex_code = latex_code.replace("$", "").strip()
        return latex_code
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else ""
        detail = e.response.text[:300] if e.response is not None else str(e)
        if status in (401, 403):
            return "❌ 识别失败：请检查 DASHSCOPE_API_KEY 是否有效，并确认该 Key 已开通 qwen-vl-max 视觉模型权限。"
        return f"❌ 识别失败：DashScope 接口返回异常（HTTP {status}）：{detail}"
    except requests.exceptions.RequestException as e:
        return f"❌ 识别失败：网络请求失败，请检查网络或代理设置。详情：{e}"
    except Exception as e:
        return f"❌ {format_ai_error(e)}"

def convert_all_formats(latex_code):
    formats = {}
    formats["无特殊附加"] = latex_code
    formats["$ ... $ 格式"] = f"${latex_code}$"
    formats["$$ ... $$ 格式"] = f"$$\n{latex_code}\n$$"
    formats["\\[ ... \\] 格式"] = f"\\[\n{latex_code}\n\\]"
    formats["\\( ... \\) 格式"] = f"\\({latex_code}\\)"
    formats["\\begin{equation} ... \\end{equation} 格式"] = f"\\begin{{equation}}\n{latex_code}\n\\end{{equation}}"
    try:
        llm = get_llm(max_tokens=4096, temperature=0.01)
        mathml_prompt = f"""
        将以下LaTeX公式转换为Microsoft Word和MathType完全兼容的标准MathML代码。
        要求：
        1. 使用Word 2016+和MathType 6.9+支持的标准标签
        2. 包含正确的命名空间：http://www.w3.org/1998/Math/MathML
        3. 不要添加任何注释、说明或多余内容
        4. 确保上下标、分数、根号、共轭转置等符号完全正确
        
        LaTeX公式：
        {latex_code}
        """
        mathml_result = llm.complete(mathml_prompt).text.strip()
        mathml_result = mathml_result.replace("```mathml", "").replace("```", "").strip()
        formats["MathML (Word/MathType完美兼容)"] = mathml_result
        formats["MathType TeX格式"] = latex_code
        asciimath_prompt = f"将以下LaTeX转换为AsciiMath，只输出代码：{latex_code}"
        formats["AsciiMath"] = llm.complete(asciimath_prompt).text.strip()
        typst_prompt = f"将以下LaTeX转换为Typst公式，只输出代码：{latex_code}"
        formats["Typst"] = llm.complete(typst_prompt).text.strip()
    except Exception as exc:
        error_text = f"转换失败：{format_ai_error(exc)}"
        formats["MathML (Word/MathType完美兼容)"] = error_text
        formats["MathType TeX格式"] = latex_code
        formats["AsciiMath"] = error_text
        formats["Typst"] = error_text
    return formats

def init_formula_state():
    """确保 formula 相关的 session_state 变量已初始化"""
    defaults = {
        "latex_code": "",
        "all_formats": {},
        "current_code": "",
        "recognition_done": False,
        "pasted_formula_image": None,
        "show_drawing": False,
        "drawn_formula_image": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def formula_page():
    render_page_shell("🧮 公式识别与转换", "支持截图粘贴 / 文件上传 / 手写板绘制，识别后一键复制 LaTeX 或 MathML")
    init_formula_state()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col_title, col_type = st.columns([3, 2])
        with col_title:
            st.subheader("识别对象")
        with col_type:
            st.selectbox("", ["自动检测", "公式", "表格", "文字"], index=0, label_visibility="collapsed")

        st.markdown("通义千问OCR识别，支持PNG/JPG/JPEG格式，清晰完整的公式截图识别准确率更高")
        st.toggle("开启文档模式视觉AI增强", value=True)

        st.markdown('<div class="glass-card-inner" style="text-align:center;padding:1rem;border:2px dashed rgba(139,158,255,0.4);background:rgba(139,158,255,0.08);border-radius:14px;margin-bottom:1rem;color:#5b6fff;font-weight:500;">点击下方蓝色区域后按 Ctrl+V，可直接粘贴截图</div>', unsafe_allow_html=True)

        pasted_value = paste_image_component(default=None, key="formula_clipboard_paste")
        parsed_image = parse_pasted_image(pasted_value)
        if parsed_image and parsed_image.get("updated_at") != st.session_state.get("pasted_formula_updated_at"):
            st.session_state.pasted_formula_image = parsed_image
            st.session_state.pasted_formula_updated_at = parsed_image.get("updated_at")
            st.session_state.latex_code = ""
            st.session_state.all_formats = {}
            st.session_state.current_code = ""
            st.session_state.recognition_done = False

        st.caption("如果浏览器不允许读取剪贴板，也可以使用下面的上传入口。")
        uploaded_file = st.file_uploader("上传公式截图（备用）", type=["png", "jpg", "jpeg"], label_visibility="collapsed", key="formula_file_upload")

        image_bytes = None
        image_mime_type = "image/png"
        image_source_name = ""
        if uploaded_file:
            image_bytes = uploaded_file.getvalue()
            image_mime_type = uploaded_file.type or "image/png"
            image_source_name = uploaded_file.name
        elif st.session_state.pasted_formula_image:
            image_bytes = st.session_state.pasted_formula_image["bytes"]
            image_mime_type = st.session_state.pasted_formula_image["mime_type"]
            image_source_name = st.session_state.pasted_formula_image["name"]
        elif st.session_state.drawn_formula_image:
            image_bytes = st.session_state.drawn_formula_image["bytes"]
            image_mime_type = st.session_state.drawn_formula_image["mime_type"]
            image_source_name = st.session_state.drawn_formula_image["name"]

        st.markdown('<div class="glass-card-inner" style="text-align:center;padding:1.5rem;min-height:180px;display:flex;align-items:center;justify-content:center;">', unsafe_allow_html=True)
        if image_bytes:
            st.image(image_bytes, width=400)
        else:
            st.info("点击上方蓝色区域后按 Ctrl+V 粘贴截图，或点击下方手写板手写公式")
        st.markdown('</div>', unsafe_allow_html=True)

        col_btn_upload, col_btn_hand = st.columns(2)
        with col_btn_upload:
            if image_bytes:
                st.success(f"✅ 已获取图片：{image_source_name}")
            else:
                st.info("等待粘贴或上传")
        with col_btn_hand:
            hand_label = "✍️ 关闭手写板" if st.session_state.show_drawing else "✍️ 手写板"
            if st.button(hand_label, use_container_width=True):
                st.session_state.show_drawing = not st.session_state.show_drawing

        if st.session_state.show_drawing:
            st.caption("🖊️ 在下方手写区用鼠标/触控笔绘制公式，点击「确认手写」后自动填入预览区")
            drawn_value = drawing_component(default=None, key="formula_drawing_canvas")
            parsed_drawing = parse_drawing_image(drawn_value)
            if parsed_drawing and parsed_drawing.get("updated_at") != st.session_state.get("drawn_formula_updated_at"):
                st.session_state.drawn_formula_image = parsed_drawing
                st.session_state.drawn_formula_updated_at = parsed_drawing.get("updated_at")
                st.session_state.latex_code = ""
                st.session_state.all_formats = {}
                st.session_state.current_code = ""
                st.session_state.recognition_done = False
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col_result_title, col_mode = st.columns([3, 2])
        with col_result_title:
            if st.session_state.recognition_done and not st.session_state.latex_code.startswith("❌"):
                st.subheader("✅ 识别结果")
            else:
                st.subheader("识别结果")
            st.markdown('<span style="display:inline-block;padding:4px 12px;border-radius:6px;background:rgba(91,111,255,0.12);color:#5b6fff;font-size:14px;margin-left:12px;font-weight:500;">类型：公式</span>', unsafe_allow_html=True)
        with col_mode:
            st.radio("", ["公式模式", "文档模式(Markdown)"], index=0, horizontal=True, label_visibility="collapsed")

        st.markdown('<div class="glass-card-inner" style="text-align:center;padding:1.5rem;min-height:180px;display:flex;align-items:center;justify-content:center;">', unsafe_allow_html=True)
        if st.session_state.latex_code and not st.session_state.latex_code.startswith("❌"):
            st.latex(st.session_state.latex_code)
        else:
            st.info("识别结果将显示在这里")
        st.markdown('</div>', unsafe_allow_html=True)

        col_btn3, col_btn4 = st.columns(2)
        with col_btn3:
            with st.popover("复制LaTeX", use_container_width=True):
                if st.button("无特殊附加", use_container_width=True) and "无特殊附加" in st.session_state.all_formats:
                    st.session_state.current_code = st.session_state.all_formats["无特殊附加"]
                if st.button("$ ... $ 格式", use_container_width=True) and "$ ... $ 格式" in st.session_state.all_formats:
                    st.session_state.current_code = st.session_state.all_formats["$ ... $ 格式"]
                if st.button("$$ ... $$ 格式", use_container_width=True) and "$$ ... $$ 格式" in st.session_state.all_formats:
                    st.session_state.current_code = st.session_state.all_formats["$$ ... $$ 格式"]
                if st.button("\\[ ... \\] 格式", use_container_width=True) and "\\[ ... \\] 格式" in st.session_state.all_formats:
                    st.session_state.current_code = st.session_state.all_formats["\\[ ... \\] 格式"]
                if st.button("\\( ... \\) 格式", use_container_width=True) and "\\( ... \\) 格式" in st.session_state.all_formats:
                    st.session_state.current_code = st.session_state.all_formats["\\( ... \\) 格式"]
                if st.button("\\begin{equation} ... \\end{equation} 格式", use_container_width=True) and "\\begin{equation} ... \\end{equation} 格式" in st.session_state.all_formats:
                    st.session_state.current_code = st.session_state.all_formats["\\begin{equation} ... \\end{equation} 格式"]
        with col_btn4:
            with st.popover("复制MathML(Word)", use_container_width=True):
                if st.button("✅ MathML (Word/MathType完美兼容)", use_container_width=True) and "MathML (Word/MathType完美兼容)" in st.session_state.all_formats:
                    st.session_state.current_code = st.session_state.all_formats["MathML (Word/MathType完美兼容)"]
                if st.button("📝 MathType TeX格式", use_container_width=True) and "MathType TeX格式" in st.session_state.all_formats:
                    st.session_state.current_code = st.session_state.all_formats["MathType TeX格式"]
                if st.button("复制AsciiMath", use_container_width=True) and "AsciiMath" in st.session_state.all_formats:
                    st.session_state.current_code = st.session_state.all_formats["AsciiMath"]
                if st.button("复制Typst", use_container_width=True) and "Typst" in st.session_state.all_formats:
                    st.session_state.current_code = st.session_state.all_formats["Typst"]

        st.markdown('<div class="glass-card-inner" style="font-family:monospace;font-size:14px;min-height:100px;white-space:pre-wrap;word-break:break-all;margin-bottom:1rem;">', unsafe_allow_html=True)
        st.code(st.session_state.current_code, language="markdown")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("🔍 开始识别", type="primary", use_container_width=True):
            if not image_bytes:
                st.warning("请先粘贴截图、上传公式图片，或使用手写板绘制公式！")
            else:
                with st.spinner("正在识别公式..."):
                    latex_code = recognize_formula(image_bytes, image_mime_type)
                    st.session_state.latex_code = latex_code
                    if not latex_code.startswith("❌"):
                        st.session_state.all_formats = convert_all_formats(latex_code)
                        mathml_code = st.session_state.all_formats["MathML (Word/MathType完美兼容)"]
                        if mathml_code.startswith("转换失败"):
                            st.session_state.current_code = st.session_state.all_formats["无特殊附加"]
                            st.warning("✅ 公式识别完成，但扩展格式转换失败，已先选择 LaTeX 原始格式。")
                        else:
                            st.session_state.current_code = mathml_code
                            st.success("✅ 识别完成！已自动选择MathType兼容格式")
                        st.session_state.recognition_done = True
                    else:
                        st.session_state.recognition_done = True
                        st.error(latex_code)

        if st.session_state.current_code:
            st.download_button("📋 一键复制当前格式", data=st.session_state.current_code, file_name="公式.txt", mime="text/plain", use_container_width=True)

        st.info("""
        💡 **三种输入方式**：
        1. **截图粘贴**：按 Win+Shift+S 截图 → 点击蓝色区域 → Ctrl+V
        2. **文件上传**：上传 PNG/JPG 公式截图
        3. **手写板**：点击「✍️ 手写板」→ 鼠标/触控笔绘制 → 确认手写
        """)
        st.markdown('</div>', unsafe_allow_html=True)
