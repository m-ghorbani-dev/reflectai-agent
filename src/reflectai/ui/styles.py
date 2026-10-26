"""Global dark-only theme and lightweight UI polish for ReflectAI."""
import streamlit as st


def inject_global_styles() -> None:
    st.markdown(r"""
    <style>
    :root { color-scheme: dark; --rai-bg:#0b1020; --rai-panel:#111b2e; --rai-card:#17233a; --rai-line:#2b3a55; --rai-text:#edf2ff; --rai-muted:#a5b2c9; --rai-accent:#8b9cff; --rai-teal:#48d7c1; --rai-danger:#ff6b81; }
    html,body,[data-testid="stAppViewContainer"],.stApp { background:var(--rai-bg)!important; color:var(--rai-text)!important; }
    .stApp { background-image:radial-gradient(ellipse at 88% 0%,rgba(74,95,180,.18),transparent 38%),linear-gradient(145deg,#0b1020 0%,#0c1425 55%,#0a1020 100%)!important; }
    [data-testid="stHeader"] { background:rgba(11,16,32,.88)!important; border-bottom:1px solid rgba(43,58,85,.55); }
    [data-testid="stToolbar"],[data-testid="stDecoration"] { color:var(--rai-muted); }
    .block-container { max-width:1500px; padding-top:1.55rem; padding-bottom:3rem; }
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#10182b,#0c1323)!important; border-right:1px solid var(--rai-line); }
    [data-testid="stSidebar"]>div:first-child { background:transparent!important; }
    .rai-brand { display:flex; align-items:center; gap:12px; padding:10px 4px 20px; }
    .rai-brand-icon { display:grid; place-items:center; width:42px; height:42px; border-radius:13px; color:white; font-weight:800; font-size:21px; background:linear-gradient(135deg,#6478ff,#965cf5); box-shadow:0 8px 22px #6478ff35; }
    .rai-brand strong { display:block; font-size:19px; color:var(--rai-text); letter-spacing:-.04em; }
    .rai-brand small { display:block; color:var(--rai-muted); font-size:11px; margin-top:3px; }
    .rai-sidebar-label { color:#7183a2; font-size:10px; font-weight:700; letter-spacing:.16em; margin:5px 0 10px; }
    .rai-sidebar-footer { display:flex; align-items:center; gap:8px; color:var(--rai-muted); font-size:12px; }
    .rai-live-dot { display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--rai-teal); box-shadow:0 0 0 4px #48d7c11a; margin-right:7px; }
    .rai-trace-card { border:1px solid var(--rai-line); background:linear-gradient(145deg,#17233a,#111b2e); border-radius:12px; padding:12px; min-height:78px; }
    .rai-model-row,.rai-provider-card { background:linear-gradient(145deg,#17233a,#111b2e); border:1px solid var(--rai-line); border-radius:13px; padding:13px 15px; margin:8px 0; }
    .rai-model-row { display:flex; align-items:center; gap:6px; }
    .rai-pill { display:inline-block; margin-left:auto; border:1px solid #38566b; border-radius:999px; padding:3px 8px; color:var(--rai-teal); font-size:11px; }
    .rai-provider-card { min-height:95px; }
    .rai-provider-card strong { margin-left:6px; }
    .rai-provider-card small { display:block; margin-top:10px; color:var(--rai-muted); overflow-wrap:anywhere; }
    .rai-status-dot { display:inline-block; width:8px; height:8px; border-radius:50%; }
    .rai-status-ok { background:var(--rai-teal); }.rai-status-off { background:#748098; }
    h1,h2,h3,h4,h5,h6 { color:var(--rai-text)!important; letter-spacing:-.025em; }
    p,li,label,.stMarkdown,[data-testid="stWidgetLabel"],[data-testid="stMarkdownContainer"] { color:var(--rai-text); }
    [data-testid="stCaptionContainer"],.stCaption,small { color:var(--rai-muted)!important; }
    hr { border-color:var(--rai-line)!important; }
    .stTextInput input,.stTextArea textarea,.stNumberInput input,.stDateInput input,.stTimeInput input,[data-baseweb="select"]>div,[data-baseweb="input"]>div,[data-baseweb="textarea"]>div { background:#0e1729!important; color:var(--rai-text)!important; border-color:#344560!important; border-radius:10px!important; }
    input::placeholder,textarea::placeholder { color:#8190aa!important; }
    [data-baseweb="popover"],[data-baseweb="menu"] { background:#151f33!important; border:1px solid var(--rai-line)!important; }
    [data-baseweb="popover"] *,[data-baseweb="menu"] * { color:var(--rai-text)!important; }
    .stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"] button { min-height:2.5rem; border-radius:10px; border:1px solid #3b4d70; background:#19253b; color:var(--rai-text)!important; font-weight:600; transition:transform .15s ease,border-color .15s ease,background .15s ease; }
    .stButton>button:hover,.stDownloadButton>button:hover,[data-testid="stFormSubmitButton"] button:hover { border-color:var(--rai-accent)!important; background:#243351!important; transform:translateY(-1px); }
    .stButton>button[kind="primary"],[data-testid="stFormSubmitButton"] button[kind="primary"] { color:white!important; border:0!important; background:linear-gradient(110deg,#6478ff,#8a5cf6)!important; box-shadow:0 5px 18px #6478ff2e; }
    .stButton>button:disabled { opacity:.48; }
    [data-testid="stVerticalBlockBorderWrapper"],[data-testid="stExpander"],[data-testid="stForm"],[data-testid="stTable"],[data-testid="stDataFrame"] { border-color:var(--rai-line)!important; border-radius:14px!important; }
    [data-testid="stMetric"] { background:linear-gradient(145deg,#17233a,#111b2e); border:1px solid var(--rai-line); border-radius:13px; padding:13px 15px; }
    [data-testid="stMetricLabel"] { color:var(--rai-muted)!important; } [data-testid="stMetricValue"] { color:var(--rai-text)!important; }
    [data-testid="stExpander"] summary { color:var(--rai-text)!important; }
    [data-baseweb="tab-list"] { gap:.35rem; border-bottom:1px solid var(--rai-line); }
    [data-baseweb="tab"] { background:transparent!important; color:var(--rai-muted)!important; border-radius:9px 9px 0 0; }
    [aria-selected="true"][data-baseweb="tab"] { color:var(--rai-text)!important; border-bottom-color:var(--rai-accent)!important; }
    [data-testid="stAlert"] { background:#141f33!important; border:1px solid var(--rai-line)!important; border-radius:12px!important; }
    pre,code,[data-testid="stCode"] { background:#090f1c!important; border-color:var(--rai-line)!important; }
    a { color:#9aabff!important; } a:hover { color:var(--rai-teal)!important; }
    .stApp [data-testid="stMarkdownContainer"] p,.stApp [data-testid="stMarkdownContainer"] li,.stApp [data-testid="stCaptionContainer"],.stApp label,.stApp [data-testid="stAlert"] { direction:rtl; text-align:right; }
    .stApp textarea,.stApp input { direction:rtl; text-align:right; }
    .stApp pre,.stApp code,.stApp .stCode,.stApp [data-testid="stCode"] { direction:ltr!important; text-align:left!important; }
    @media(max-width:760px) { .block-container { padding:1rem .85rem 2rem; } h1 { font-size:1.75rem!important; } }
    </style>
    """, unsafe_allow_html=True)
