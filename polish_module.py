# polish_module.py —— 论文内容润色（报告化升级版 + 玻璃 UI）
import streamlit as st
from ui_theme import render_page_shell, glass_card, glass_card_close, inner_card, inner_card_close
from shared_utils import (
    get_llm, check_dependencies, show_dependency_install_hint,
    extract_text_from_uploaded_file, chunk_text_by_paragraphs, render_download_button,
)
from prompt_templates import POLISH_CHUNK_PROMPT, POLISH_REPORT_PROMPT

POLISH_RULES = {
    "轻度润色（通顺）": "1. 只修正错别字、标点、语法错误。\n2. 让语句更通顺，不做大改动。\n3. 不改变句式、不学术化，保留原文风格。",
    "标准润色（学术化）": "1. 语言学术化、严谨、正式，符合论文规范。\n2. 优化逻辑、流畅度、段落连贯性。\n3. 修正格式错误，不改变原意。\n4. 适度优化句式，不做大改写。",
    "深度润色（强降重）": "1. 大幅度优化句式结构，更换表达方式，强力降重。\n2. 全面学术化、专业化、正式化。\n3. 保持原意不变，表达方式完全重构。\n4. 逻辑强化、层次更清晰、语句更高级。",
}

def polish_chunk(llm, text, polish_level):
    return llm.complete(POLISH_CHUNK_PROMPT.format(polish_level=polish_level, polish_rules=POLISH_RULES[polish_level], text=text)).text

def generate_polish_report(llm, original, polished):
    return llm.complete(POLISH_REPORT_PROMPT.format(original_text=original[:8000], polished_text=polished[:8000])).text

def polish_page():
    render_page_shell("✍️ 论文内容润色", "支持手动粘贴或上传 PDF / Word；长文本自动分段；输出原文摘要、润色内容、修改说明、学术表达替换建议")

    deps_ok, missing = check_dependencies()
    if not deps_ok:
        show_dependency_install_hint(missing)

    # ---- 输入卡片 ----
    st.markdown(glass_card(), unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("📌 润色设置")
        polish_level = st.radio("润色强度", ["轻度润色（通顺）", "标准润色（学术化）", "深度润色（强降重）"])
        st.subheader("📎 上传文档（可选）")
        uploaded_file = st.file_uploader("上传 PDF 或 DOCX 文件", type=["pdf", "docx"], help="上传后自动抽取正文；也可同时粘贴文本，两者会合并处理。")
    with col2:
        st.subheader("✍️ 输入需要润色的内容")
        input_text = st.text_area("", height=280, placeholder="粘贴你的论文段落、摘要、草稿……\n也可上传 PDF/DOCX 自动抽取。")

    extracted_text = ""
    if uploaded_file and deps_ok:
        try:
            extracted_text = extract_text_from_uploaded_file(uploaded_file)
            if extracted_text.strip():
                st.caption(f"✅ 已从 {uploaded_file.name} 抽取 {len(extracted_text)} 字符")
            else:
                st.warning(f"⚠️ {uploaded_file.name} 未能抽取到正文。")
        except RuntimeError as e:
            st.warning(f"⚠️ {e}")
        except Exception as e:
            st.error(f"解析异常：{e}")

    combined_text = (input_text + "\n\n" + extracted_text).strip()

    if st.button("开始润色", type="primary", use_container_width=True):
        if not combined_text:
            st.warning("请输入需要润色的内容或上传文档！")
        else:
            llm = get_llm(max_tokens=4096, temperature=0.1)
            with st.spinner("正在润色中，请稍候..."):
                chunks = chunk_text_by_paragraphs(combined_text, max_chars=3000)
                if len(chunks) == 1:
                    polished = polish_chunk(llm, chunks[0], polish_level)
                else:
                    polished_chunks = []
                    progress_bar = st.progress(0, text="正在分段润色...")
                    for i, chunk in enumerate(chunks):
                        progress_bar.progress((i + 0.5) / len(chunks), text=f"正在润色第 {i+1}/{len(chunks)} 段...")
                        polished_chunks.append(polish_chunk(llm, chunk, polish_level))
                    progress_bar.progress(1.0, text="分段润色完成 ✅")
                    polished = "\n\n".join(polished_chunks)

                with st.spinner("正在生成润色报告（摘要/修改说明/替换建议）..."):
                    report = generate_polish_report(llm, combined_text, polished)

                full_report = f"""# ✍️ 论文润色报告

> 润色强度：{polish_level}

---

## 润色后内容

{polished}

---

{report}
"""
                st.session_state.polish_report = full_report
                st.session_state.polish_polished = polished
                st.session_state.polish_level = polish_level
                st.success("✅ 润色完成！")
    st.markdown(glass_card_close(), unsafe_allow_html=True)

    # ---- 结果卡片 ----
    if "polish_report" in st.session_state:
        st.markdown(glass_card(f"📄 润色后内容（{st.session_state.polish_level}）"), unsafe_allow_html=True)
        st.markdown(st.session_state.polish_polished)
        st.markdown(glass_card_close(), unsafe_allow_html=True)

        parts = st.session_state.polish_report.split("---\n\n", 1)
        if len(parts) > 1:
            st.markdown(glass_card("📋 修改说明与替换建议"), unsafe_allow_html=True)
            st.markdown(parts[1])
            st.markdown(glass_card_close(), unsafe_allow_html=True)

        render_download_button(st.session_state.polish_report, "论文润色报告.md")
