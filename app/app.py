import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle, json, os

st.set_page_config(page_title="ChurnIQ", page_icon="🏦", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;700&display=swap');

*, html, body, [class*="css"] { font-family: 'Outfit', sans-serif; margin: 0; padding: 0; box-sizing: border-box; }

/* ── ANIMATED BACKGROUND ── */
.stApp {
    background: #03060f;
    overflow-x: hidden;
}

/* ── ANIMATED GRID BACKGROUND ── */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background-image:
        linear-gradient(rgba(99,102,241,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(99,102,241,0.03) 1px, transparent 1px);
    background-size: 50px 50px;
    animation: gridMove 20s linear infinite;
    pointer-events: none;
    z-index: 0;
}

@keyframes gridMove {
    0% { transform: translateY(0); }
    100% { transform: translateY(50px); }
}

/* ── GLOWING ORBS ── */
.stApp::after {
    content: '';
    position: fixed;
    top: -200px; left: -200px;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);
    animation: orbFloat 8s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
    border-radius: 50%;
}

@keyframes orbFloat {
    0% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(200px, 100px) scale(1.2); }
    100% { transform: translate(100px, 300px) scale(0.9); }
}

/* ── SIDEBAR ── */
div[data-testid="stSidebarContent"] {
    background: rgba(5,8,20,0.95) !important;
    border-right: 1px solid rgba(99,102,241,0.2) !important;
    backdrop-filter: blur(20px);
}

#MainMenu, footer, header { visibility: hidden; }

/* ── GLOWING KPI CARDS ── */
.kpi-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 20px;
    padding: 24px 20px 20px;
    position: relative;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    animation: cardEntrance 0.6s ease backwards;
}

.kpi-card:hover {
    transform: translateY(-8px) scale(1.02);
    border-color: rgba(99,102,241,0.6);
    box-shadow:
        0 20px 60px rgba(99,102,241,0.3),
        0 0 30px rgba(99,102,241,0.15),
        inset 0 0 30px rgba(99,102,241,0.05);
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.1), transparent);
    transition: left 0.6s ease;
}

.kpi-card:hover::before { left: 100%; }

.kpi-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #6366f1, #10b981, #6366f1);
    background-size: 200% 100%;
    animation: shimmer 3s linear infinite;
}

@keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

@keyframes cardEntrance {
    from { opacity: 0; transform: translateY(30px); }
    to   { opacity: 1; transform: translateY(0); }
}

.kpi-card:nth-child(1) { animation-delay: 0.1s; }
.kpi-card:nth-child(2) { animation-delay: 0.2s; }
.kpi-card:nth-child(3) { animation-delay: 0.3s; }
.kpi-card:nth-child(4) { animation-delay: 0.4s; }
.kpi-card:nth-child(5) { animation-delay: 0.5s; }

.kpi-emoji { font-size: 1.6rem; margin-bottom: 10px; display: block; animation: bounce 2s ease-in-out infinite; }
@keyframes bounce { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-5px)} }

.kpi-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #6366f1, #10b981);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    letter-spacing: -1px;
}

.kpi-text {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.3);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 8px;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 16px;
    padding: 5px;
    gap: 3px;
    backdrop-filter: blur(10px);
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.83rem !important;
    color: rgba(255,255,255,0.35) !important;
    border-radius: 12px !important;
    padding: 10px 22px !important;
    border: none !important;
    background: transparent !important;
    transition: all 0.3s ease !important;
    letter-spacing: 0.3px;
}

.stTabs [data-baseweb="tab"]:hover {
    color: rgba(255,255,255,0.7) !important;
    background: rgba(99,102,241,0.1) !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.4), 0 0 40px rgba(99,102,241,0.2) !important;
    transform: scale(1.02) !important;
}

/* ── DIVIDER ── */
.div {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.4), rgba(16,185,129,0.4), transparent);
    margin: 28px 0;
    position: relative;
    overflow: visible;
}

.div::after {
    content: '◆';
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    color: #6366f1;
    font-size: 0.6rem;
    background: #03060f;
    padding: 0 8px;
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
    0%,100% { opacity: 1; transform: translate(-50%,-50%) scale(1); }
    50% { opacity: 0.5; transform: translate(-50%,-50%) scale(1.5); }
}

/* ── RISK BOX ── */
.risk-container {
    border-radius: 20px;
    padding: 32px 28px;
    text-align: center;
    border: 1px solid;
    margin: 10px 0;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}

.risk-container::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: conic-gradient(transparent 0deg, rgba(99,102,241,0.05) 60deg, transparent 120deg);
    animation: rotate 4s linear infinite;
}

@keyframes rotate { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }

