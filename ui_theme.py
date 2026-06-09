# ui_theme.py —— iOS 液态玻璃视觉系统
# 全局 CSS 注入 + 页面模板 + 导航组件

import streamlit as st

# ============================================================
# CSS 模板（单一注入入口）
# ============================================================

THEME_CSS = """
/* ============================================================
   iOS 液态玻璃 v6 — 只改容器外观，零干涉 Streamlit 控件内部
   原则：
     1. 绝不用 * 或 p/div 等宽选择器碰 Streamlit 内部 DOM
     2. 按钮/输入框/下拉框等原生控件只改外层（bg/border/radius），
        不碰 font-size / line-height / padding / min-height / font-family
     3. backdrop-filter 仅用于大容器
   ============================================================ */

:root {
    --mouse-x:          50%;
    --mouse-y:          35%;
    --primary:          #5b6fff;
    --primary-light:    #8b9eff;
    --primary-glow:     rgba(91,111,255,0.16);
    --surface-card:     rgba(255,255,255,0.24);
    --surface-inner:    rgba(255,255,255,0.22);
    --surface-input:    rgba(255,255,255,0.18);
    --border-card:      rgba(255,255,255,0.48);
    --border-subtle:    rgba(255,255,255,0.32);
    --glass-highlight:  rgba(255,255,255,0.72);
    --shadow-card:      0 16px 48px rgba(38,45,78,0.08), 0 2px 8px rgba(38,45,78,0.04), inset 0 1px 0 rgba(255,255,255,0.46);
    --shadow-hover:     0 20px 58px rgba(38,45,78,0.11), 0 5px 18px rgba(91,111,255,0.08), inset 0 1px 0 rgba(255,255,255,0.58);
    --radius-xl:        24px;
    --radius-lg:        18px;
    --radius-md:        14px;
    --radius-sm:        10px;
    --ease-ios:         0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
}

/* ===== 背景 ===== */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] { background: transparent !important; }

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at var(--mouse-x) var(--mouse-y), rgba(255,255,255,0.36), transparent 28%),
        linear-gradient(150deg, #dbe3f0 0%, #eef2f8 36%, #f3eef8 68%, #e2eaf4 100%) !important;
    position: relative; overflow-x: hidden;
}
[data-testid="stAppViewContainer"]::before {
    content: ""; position: fixed; top: -250px; left: -160px;
    width: 620px; height: 620px;
    background: radial-gradient(circle, rgba(91,111,255,0.12) 0%, transparent 68%);
    border-radius: 50%; pointer-events: none; z-index: 0;
}
[data-testid="stAppViewContainer"]::after {
    content: ""; position: fixed; bottom: -220px; right: -140px;
    width: 540px; height: 540px;
    background: radial-gradient(circle, rgba(125,100,230,0.09) 0%, transparent 68%);
    border-radius: 50%; pointer-events: none; z-index: 0;
}

/* ===== 消除 Streamlit 默认 chrome ===== */
[data-testid="stHeader"]          { height: 0 !important; min-height: 0 !important; padding: 0 !important; margin: 0 !important; overflow: hidden !important; border: none !important; }
[data-testid="stToolbar"]         { display: none !important; }
[data-testid="stDecoration"]      { display: none !important; }
[data-testid="collapsedControl"]  { display: none !important; }
[data-testid="stSidebar"]         { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }
button[kind="header"]             { display: none !important; }
#MainMenu                         { visibility: hidden; }
footer                            { visibility: hidden; }

/* ===== 主内容 ===== */
.block-container {
    padding: 0 1.5rem 2rem 1.5rem !important;
    max-width: 1200px !important;
    position: relative; z-index: 1;
}

/* ===== 玻璃卡片 ===== */
.glass-card {
    background:
        radial-gradient(circle at var(--mouse-x) var(--mouse-y), rgba(255,255,255,0.38), transparent 32%),
        linear-gradient(145deg, rgba(255,255,255,0.32), rgba(255,255,255,0.12)) !important;
    backdrop-filter: blur(34px) saturate(1.45); -webkit-backdrop-filter: blur(34px) saturate(1.45);
    border-radius: var(--radius-xl) !important;
    border: 1px solid var(--border-card) !important;
    box-shadow: var(--shadow-card) !important;
    padding: 1.5rem 1.7rem !important;
    margin-bottom: 0.9rem !important;
    transition: transform var(--ease-ios), box-shadow var(--ease-ios), border-color var(--ease-ios), background 0.45s ease;
    animation: fadeSlideIn 0.4s ease both;
    position: relative; z-index: 2;
    overflow: hidden;
    isolation: isolate;
}
.glass-card::before {
    content: "";
    position: absolute; inset: 0;
    border-radius: inherit;
    pointer-events: none;
    z-index: 0;
    background:
        linear-gradient(135deg, rgba(255,255,255,0.74), rgba(255,255,255,0.06) 36%, rgba(255,255,255,0.02) 62%, rgba(91,111,255,0.08)),
        radial-gradient(circle at 18% 0%, rgba(255,255,255,0.72), transparent 30%);
    opacity: 0.58;
}
.glass-card::after {
    content: "";
    position: absolute; inset: 1px;
    border-radius: calc(var(--radius-xl) - 1px);
    pointer-events: none;
    z-index: 0;
    background: radial-gradient(circle at var(--mouse-x) var(--mouse-y), rgba(91,111,255,0.10), transparent 36%);
    opacity: 0;
    transition: opacity var(--ease-ios);
}
.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-hover) !important;
    border-color: rgba(255,255,255,0.62) !important;
}
.glass-card:hover::after { opacity: 1; }
.glass-card > * { position: relative; z-index: 1; }
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}
.glass-card-inner {
    background:
        linear-gradient(145deg, rgba(255,255,255,0.26), rgba(255,255,255,0.12)) !important;
    backdrop-filter: blur(22px) saturate(1.3); -webkit-backdrop-filter: blur(22px) saturate(1.3);
    border-radius: var(--radius-lg) !important;
    border: 1px solid var(--border-subtle) !important;
    padding: 1.1rem 1.3rem !important;
    margin-bottom: 0.6rem !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.38), 0 6px 22px rgba(38,45,78,0.04);
    position: relative;
    overflow: hidden;
}
.glass-card-inner::before {
    content: "";
    position: absolute; inset: 0;
    pointer-events: none;
    background: radial-gradient(circle at var(--mouse-x) var(--mouse-y), rgba(255,255,255,0.24), transparent 34%);
    opacity: 0.55;
}
.glass-card-inner > * { position: relative; z-index: 1; }

/* ===== 按钮 — 只改外层三个属性，不动内部文字 ===== */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #5b6fff 0%, #7555ef 100%) !important;
    border-color: transparent !important;
    color: #fff !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 4px 16px rgba(91,111,255,0.3) !important;
}
.stButton > button:not([kind="primary"]),
.stDownloadButton > button {
    background: rgba(255,255,255,0.34) !important;
    border-color: rgba(255,255,255,0.56) !important;
    color: #3a3f5c !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.42) !important;
}
.stButton > button:not([kind="primary"]):hover,
.stDownloadButton > button:hover {
    background: rgba(255,255,255,0.5) !important;
    border-color: rgba(130,150,255,0.4) !important;
}

/* ===== 输入框 — 只改背景和边框 ===== */
.stTextInput > div > div,
.stTextArea > div > div,
.stSelectbox > div > div {
    background: var(--surface-input) !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    border-radius: var(--radius-md) !important;
}
.stTextInput > div > div:focus-within,
.stTextArea > div > div:focus-within {
    border-color: var(--primary-light) !important;
    box-shadow: 0 0 0 3px var(--primary-glow) !important;
}
.stTextInput input, .stTextArea textarea { color: #1a1f36 !important; }

/* ===== 文件上传 ===== */
[data-testid="stFileUploader"] { background: transparent !important; }
[data-testid="stFileUploader"] section {
    background: rgba(255,255,255,0.1) !important;
    backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
    border: 1.5px dashed rgba(255,255,255,0.4) !important;
    border-radius: var(--radius-xl) !important; padding: 2rem !important;
}
[data-testid="stFileUploader"] section:hover {
    background: rgba(255,255,255,0.2) !important;
    border-color: var(--primary-light) !important;
}

/* ===== 通知 ===== */
div.stAlert {
    background: rgba(255,255,255,0.16) !important;
    backdrop-filter: blur(22px); -webkit-backdrop-filter: blur(22px);
    border-radius: var(--radius-md) !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
}

/* ===== Spinner / Progress ===== */
.stSpinner > div { border-top-color: var(--primary) !important; }
.stProgress > div > div {
    background: linear-gradient(90deg, #5b6fff, #7555ef) !important;
    border-radius: 100px !important;
}

/* ===== Expander ===== */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.12) !important;
    backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-lg) !important;
}

/* ===== Tabs ===== */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.1) !important;
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border-radius: var(--radius-md) !important; gap: 3px; padding: 3px;
}
.stTabs [data-baseweb="tab"] { border-radius: var(--radius-sm) !important; }
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: rgba(255,255,255,0.3) !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}

/* ===== Radio ===== */
.stRadio > div { flex-direction: row !important; gap: 0 !important; }
.stRadio [data-testid="stRadioOption"] {
    border: 1px solid rgba(255,255,255,0.35) !important;
    padding: 7px 20px !important; margin: 0 !important;
    background: rgba(255,255,255,0.14) !important;
}
.stRadio [data-testid="stRadioOption"]:first-child { border-radius: var(--radius-md) 0 0 var(--radius-md) !important; }
.stRadio [data-testid="stRadioOption"]:last-child  { border-radius: 0 var(--radius-md) var(--radius-md) 0 !important; border-left: none !important; }

/* ===== 导航 ===== */
.nav-container {
    display: flex; gap: 5px; flex-wrap: wrap;
    justify-content: center; padding: 0.4rem 0 0.8rem 0;
    position: relative; z-index: 10;
}

/* ===== 页面标题 ===== */
.page-hero {
    text-align: center; padding: 0.4rem 0 0.2rem 0;
    position: relative; z-index: 5;
}
.page-hero h1 {
    font-size: 1.7rem !important; font-weight: 700 !important;
    background: linear-gradient(135deg, #2a2d42 0%, #5b6fff 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin-bottom: 0.15rem; letter-spacing: -0.02em;
}
.page-hero p { color: #9095ae; font-size: 0.9rem; margin: 0; }

/* ===== 光标光晕 (A) ===== */
#cursor-glow {
    position: fixed; top: -170px; left: -170px;
    width: 340px; height: 340px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255,255,255,0.24) 0%, rgba(91,111,255,0.10) 36%, rgba(125,100,230,0.04) 58%, transparent 74%);
    pointer-events: none; z-index: 9998;
    mix-blend-mode: screen;
    opacity: 0.72;
    transform: translate(-50%, -50%);
    will-change: left, top, opacity;
}

/* ===== 点击涟漪 (C) ===== */
.ripple {
    position: fixed; top: 0; left: 0;
    width: 28px; height: 28px;
    border-radius: 50%;
    pointer-events: none; z-index: 9997;
    transform: translate(-50%, -50%) scale(0);
    opacity: 0;
    border: 1px solid rgba(91,111,255,0.32);
    background: rgba(255,255,255,0.10);
    will-change: transform, opacity;
}
.ripple.go {
    animation: rippleOut 0.58s ease-out forwards;
}
@keyframes rippleOut {
    0%   { transform: translate(-50%, -50%) scale(0);   opacity: 0.42; }
    65%  { opacity: 0.12; }
    100% { transform: translate(-50%, -50%) scale(6);   opacity: 0; }
}

@media (max-width: 760px) {
    #cursor-glow { display: none; }
    .glass-card:hover { transform: none; }
    .block-container { padding-left: 0.8rem !important; padding-right: 0.8rem !important; }
}

@media (prefers-reduced-motion: reduce) {
    #cursor-glow, .ripple { display: none !important; }
    .glass-card, .glass-card-inner, .stButton > button, .stDownloadButton > button {
        animation: none !important;
        transition: none !important;
    }
    .glass-card:hover { transform: none !important; }
}
"""


