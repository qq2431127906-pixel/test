# literature_module.py —— 文献摘要智能梳理（报告化升级版 + 玻璃 UI）
import streamlit as st
from ui_theme import render_page_shell, glass_card, glass_card_close, inner_card, inner_card_close
from shared_utils import (
    get_llm,
    check_dependencies,
    show_dependency_install_hint,
    extract_texts_from_files,
    render_download_button,
    show_ai_error,
)
from prompt_templates import (
    LITERATURE_SINGLE_SUMMARY_PROMPT,
    LITERATURE_SYNTHESIS_PROMPT,
)

def generate_single_summary(llm, paper_text: str, subject: str, file_name: str) -> str:
    prompt = LITERATURE_SINGLE_SUMMARY_PROMPT.format(
        subject=subject,
        paper_text=paper_text[:12000],
    )
    response = llm.complete(prompt)
    return f"## 📄 {file_name}\n\n{response.text}"

def generate_synthesis(llm, summaries_text: str, subject: str) -> str:
    prompt = LITERATURE_SYNTHESIS_PROMPT.format(
        subject=subject,
        summaries_text=summaries_text,
    )
    response = llm.complete(prompt)
    return response.text

def literature_page():
    render_page_shell("📑 文献摘要智能梳理", "上传 PDF / Word 学术文献，逐篇结构化摘要 + 综合研究脉络/对比/热点/大纲")

    deps_ok, missing = check_dependencies()
    if not deps_ok:
        show_dependency_install_hint(missing)

    # ---- 输入卡片 ----
    st.markdown(glass_card(), unsafe_allow_html=True)
    subject = st.text_input("学科领域（必填）", placeholder="例如：计算机科学与技术、管理学、机械工程、医学...")
    uploaded_files = st.file_uploader(
        "上传学术文献（PDF / DOCX）",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        help="支持同时上传多篇文献；旧版 .doc 请先另存为 .docx",
    )

    if st.button("开始生成文献梳理结果", type="primary", use_container_width=True):
        if not uploaded_files:
            st.warning("请先上传至少一篇文献。")
        elif not subject.strip():
            st.warning("请填写学科领域。")
        elif not deps_ok:
            st.error("请先安装缺失的依赖包后再使用上传功能。")
        else:
            try:
                llm = get_llm(max_tokens=4096, temperature=0.1)
                with st.spinner("正在抽取文献正文..."):
                    file_data = extract_texts_from_files(uploaded_files)
                valid_files = [f for f in file_data if not f["error"] and f["text"]]
                error_files = [f for f in file_data if f["error"]]
                for ef in error_files:
                    st.warning(f"⚠️ {ef['name']}：{ef['error']}")
                if not valid_files:
                    st.error("所有文件均无法抽取正文，请检查文件格式或内容。")
                else:
                    single_summaries = []
                    progress_bar = st.progress(0, text="正在生成单篇摘要...")
                    for i, fdata in enumerate(valid_files):
                        progress_bar.progress(i / len(valid_files), text=f"正在生成：{fdata['name']} 的结构化摘要...")
                        with st.spinner(f"正在分析：{fdata['name']}..."):
                            single_summaries.append(generate_single_summary(llm, fdata["text"], subject, fdata["name"]))
                    progress_bar.progress(1.0, text="单篇摘要生成完成 ✅")

                    with st.spinner("正在生成综合研究报告（脉络/对比/热点/大纲）..."):
                        synthesis = generate_synthesis(llm, "\n\n---\n\n".join(single_summaries), subject)

                    single_section = "\n\n---\n\n".join(single_summaries)
                    full_report = f"""# 📑 文献梳理报告

---

## 第一部分 · 单篇文献结构化摘要

{single_section}

---

## 第二部分 · 综合研究报告

{synthesis}

---
"""
                    st.session_state.literature_report = full_report
                    st.session_state.literature_single = single_section
                    st.session_state.literature_synthesis = synthesis
                    st.success("✅ 文献梳理完成！")
            except Exception as exc:
                show_ai_error(exc, "文献梳理失败")
    st.markdown(glass_card_close(), unsafe_allow_html=True)

    # ---- 结果卡片 ----
    if "literature_report" in st.session_state:
        st.markdown(glass_card("📋 单篇文献结构化摘要"), unsafe_allow_html=True)
        st.markdown(st.session_state.literature_single)
        st.markdown(glass_card_close(), unsafe_allow_html=True)

        st.markdown(glass_card("🔬 综合研究报告"), unsafe_allow_html=True)
        st.markdown(st.session_state.literature_synthesis)
        st.markdown(glass_card_close(), unsafe_allow_html=True)

        render_download_button(st.session_state.literature_report, "文献梳理报告.md", "📥 下载完整文献梳理报告 (Markdown)")