.risk-high { background: rgba(239,68,68,0.06); border-color: rgba(239,68,68,0.4); }
.risk-med  { background: rgba(245,158,11,0.06); border-color: rgba(245,158,11,0.4); }
.risk-low  { background: rgba(16,185,129,0.06); border-color: rgba(16,185,129,0.4); }

.risk-num-high {
    font-family:'JetBrains Mono',monospace;
    font-size:3.5rem; font-weight:700; color:#ef4444; line-height:1;
    animation: glowRed 2s ease-in-out infinite alternate;
}
.risk-num-med  {
    font-family:'JetBrains Mono',monospace;
    font-size:3.5rem; font-weight:700; color:#f59e0b; line-height:1;
    animation: glowAmber 2s ease-in-out infinite alternate;
}
.risk-num-low  {
    font-family:'JetBrains Mono',monospace;
    font-size:3.5rem; font-weight:700; color:#10b981; line-height:1;
    animation: glowGreen 2s ease-in-out infinite alternate;
}

@keyframes glowRed   { from{text-shadow:0 0 10px rgba(239,68,68,0.3)}  to{text-shadow:0 0 30px rgba(239,68,68,0.8),0 0 60px rgba(239,68,68,0.4)} }
@keyframes glowAmber { from{text-shadow:0 0 10px rgba(245,158,11,0.3)} to{text-shadow:0 0 30px rgba(245,158,11,0.8),0 0 60px rgba(245,158,11,0.4)} }
@keyframes glowGreen { from{text-shadow:0 0 10px rgba(16,185,129,0.3)} to{text-shadow:0 0 30px rgba(16,185,129,0.8),0 0 60px rgba(16,185,129,0.4)} }

.risk-badge-high { display:inline-block; background:rgba(239,68,68,0.15); color:#ef4444; border:1px solid rgba(239,68,68,0.4); border-radius:100px; padding:6px 20px; font-size:0.85rem; font-weight:700; margin-top:14px; animation: badgePulse 1.5s ease-in-out infinite; }
.risk-badge-med  { display:inline-block; background:rgba(245,158,11,0.15); color:#f59e0b; border:1px solid rgba(245,158,11,0.4); border-radius:100px; padding:6px 20px; font-size:0.85rem; font-weight:700; margin-top:14px; }
.risk-badge-low  { display:inline-block; background:rgba(16,185,129,0.15); color:#10b981; border:1px solid rgba(16,185,129,0.4); border-radius:100px; padding:6px 20px; font-size:0.85rem; font-weight:700; margin-top:14px; }

@keyframes badgePulse {
    0%,100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.4); }
    50%      { box-shadow: 0 0 0 10px rgba(239,68,68,0); }
}

/* ── SECTION HEADERS ── */
.tag {
    display: inline-block;
    font-size: 0.65rem; font-weight: 700; letter-spacing: 3px; text-transform: uppercase;
    color: #6366f1;
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 100px;
    padding: 4px 16px;
    margin-bottom: 10px;
    animation: tagGlow 3s ease-in-out infinite;
}

@keyframes tagGlow {
    0%,100% { box-shadow: 0 0 0 0 rgba(99,102,241,0); }
    50% { box-shadow: 0 0 15px rgba(99,102,241,0.3); }
}

.big-title {
    font-size: 1.6rem; font-weight: 800; color: #ffffff;
    line-height: 1.2; margin-bottom: 22px; letter-spacing: -0.5px;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 14px 28px !important;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.3) !important;
    letter-spacing: 0.5px !important;
    position: relative !important;
    overflow: hidden !important;
}

.stButton > button:hover {
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 10px 40px rgba(99,102,241,0.5), 0 0 60px rgba(99,102,241,0.2) !important;
}

.stButton > button:active {
    transform: scale(0.97) !important;
}

/* ── SLIDERS ── */
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background: linear-gradient(135deg, #6366f1, #10b981) !important;
    box-shadow: 0 0 15px rgba(99,102,241,0.5) !important;
    transition: box-shadow 0.3s ease !important;
}

/* ── SIDEBAR ── */
.sb-brand {
    font-family: 'Outfit', sans-serif;
    font-size: 1.3rem; font-weight: 800; color: #6366f1;
    letter-spacing: 1px;
    text-shadow: 0 0 20px rgba(99,102,241,0.5);
    animation: brandPulse 3s ease-in-out infinite;
}
@keyframes brandPulse {
    0%,100% { text-shadow: 0 0 20px rgba(99,102,241,0.5); }
    50% { text-shadow: 0 0 40px rgba(99,102,241,0.9), 0 0 80px rgba(99,102,241,0.3); }
}

