"""Global dark-only visual theme for ReflectAI's Streamlit interface."""
import streamlit as st


def inject_global_styles() -> None:
    """Apply a consistent dark palette to every page and Streamlit component."""
    st.markdown("""
    <style>
    :root { color-scheme: dark; --bg:#0b1020; --surface:#151f33; --border:#2b3a55; --text:#edf2ff; --muted:#a5b2c9; --accent:#8b9cff; --teal:#48d7c1; }
    html, body, [data-testid="stAppViewContainer"], .stApp { background:var(--bg)!important; color:var(--text)!important; }
    .stApp { background-image:radial-gradient(ellipse at 88% 0%,rgba(74,95,180,.18),transparent 38%),linear-gradient(145deg,#0b1020 0%,#0c1425 55%,#0a1020 100%)!important; }
    [data-testid="stHeader"] { background:rgba(11,16,32,.86)!important; border-bottom:1px solid rgba(43,58,85,.55); }
    .block-container { max-width:1500px; padding-top:1.65rem; padding-bottom:3.2rem; }
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#10182b,#0c1323)!important; border-right:1px solid var(--border); }
    [data-testid="stSidebar"]>div:first-child { background:transparent!important; }
    [data-testid="stSidebar"] [role="radiogroup"] label { border-radius:10px; padding:.35rem .55rem; }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover { background:rgba(139,156,255,.11); }
    h1,h2,h3,h4,h5,h6 { color:var(--text)!important; letter-spacing:-.025em; }
    p,li,label,.stMarkdown,[data-testid="stWidgetLabel"],[data-testid="stMarkdownContainer"] { color:var(--text); }
    [data-testid="stCaptionContainer"],.stCaption,small { color:var(--muted)!important; }
    hr { border-color:var(--border)!important; }
    .stTextInput input,.stTextArea textarea,.stNumberInput input,.stDateInput input,.stTimeInput input,[data-baseweb="select"]>div,[data-baseweb="input"]>div,[data-baseweb="textarea"]>div { background:#0e1729!important;color:var(--text)!important;border-color:#344560!important;border-radius:10px!important; }
    input::placeholder,textarea::placeholder { color:#8190aa!important; }
    [data-baseweb="select"] *,[data-baseweb="popover"] *,[data-baseweb="menu"] * { color:var(--text)!important; }
    [data-baseweb="popover"],[data-baseweb="menu"] { background:var(--surface)!important;border:1px solid var(--border)!important; }
    .stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"] button { min-height:2.55rem;border-radius:10px;border:1px solid #3b4d70;background:#19253b;color:var(--text)!important;font-weight:600;transition:all .15s ease; }
    .stButton>button:hover,.stDownloadButton>button:hover,[data-testid="stFormSubmitButton"] button:hover { border-color:var(--accent)!important;background:#243351!important;transform:translateY(-1px); }
    .stButton>button[kind="primary"],[data-testid="stFormSubmitButton"] button[kind="primary"] { color:white!important;border:0!important;background:linear-gradient(110deg,#6478ff,#8a5cf6)!important;box-shadow:0 5px 18px rgba(100,120,255,.18); }
    [data-testid="stVerticalBlockBorderWrapper"],[data-testid="stExpander"],[data-testid="stForm"],[data-testid="stTable"],[data-testid="stDataFrame"] { border-color:var(--border)!important;border-radius:14px!important; }
    [data-testid="stMetric"] { background:linear-gradient(145deg,#17233a,#111b2e);border:1px solid var(--border);border-radius:13px;padding:14px 16px; }
    [data-testid="stMetricLabel"] { color:var(--muted)!important; } [data-testid="stMetricValue"] { color:var(--text)!important; }
    [data-testid="stExpander"] summary { color:var(--text)!important; } [data-testid="stExpander"] details { background:rgba(18,28,47,.65); }
    [data-baseweb="tab-list"] { gap:.35rem;border-bottom:1px solid var(--border); } [data-baseweb="tab"] { background:transparent!important;color:var(--muted)!important;border-radius:9px 9px 0 0; }
    [aria-selected="true"][data-baseweb="tab"] { color:var(--text)!important;border-bottom-color:var(--accent)!important; }
    [data-testid="stAlert"] { background:#141f33!important;border:1px solid var(--border)!important;border-radius:12px!important; }
    [data-testid="stCode"],pre,code { background:#090f1c!important;border-color:var(--border)!important; }
    a { color:#9aabff!important; } a:hover { color:var(--teal)!important; }
    .stApp [data-testid="stMarkdownContainer"] p,.stApp [data-testid="stMarkdownContainer"] li,.stApp [data-testid="stCaptionContainer"],.stApp label,.stApp [data-testid="stAlert"] { direction:rtl;text-align:right; }
    .stApp textarea,.stApp input { direction:rtl;text-align:right; }
    .stApp pre,.stApp code,.stApp .stCode,.stApp [data-testid="stCode"] { direction:ltr!important;text-align:left!important; }
    @media(max-width:760px){.block-container{padding:1rem .85rem 2rem}h1{font-size:1.75rem!important}}
    </style>
    """, unsafe_allow_html=True)