def apply_theme():
    """注入全局 CSS 主题 + iOS 交互效果（仅调用一次）"""
    st.markdown(f"<style>{THEME_CSS}</style>", unsafe_allow_html=True)
    st.markdown(INTERACTION_JS, unsafe_allow_html=True)


# ============================================================
# iOS 鼠标交互效果：光晕跟随 + 点击涟漪
# ============================================================

INTERACTION_JS = """
<script>
(function() {
    if (window.__iosRippleInstalled) return;
    window.__iosRippleInstalled = true;

    var reducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var coarsePointer = window.matchMedia && window.matchMedia('(pointer: coarse)').matches;
    if (reducedMotion) return;

    // ========== 光标光晕 (A) ==========
    var glow = document.createElement('div');
    glow.id = 'cursor-glow';
    document.body.appendChild(glow);

    var mx = innerWidth / 2, my = innerHeight / 2;  // 目标位置
    var cx = mx, cy = my;                            // 当前渲染位置（lerp）
    var root = document.documentElement;
    var rafPending = false;

    function updateMouseVars(x, y) {
        if (rafPending) return;
        rafPending = true;
        requestAnimationFrame(function() {
            root.style.setProperty('--mouse-x', Math.max(0, Math.min(100, (x / innerWidth) * 100)) + '%');
            root.style.setProperty('--mouse-y', Math.max(0, Math.min(100, (y / innerHeight) * 100)) + '%');
            rafPending = false;
        });
    }

    function lerp() {
        cx += (mx - cx) * 0.12;
        cy += (my - cy) * 0.12;
        if (!coarsePointer) {
            glow.style.left = cx + 'px';
            glow.style.top  = cy + 'px';
        }
        requestAnimationFrame(lerp);
    }
    requestAnimationFrame(lerp);

    window.addEventListener('mousemove', function(e) {
        mx = e.clientX; my = e.clientY;
        updateMouseVars(e.clientX, e.clientY);
    });
    window.addEventListener('touchmove', function(e) {
        if (e.touches.length) {
            mx = e.touches[0].clientX; my = e.touches[0].clientY;
            updateMouseVars(mx, my);
        }
    }, {passive: true});

    if (coarsePointer) {
        glow.style.display = 'none';
    }

    // ========== 点击涟漪 (C) ==========
    var POOL_SIZE = 8;
    var pool = [];
    for (var i = 0; i < POOL_SIZE; i++) {
        var r = document.createElement('div');
        r.className = 'ripple';
        r.addEventListener('animationend', function() {
            this.classList.remove('go');
        });
        document.body.appendChild(r);
        pool.push({ el: r, busy: false });
    }
    var poolIdx = 0;

    function spawnRipple(x, y) {
        if (reducedMotion) return;
        var item = pool[poolIdx];
        poolIdx = (poolIdx + 1) % POOL_SIZE;
        if (item.busy) { item.el.classList.remove('go'); }
        item.busy = true;
        item.el.style.left = x + 'px';
        item.el.style.top  = y + 'px';
        // force reflow so animation restarts
        void item.el.offsetWidth;
        item.el.classList.add('go');
        setTimeout(function() { item.busy = false; }, 620);
    }

    window.addEventListener('click', function(e) {
        spawnRipple(e.clientX, e.clientY);
    });

    // ========== 防止 Streamlit 切页重建 DOM 后丢失 ==========
    var observer = new MutationObserver(function() {
        if (!document.getElementById('cursor-glow')) {
            document.body.appendChild(glow);
        }
        for (var i = 0; i < pool.length; i++) {
            if (!document.body.contains(pool[i].el)) {
                document.body.appendChild(pool[i].el);
            }
        }
    });
    observer.observe(document.body, {childList: true, subtree: false});
})();
</script>
"""