.sb-sub { font-size: 0.7rem; color: rgba(255,255,255,0.2); letter-spacing: 3px; text-transform: uppercase; margin-bottom: 22px; margin-top: 4px; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #03060f; }
::-webkit-scrollbar-thumb { background: linear-gradient(#6366f1, #10b981); border-radius: 10px; }

/* ── DATAFRAME ── */
.stDataFrame { border-radius: 16px; overflow: hidden; border: 1px solid rgba(99,102,241,0.15); }

/* ── INPUT LABELS ── */
.stSlider label, .stSelectbox label, .stNumberInput label { color: rgba(255,255,255,0.5) !important; font-size: 0.83rem !important; font-family: 'Outfit', sans-serif !important; }

/* ── CURSOR TRAIL JS injection ── */
</style>

<script>
// Particle cursor trail
document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.createElement('canvas');
    canvas.style.cssText = 'position:fixed;top:0;left:0;pointer-events:none;z-index:99999;width:100%;height:100%;';
    document.body.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    window.addEventListener('resize', () => { canvas.width = window.innerWidth; canvas.height = window.innerHeight; });

    let particles = [];
    let mouse = { x: 0, y: 0 };

    document.addEventListener('mousemove', (e) => {
        mouse.x = e.clientX; mouse.y = e.clientY;
        for(let i = 0; i < 3; i++) {
            particles.push({
                x: mouse.x, y: mouse.y,
                vx: (Math.random()-0.5)*3, vy: (Math.random()-0.5)*3,
                life: 1, size: Math.random()*4+1,
                color: Math.random() > 0.5 ? '99,102,241' : '16,185,129'
            });
        }
    });

    document.addEventListener('click', (e) => {
        for(let i = 0; i < 30; i++) {
            const angle = (Math.PI*2/30)*i;
            particles.push({
                x: e.clientX, y: e.clientY,
                vx: Math.cos(angle)*6, vy: Math.sin(angle)*6,
                life: 1, size: Math.random()*6+2,
                color: Math.random() > 0.5 ? '99,102,241' : '16,185,129'
            });
        }
    });

    function animate() {
        ctx.clearRect(0,0,canvas.width,canvas.height);
        particles = particles.filter(p => p.life > 0);
        particles.forEach(p => {
            p.x += p.vx; p.y += p.vy;
            p.vx *= 0.95; p.vy *= 0.95;
            p.life -= 0.025;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size * p.life, 0, Math.PI*2);
            ctx.fillStyle = `rgba(${p.color},${p.life})`;
            ctx.shadowBlur = 10;
            ctx.shadowColor = `rgba(${p.color},0.8)`;
            ctx.fill();
        });
        requestAnimationFrame(animate);
    }
    animate();
});
</script>
""", unsafe_allow_html=True)

# ── PATHS ─────────────────────────────────────────────────────────────────────
BASE      = os.path.dirname(os.path.abspath(__file__))
ROOT      = os.path.dirname(BASE)
DATA_PATH = os.path.join(ROOT, "data",   "European_Bank.csv")
MDL_PATH  = os.path.join(ROOT, "models")

CHART = dict(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(3,6,15,0.95)",
             font_color="#94a3b8", font_family="Outfit")
BLUE  = "#6366f1"
GREEN = "#10b981"
RED   = "#ef4444"
AMBER = "#f59e0b"
SEQ   = [BLUE, GREEN, RED, AMBER, "#8b5cf6", "#06b6d4"]

def chl(fig, h=400, **kw):
    fig.update_layout(**CHART, height=h, margin=dict(l=15,r=15,t=40,b=15),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#64748b")),
        xaxis=dict(gridcolor="rgba(255,255,255,0.03)", zerolinecolor="rgba(255,255,255,0.03)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.03)", zerolinecolor="rgba(255,255,255,0.03)"), **kw)
    return fig

@st.cache_resource
def load_models():
    mdls = {}
    for nm, fn in [("Gradient Boosting","gb_model.pkl"),("Random Forest","rf_model.pkl"),
                   ("Decision Tree","dt_model.pkl"),("Logistic Regression","lr_model.pkl")]:
        with open(os.path.join(MDL_PATH, fn),"rb") as f: mdls[nm] = pickle.load(f)
    with open(os.path.join(MDL_PATH,"scaler.pkl"),"rb") as f: sc = pickle.load(f)
    with open(os.path.join(MDL_PATH,"feature_names.json")) as f: feats = json.load(f)
    with open(os.path.join(MDL_PATH,"results.json")) as f: res = json.load(f)
    return mdls, sc, feats, res

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df = df.drop(['CustomerId','Surname','Year'], axis=1)
    df['Balance_Salary_Ratio']   = df['Balance'] / (df['EstimatedSalary'] + 1)
    df['Age_Tenure_Interaction'] = df['Age'] * df['Tenure']
    df['Product_Engagement']     = df['NumOfProducts'] * df['IsActiveMember']
    df['Zero_Balance']           = (df['Balance'] == 0).astype(int)
    return df

MODELS, SCALER, FEATURES, RESULTS = load_models()
df_raw = load_data()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='sb-brand'>⚡ ChurnIQ</div>", unsafe_allow_html=True)
    st.markdown("<div class='sb-sub'>Bank Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='div'></div>", unsafe_allow_html=True)
    geo_filter    = st.multiselect("Geography", ["France","Germany","Spain"], default=["France","Germany","Spain"])
    gender_filter = st.multiselect("Gender", ["Male","Female"], default=["Male","Female"])
    age_range     = st.slider("Age Range", int(df_raw['Age'].min()), int(df_raw['Age'].max()), (18, 80))
    model_choice  = st.selectbox("Prediction Model", list(MODELS.keys()), index=0)
    st.markdown("<div class='div'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.7rem;color:rgba(255,255,255,0.15);text-align:center;letter-spacing:1px;'>BEST MODEL: GRADIENT BOOSTING<br>AUC: 86.84%</div>", unsafe_allow_html=True)

df = df_raw[
    df_raw['Geography'].isin(geo_filter) &
    df_raw['Gender'].isin(gender_filter) &
    df_raw['Age'].between(age_range[0], age_range[1])
].copy()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:50px 0 36px; position:relative;">
    <div style="font-size:0.68rem;font-weight:700;letter-spacing:5px;text-transform:uppercase;
                color:#6366f1;margin-bottom:14px;
                animation:fadeInUp 0.6s ease backwards;">
        ◆ European Central Bank · Predictive Analytics ◆
    </div>
    <div style="font-family:'Outfit',sans-serif;font-size:3.2rem;font-weight:900;
                color:#fff;line-height:1.0;letter-spacing:-2px;
                animation:fadeInUp 0.8s ease 0.1s backwards;">
        Customer Churn
        <span style="background:linear-gradient(90deg,#6366f1,#10b981,#6366f1);
                     background-size:200% 100%;
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                     animation:gradientFlow 3s linear infinite;">
            Risk Intelligence
        </span>
    </div>
    <div style="font-size:0.9rem;color:rgba(255,255,255,0.25);margin-top:14px;font-weight:400;letter-spacing:0.5px;
                animation:fadeInUp 1s ease 0.2s backwards;">
        Predictive Modeling &nbsp;·&nbsp; Risk Scoring &nbsp;·&nbsp; ML-Powered &nbsp;·&nbsp; Real-Time Analysis
    </div>
</div>
<style>
@keyframes fadeInUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
@keyframes gradientFlow { 0%{background-position:0% 50%} 100%{background-position:200% 50%} }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='div'></div>", unsafe_allow_html=True)

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
churn_rate = df['Exited'].mean() * 100
avg_bal    = df[df['Exited']==1]['Balance'].mean()

c1,c2,c3,c4,c5 = st.columns(5)
for col,em,val,lbl in [
    (c1,"👥",f"{len(df):,}","Total Customers"),
    (c2,"🚨",f"{churn_rate:.1f}%","Churn Rate"),
    (c3,"💰",f"${avg_bal:,.0f}","Avg Churner Balance"),
    (c4,"🎯",f"{RESULTS['Gradient Boosting']['ROC-AUC']}%","Best Model AUC"),
    (c5,"🧠","4","ML Models Trained"),
]:
    col.markdown(f"""<div class='kpi-card'>
        <span class='kpi-emoji'>{em}</span>
        <div class='kpi-number'>{val}</div>
        <div class='kpi-text'>{lbl}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
