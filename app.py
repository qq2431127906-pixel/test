import streamlit as st

st.set_page_config(
    page_title="学术论文辅助写作智能体",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from ui_theme import apply_theme, render_nav, render_page_shell
from literature_module import literature_page
from outline_module import outline_page
from polish_module import polish_page
from format_module import format_page
from plagiarism_module import plagiarism_page
from formula_module import formula_page

# 全局主题注入（只一次）
apply_theme()

# 顶部胶囊导航
render_nav()

# 路由
page = st.session_state.get("nav_page", 0)
if page == 0:
    literature_page()
elif page == 1:
    outline_page()
elif page == 2:
    polish_page()
elif page == 3:
    format_page()
elif page == 4:
    plagiarism_page()
elif page == 5:
    formula_page()