# ============================================================
# 顶部胶囊导航
# ============================================================

NAV_ITEMS = [
    ("📑", "文献摘要梳理"),
    ("📝", "论文框架生成"),
    ("✍️", "论文内容润色"),
    ("📐", "格式校对"),
    ("⚠️", "查重分析提醒"),
    ("🧮", "公式识别与转换"),
]


def render_nav():
    """渲染顶部 iOS 胶囊导航"""
    if "nav_page" not in st.session_state:
        st.session_state.nav_page = 0

    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    cols = st.columns(len(NAV_ITEMS))
    for i, (icon, label) in enumerate(NAV_ITEMS):
        with cols[i]:
            active = st.session_state.nav_page == i
            if st.button(
                f"{icon} {label}",
                key=f"nav_{i}",
                use_container_width=True,
                type="primary" if active else "secondary",
            ):
                if st.session_state.nav_page != i:
                    st.session_state.nav_page = i
                    for k in list(st.session_state.keys()):
                        if k.startswith(("literature_", "outline_", "polish_", "plagiarism_", "format_")):
                            del st.session_state[k]
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# 页面外壳模板
# ============================================================

def render_page_shell(title: str, subtitle: str = ""):
    """统一的页面外壳：渲染页面标题 hero"""
    st.markdown(
        f"""
        <div class="page-hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def glass_card_begin():
    """开始一个玻璃卡片（返回 opening div）"""
    return '<div class="glass-card">'


def glass_card_end():
    """结束玻璃卡片"""
    return '</div>'


def glass_card(title: str = ""):
    """玻璃卡片内容包装器（直接用 st.markdown 包裹）"""
    if title:
        return f'<div class="glass-card"><h3 style="margin-top:0">{title}</h3>'
    return '<div class="glass-card">'


def glass_card_close():
    return '</div>'


def inner_card(title: str = ""):
    """内嵌二级玻璃卡片"""
    if title:
        return f'<div class="glass-card-inner"><h4 style="margin-top:0">{title}</h4>'
    return '<div class="glass-card-inner">'


def inner_card_close():
    return '</div>'