t1,t2,t3,t4 = st.tabs(["  🔮  Risk Calculator  ","  📊  EDA & Insights  ","  🤖  Model Performance  ","  🎮  What-If Simulator  "])

# ════════════════════════════════════
# TAB 1 — RISK CALCULATOR
# ════════════════════════════════════
with t1:
    st.markdown("<div class='tag'>Live Prediction Engine</div>", unsafe_allow_html=True)
    st.markdown("<div class='big-title'>Customer Churn Risk Calculator</div>", unsafe_allow_html=True)

    col_inp, col_out = st.columns([1.2, 1])
    with col_inp:
        st.markdown("##### Enter Customer Profile")
        i1,i2 = st.columns(2)
        credit_score = i1.slider("Credit Score", 350, 850, 650)
        age          = i2.slider("Age", 18, 92, 40)
        i3,i4 = st.columns(2)
        tenure       = i3.slider("Tenure (years)", 0, 10, 5)
        num_products = i4.selectbox("No. of Products", [1,2,3,4], index=1)
        i5,i6 = st.columns(2)
        balance      = i5.number_input("Balance ($)", min_value=0.0, max_value=300000.0, value=60000.0, step=1000.0)
        salary       = i6.number_input("Salary ($)", min_value=0.0, max_value=200000.0, value=100000.0, step=1000.0)
        i7,i8 = st.columns(2)
        geography    = i7.selectbox("Country", ["France","Germany","Spain"])
        gender       = i8.selectbox("Gender", ["Male","Female"])
        i9,i10 = st.columns(2)
        has_cc       = i9.selectbox("Has Credit Card", ["Yes","No"])
        is_active    = i10.selectbox("Active Member", ["Yes","No"])
        predict_btn  = st.button("  ⚡  Predict Churn Risk  ", use_container_width=True)

    with col_out:
        if predict_btn:
            row = {
                'CreditScore': credit_score, 'Age': age, 'Tenure': tenure,
                'Balance': balance, 'NumOfProducts': num_products,
                'HasCrCard': 1 if has_cc=="Yes" else 0,
                'IsActiveMember': 1 if is_active=="Yes" else 0,
                'EstimatedSalary': salary,
                'Balance_Salary_Ratio': balance / (salary + 1),
                'Age_Tenure_Interaction': age * tenure,
                'Product_Engagement': num_products * (1 if is_active=="Yes" else 0),
                'Zero_Balance': 1 if balance == 0 else 0,
                'Geography_France':  1 if geography=="France" else 0,
                'Geography_Germany': 1 if geography=="Germany" else 0,
                'Geography_Spain':   1 if geography=="Spain" else 0,
                'Gender_Female': 1 if gender=="Female" else 0,
                'Gender_Male':   1 if gender=="Male" else 0,
            }
            X_input = pd.DataFrame([row])[FEATURES]
            model = MODELS[model_choice]
            if model_choice == "Logistic Regression":
                prob = model.predict_proba(SCALER.transform(X_input))[0][1]
            else:
                prob = model.predict_proba(X_input)[0][1]
            pct = prob * 100

            if pct >= 60:
                cls, badge = "high", "⚠️ HIGH RISK — Act Now"
            elif pct >= 35:
                cls, badge = "med",  "⚡ MODERATE RISK — Monitor"
            else:
                cls, badge = "low",  "✅ LOW RISK — Stable"

            st.markdown(f"""
            <div class='risk-container risk-{cls}'>
                <div style='font-size:0.65rem;color:rgba(255,255,255,0.3);letter-spacing:3px;text-transform:uppercase;margin-bottom:16px;'>Churn Probability</div>
                <div class='risk-num-{cls}'>{pct:.1f}%</div>
                <div style='font-size:0.72rem;color:rgba(255,255,255,0.25);margin-top:6px;'>via {model_choice}</div>
                <div class='risk-badge-{cls}'>{badge}</div>
            </div>""", unsafe_allow_html=True)

            fig_g = go.Figure(go.Indicator(
                mode="gauge+number", value=pct,
                number={'suffix':"%",'font':{'size':28,'color':'white','family':'JetBrains Mono'}},
                gauge={
                    'axis':{'range':[0,100],'tickcolor':'#1e293b','tickfont':{'color':'#475569'}},
                    'bar':{'color': RED if pct>=60 else AMBER if pct>=35 else GREEN, 'thickness':0.22},
                    'bgcolor':'rgba(0,0,0,0)', 'bordercolor':'rgba(0,0,0,0)',
                    'steps':[
                        {'range':[0,35],'color':'rgba(16,185,129,0.08)'},
                        {'range':[35,60],'color':'rgba(245,158,11,0.08)'},
                        {'range':[60,100],'color':'rgba(239,68,68,0.08)'},
                    ],
                    'threshold':{'line':{'color':'white','width':2},'thickness':0.8,'value':pct}
                }
            ))
            fig_g.update_layout(**CHART, height=230, margin=dict(l=20,r=20,t=20,b=10))
            st.plotly_chart(fig_g, use_container_width=True)
        else:
            st.markdown("""
            <div style='height:440px;display:flex;flex-direction:column;align-items:center;justify-content:center;
                        border:1px dashed rgba(99,102,241,0.2);border-radius:20px;text-align:center;padding:30px;
                        background:rgba(99,102,241,0.02);'>
                <div style='font-size:4rem;margin-bottom:16px;animation:float 3s ease-in-out infinite;'>🔮</div>
                <div style='font-size:1rem;font-weight:600;color:rgba(255,255,255,0.3);'>Fill in customer details</div>
                <div style='font-size:0.8rem;margin-top:8px;color:rgba(255,255,255,0.15);'>Click predict to see churn risk</div>
            </div>
            <style>@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}</style>
            """, unsafe_allow_html=True)

