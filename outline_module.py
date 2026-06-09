# outline_module.py —— 论文框架自动生成（报告化升级版 + 玻璃 UI）
import streamlit as st
from ui_theme import render_page_shell, glass_card, glass_card_close
from shared_utils import get_llm, render_download_button, show_ai_error
from prompt_templates import OUTLINE_ENHANCED_PROMPT

def generate_outline_report(llm, subject, thesis_title, research_direction, thesis_type,
                            research_methods, innovation_points, chapter_preference, format_preference):
    prompt = OUTLINE_ENHANCED_PROMPT.format(
        subject=subject, thesis_title=thesis_title, research_direction=research_direction,
        thesis_type=thesis_type,
        research_methods=research_methods or "未指定", innovation_points=innovation_points or "未指定",
        chapter_preference=chapter_preference or "标准章节数量与深度", format_preference=format_preference or "通用学术格式",
    )
    return llm.complete(prompt).text

def outline_page():
    render_page_shell("📝 论文框架自动生成", "输入研究信息，一键生成摘要建议、章节框架、写作要点、方法安排、进度建议的完整报告")

    # ---- 输入卡片 ----
    st.markdown(glass_card(), unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_input("学科领域（必填）", placeholder="例如：计算机科学与技术、管理学...")
        thesis_type = st.selectbox("论文类型（必填）", ["本科毕业论文", "硕士学位论文", "博士学位论文", "开题报告"])
    with col2:
        thesis_title = st.text_input("论文题目（必填）", placeholder="例如：S波段多普勒天气雷达回波模拟技术研究")
        research_direction = st.text_area("研究方向/核心内容（必填）", placeholder="例如：研究S波段多普勒天气雷达回波的高精度模拟方法...", height=100)

    with st.expander("⚙️ 高级选项（可选，可提升框架针对性）"):
        research_methods = st.text_input("研究方法", placeholder="例如：数值模拟、对比实验、问卷调查...")
        innovation_points = st.text_input("创新点", placeholder="例如：提出了一种新的XX算法...")
        chapter_preference = st.selectbox("章节数量/深度偏好", [
            "标准章节数量与深度", "精简型（4-5章，侧重核心内容）",
            "详尽型（6-8章，覆盖全面）", "理论深挖型（侧重理论分析与推导）", "工程实践型（侧重系统设计与实现）",
        ])
        format_preference = st.text_input("学校格式偏好", placeholder="例如：清华大学硕士论文格式、GB/T 7714 参考文献...")

    if st.button("一键生成论文框架", type="primary", use_container_width=True):
        if not thesis_title or not research_direction:
            st.error("❌ 请填写论文题目和研究方向（必填）！")
        elif not subject.strip():
            st.error("❌ 请填写学科领域（必填）！")
        else:
            try:
                llm = get_llm(max_tokens=8192, temperature=0.1)
                with st.spinner("正在生成专业论文框架报告，请稍候..."):
                    report = generate_outline_report(llm, subject, thesis_title, research_direction,
                                                     thesis_type, research_methods, innovation_points,
                                                     chapter_preference, format_preference)
                st.session_state.outline_report = report
                st.session_state.outline_title = thesis_title
                st.success("✅ 论文框架生成完成！")
            except Exception as exc:
                show_ai_error(exc, "论文框架生成失败")
    st.markdown(glass_card_close(), unsafe_allow_html=True)

    # ---- 结果卡片 ----
    if "outline_report" in st.session_state:
        st.markdown(glass_card(f"📋 {st.session_state.outline_title} 论文框架报告"), unsafe_allow_html=True)
        st.markdown(st.session_state.outline_report)
        st.markdown(glass_card_close(), unsafe_allow_html=True)
        safe_title = st.session_state.outline_title.replace("/", "_").replace("\\", "_")
        render_download_button(st.session_state.outline_report, f"{safe_title}_论文框架报告.md")
