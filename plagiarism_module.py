# plagiarism_module.py —— 查重分析提醒（报告化升级版 + 玻璃 UI）
import streamlit as st
from ui_theme import render_page_shell, glass_card, glass_card_close
from shared_utils import (
    get_llm, check_dependencies, show_dependency_install_hint,
    extract_text_from_uploaded_file, render_download_button,
)
from prompt_templates import PLAGIARISM_RISK_PROMPT

def analyze_plagiarism_risk(llm, text):
    return llm.complete(PLAGIARISM_RISK_PROMPT.format(text=text[:8000])).text

def plagiarism_page():
    render_page_shell("⚠️ 查重分析提醒", "基于语义相似度检测重复风险，输出风险等级、疑似高风险句、降重策略与改写示例")

    st.info("⚠️ **重要提示**：本功能基于大语言模型的语义分析，判断文本与常见学术表达的相似程度，属于**语义风险分析**，不是知网/万方等数据库级的正式查重。结果仅供写作参考，不能替代正式查重服务。")

    deps_ok, missing = check_dependencies()
    if not deps_ok:
        show_dependency_install_hint(missing)

    # ---- 输入卡片 ----
    st.markdown(glass_card(), unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("📎 上传文档（可选）")
        uploaded_file = st.file_uploader("上传 PDF 或 DOCX 文件", type=["pdf", "docx"], help="上传后自动抽取正文进行查重分析。")
    with col2:
        st.subheader("📝 粘贴需要检测的内容")
        input_text = st.text_area("", height=250, placeholder="粘贴论文的摘要、绪论、研究内容等段落，检测重复风险并获取降重建议...")

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

    if st.button("🔍 开始查重分析", type="primary", use_container_width=True):
        if not combined_text:
            st.warning("请输入需要检测的内容或上传文档！")
        else:
            llm = get_llm(max_tokens=4096, temperature=0.1)
            with st.spinner("正在进行语义查重分析，请稍候..."):
                analysis = analyze_plagiarism_risk(llm, combined_text)
            full_report = f"""# ⚠️ 查重风险分析报告

> ⚠️ **重要提示**：本报告基于大语言模型语义分析，非知网/万方数据库级正式查重。结果仅供参考。

---

{analysis}

---
> 生成说明：本报告由学术论文辅助写作智能体自动生成，基于语义相似度判断，不能替代正式查重服务。
"""
            st.session_state.plagiarism_report = full_report
            st.session_state.plagiarism_analysis = analysis
            st.success("✅ 查重分析完成！")
    st.markdown(glass_card_close(), unsafe_allow_html=True)

    # ---- 结果卡片 ----
    if "plagiarism_report" in st.session_state:
        st.markdown(glass_card("🔍 查重风险分析结果"), unsafe_allow_html=True)
        st.markdown(st.session_state.plagiarism_analysis)
        st.markdown(glass_card_close(), unsafe_allow_html=True)
        render_download_button(st.session_state.plagiarism_report, "查重风险分析报告.md")