# ════════════════════════════════════
# TAB 2 — EDA
# ════════════════════════════════════
with t2:
    st.markdown("<div class='tag'>Exploratory Analysis</div>", unsafe_allow_html=True)
    st.markdown("<div class='big-title'>Customer Churn Insights</div>", unsafe_allow_html=True)

    r1,r2,r3 = st.columns(3)
    with r1:
        gc = df.groupby('Geography')['Exited'].mean().reset_index()
        gc['Exited'] = (gc['Exited']*100).round(1)
        f = px.bar(gc, x='Geography', y='Exited', color='Geography',
                   color_discrete_sequence=SEQ, text='Exited', title="Churn Rate by Country")
        f.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_line_width=0)
        chl(f, 320, showlegend=False); st.plotly_chart(f, use_container_width=True)
    with r2:
        gen = df.groupby('Gender')['Exited'].mean().reset_index()
        gen['Exited'] = (gen['Exited']*100).round(1)
        f2 = px.pie(gen, values='Exited', names='Gender', color_discrete_sequence=[BLUE,GREEN], title="Churn by Gender", hole=0.5)
        f2.update_layout(**CHART, height=320, margin=dict(l=10,r=10,t=40,b=10), legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#64748b")))
        st.plotly_chart(f2, use_container_width=True)
    with r3:
        pc = df.groupby('NumOfProducts')['Exited'].mean().reset_index()
        pc['Exited'] = (pc['Exited']*100).round(1)
        f3 = px.bar(pc, x='NumOfProducts', y='Exited', color='Exited',
                    color_continuous_scale=[[0,GREEN],[0.5,AMBER],[1,RED]], text='Exited',
                    title="Churn Rate by No. of Products", labels={'NumOfProducts':'Products','Exited':'Churn %'})
        f3.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_line_width=0)
        chl(f3, 320, showlegend=False); f3.update_coloraxes(showscale=False)
        st.plotly_chart(f3, use_container_width=True)

    st.markdown("<div class='div'></div>", unsafe_allow_html=True)
    r4,r5 = st.columns(2)
    with r4:
        f4 = px.histogram(df, x='Age', color='Exited', color_discrete_map={0:BLUE,1:RED},
                          barmode='overlay', opacity=0.75, title="Age Distribution: Churned vs Retained")
        chl(f4, 360); st.plotly_chart(f4, use_container_width=True)
    with r5:
        f5 = px.box(df, x='Exited', y='Balance', color='Exited',
                    color_discrete_map={0:BLUE,1:RED}, title="Balance: Churned vs Retained")
        chl(f5, 360, showlegend=False); st.plotly_chart(f5, use_container_width=True)

    st.markdown("<div class='div'></div>", unsafe_allow_html=True)
    r6,r7 = st.columns(2)
    with r6:
        ac = df.groupby('IsActiveMember')['Exited'].mean().reset_index()
        ac['Label'] = ac['IsActiveMember'].map({0:'Inactive',1:'Active'})
        ac['Exited'] = (ac['Exited']*100).round(1)
        f6 = px.bar(ac, x='Label', y='Exited', color='Label',
                    color_discrete_sequence=[RED,GREEN], text='Exited',
                    title="Active vs Inactive Members", labels={'Exited':'Churn %','Label':''})
        f6.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_line_width=0)
        chl(f6, 320, showlegend=False); st.plotly_chart(f6, use_container_width=True)
    with r7:
        f7 = px.scatter(df.sample(min(2000,len(df))), x='CreditScore', y='EstimatedSalary',
                        color='Exited', color_discrete_map={0:BLUE,1:RED}, opacity=0.5,
                        title="Credit Score vs Salary")
        chl(f7, 320); st.plotly_chart(f7, use_container_width=True)

# ════════════════════════════════════
# TAB 3 — MODEL PERFORMANCE
# ════════════════════════════════════
with t3:
    st.markdown("<div class='tag'>Machine Learning</div>", unsafe_allow_html=True)
    st.markdown("<div class='big-title'>Model Performance Comparison</div>", unsafe_allow_html=True)

    res_df = pd.DataFrame(RESULTS).T.reset_index()
    res_df.columns = ['Model','Accuracy','Precision','Recall','F1','ROC-AUC']

    mc1,mc2 = st.columns(2)
    with mc1:
        fa = px.bar(res_df.sort_values('Accuracy'), x='Accuracy', y='Model', orientation='h',
                    color='Accuracy', color_continuous_scale=[[0,BLUE],[1,GREEN]], text='Accuracy', title="Accuracy (%)")
        fa.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_line_width=0)
        chl(fa, 340); fa.update_layout(yaxis={'categoryorder':'total ascending'}); fa.update_coloraxes(showscale=False)
        st.plotly_chart(fa, use_container_width=True)
    with mc2:
        fu = px.bar(res_df.sort_values('ROC-AUC'), x='ROC-AUC', y='Model', orientation='h',
                    color='ROC-AUC', color_continuous_scale=[[0,BLUE],[1,GREEN]], text='ROC-AUC', title="ROC-AUC Score (%)")
        fu.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_line_width=0)
        chl(fu, 340); fu.update_layout(yaxis={'categoryorder':'total ascending'}); fu.update_coloraxes(showscale=False)
        st.plotly_chart(fu, use_container_width=True)

    st.markdown("<div class='div'></div>", unsafe_allow_html=True)
    mc3,mc4 = st.columns(2)
    with mc3:
        metrics = ['Accuracy','Precision','Recall','F1','ROC-AUC']
        colors_rad = [BLUE, GREEN, AMBER, RED]
        fr = go.Figure()
        for i, (_, row) in enumerate(res_df.iterrows()):
            vals = [row[m] for m in metrics] + [row[metrics[0]]]
            r,g,b = int(colors_rad[i][1:3],16), int(colors_rad[i][3:5],16), int(colors_rad[i][5:7],16)
            fr.add_trace(go.Scatterpolar(
                r=vals, theta=metrics+[metrics[0]], fill='toself', name=row['Model'],
                line=dict(color=colors_rad[i], width=2),
                fillcolor=f"rgba({r},{g},{b},0.08)", opacity=0.9
            ))
        fr.update_layout(**CHART, height=380, polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True, range=[0,100], gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color='#475569')),
            angularaxis=dict(gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color='#94a3b8'))
        ), legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#64748b')))
        st.plotly_chart(fr, use_container_width=True)
    with mc4:
        ff = px.bar(res_df.sort_values('F1'), x='F1', y='Model', orientation='h',
                    color='F1', color_continuous_scale=[[0,RED],[0.5,AMBER],[1,GREEN]],
                    text='F1', title="F1 Score (%)")
        ff.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_line_width=0)
        chl(ff, 380); ff.update_layout(yaxis={'categoryorder':'total ascending'}); ff.update_coloraxes(showscale=False)
        st.plotly_chart(ff, use_container_width=True)

    st.markdown("<div class='div'></div>", unsafe_allow_html=True)
    st.markdown("<div class='big-title'>Feature Importance</div>", unsafe_allow_html=True)
    imp = pd.DataFrame({'Feature': FEATURES, 'Importance': MODELS['Gradient Boosting'].feature_importances_}).sort_values('Importance').tail(12)
    fi = px.bar(imp, x='Importance', y='Feature', orientation='h',
                color='Importance', color_continuous_scale=[[0,BLUE],[1,GREEN]], title="Top Churn Drivers — Gradient Boosting")
    fi.update_traces(marker_line_width=0)
    chl(fi, 420); fi.update_coloraxes(showscale=False)
    st.plotly_chart(fi, use_container_width=True)

    st.markdown("<div class='div'></div>", unsafe_allow_html=True)
    st.dataframe(res_df.set_index('Model'), use_container_width=True)

# ════════════════════════════════════
# TAB 4 — WHAT-IF SIMULATOR
# ════════════════════════════════════
with t4:
    st.markdown("<div class='tag'>Scenario Analysis</div>", unsafe_allow_html=True)
    st.markdown("<div class='big-title'>What-If Churn Simulator</div>", unsafe_allow_html=True)
    st.markdown("<div style='color:rgba(255,255,255,0.3);font-size:0.88rem;margin-bottom:24px;'>Move sliders and watch churn probability change live across all 4 models instantly.</div>", unsafe_allow_html=True)

    w1,w2,w3 = st.columns(3)
    with w1:
        w_age  = st.slider("Age", 18, 92, 40, key='w_age')
        w_bal  = st.slider("Balance ($k)", 0, 300, 60, key='w_bal')
        w_scr  = st.slider("Credit Score", 350, 850, 650, key='w_scr')
    with w2:
        w_prod = st.selectbox("No. of Products", [1,2,3,4], index=1, key='w_prod')
        w_ten  = st.slider("Tenure (years)", 0, 10, 5, key='w_ten')
        w_sal  = st.slider("Salary ($k)", 10, 200, 100, key='w_sal')
    with w3:
        w_geo  = st.selectbox("Country", ["France","Germany","Spain"], key='w_geo')
        w_act  = st.selectbox("Active Member", ["Yes","No"], key='w_act')
        w_gen  = st.selectbox("Gender", ["Male","Female"], key='w_gen')

    bal, sal = w_bal*1000, w_sal*1000
    row = {
        'CreditScore': w_scr, 'Age': w_age, 'Tenure': w_ten, 'Balance': bal,
        'NumOfProducts': w_prod, 'HasCrCard': 1, 'IsActiveMember': 1 if w_act=="Yes" else 0,
        'EstimatedSalary': sal, 'Balance_Salary_Ratio': bal/(sal+1),
        'Age_Tenure_Interaction': w_age*w_ten, 'Product_Engagement': w_prod*(1 if w_act=="Yes" else 0),
        'Zero_Balance': 1 if bal==0 else 0,
        'Geography_France': 1 if w_geo=="France" else 0,
        'Geography_Germany': 1 if w_geo=="Germany" else 0,
        'Geography_Spain': 1 if w_geo=="Spain" else 0,
        'Gender_Female': 1 if w_gen=="Female" else 0, 'Gender_Male': 1 if w_gen=="Male" else 0,
    }
    X_sim = pd.DataFrame([row])[FEATURES]
    probs = {}
    for nm, mdl in MODELS.items():
        probs[nm] = round(mdl.predict_proba(SCALER.transform(X_sim) if nm=="Logistic Regression" else X_sim)[0][1]*100, 1)

    st.markdown("<div class='div'></div>", unsafe_allow_html=True)
    sc1,sc2,sc3,sc4 = st.columns(4)
    for (nm,prob),col in zip(probs.items(),[ sc1,sc2,sc3,sc4]):
        cls = "high" if prob>=60 else "med" if prob>=35 else "low"
        col.markdown(f"""<div class='risk-container risk-{cls}' style='padding:20px 15px;'>
            <div style='font-size:0.6rem;color:rgba(255,255,255,0.25);letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;'>{nm}</div>
            <div class='risk-num-{cls}' style='font-size:2.2rem;'>{prob}%</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    prob_df = pd.DataFrame({'Model':list(probs.keys()),'Churn Probability %':list(probs.values())})
    fsim = px.bar(prob_df, x='Model', y='Churn Probability %',
                  color='Churn Probability %',
                  color_continuous_scale=[[0,GREEN],[0.35,AMBER],[0.6,RED],[1,RED]],
                  text='Churn Probability %', title="Live Churn Probability — All Models")
    fsim.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_line_width=0)
    fsim.add_hline(y=50, line_dash="dash", line_color="rgba(255,255,255,0.15)", annotation_text="50% Decision Threshold", annotation_font_color="#64748b")
    chl(fsim, 380); fsim.update_coloraxes(showscale=False)
    st.plotly_chart(fsim, use_container_width=True)

    st.markdown("<div class='div'></div>", unsafe_allow_html=True)
    st.markdown("##### How Balance Affects Churn Risk")
    bal_range = list(range(0, 260000, 10000))
    gb = MODELS['Gradient Boosting']
    sens = []
    for b in bal_range:
        r2 = row.copy(); r2['Balance']=b; r2['Balance_Salary_Ratio']=b/(sal+1); r2['Zero_Balance']=1 if b==0 else 0
        sens.append(round(gb.predict_proba(pd.DataFrame([r2])[FEATURES])[0][1]*100,1))
    fsen = px.area(x=[b/1000 for b in bal_range], y=sens,
                   labels={'x':'Balance ($k)','y':'Churn Probability %'}, title="Balance vs Churn Risk Sensitivity")
    fsen.update_traces(line=dict(color=BLUE, width=2.5), fillcolor='rgba(99,102,241,0.1)')
    fsen.add_hline(y=50, line_dash="dash", line_color="rgba(239,68,68,0.4)", annotation_text="50% Threshold", annotation_font_color="#64748b")
    chl(fsen, 380)
    st.plotly_chart(fsen, use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("<div class='div'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;padding:16px 0 30px;font-size:0.7rem;
            color:rgba(255,255,255,0.1);letter-spacing:2px;">
    ⚡ CHURNIQ &nbsp;·&nbsp; EUROPEAN CENTRAL BANK &nbsp;·&nbsp; UNIFIED MENTOR &nbsp;·&nbsp; AYUSH PRAKASH G
</div>
""", unsafe_allow_html=True)
