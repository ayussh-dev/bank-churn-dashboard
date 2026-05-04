import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle, json, os

st.set_page_config(page_title="ChurnIQ — Bank Intelligence", page_icon="🏦", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

.stApp {
    background-color: #060910;
    background-image:
        radial-gradient(ellipse 900px 600px at 0% 0%, rgba(99,102,241,0.12) 0%, transparent 70%),
        radial-gradient(ellipse 700px 500px at 100% 100%, rgba(16,185,129,0.08) 0%, transparent 70%),
        radial-gradient(ellipse 500px 400px at 50% 50%, rgba(239,68,68,0.04) 0%, transparent 60%);
}

div[data-testid="stSidebarContent"] {
    background: linear-gradient(180deg, #080b14 0%, #060910 100%) !important;
    border-right: 1px solid rgba(99,102,241,0.15) !important;
}

#MainMenu, footer, header { visibility: hidden; }

/* KPI CARDS */
.kpi-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 20px;
    padding: 24px 20px 20px;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(10px);
}
.kpi-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #10b981);
    border-radius: 20px 20px 0 0;
}
.kpi-emoji { font-size: 1.6rem; margin-bottom: 10px; display: block; }
.kpi-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2.1rem;
    font-weight: 700;
    background: linear-gradient(135deg, #6366f1, #10b981);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    letter-spacing: -1px;
}
.kpi-text {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.35);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 8px;
    font-weight: 500;
}

/* SECTION HEADERS */
.tag {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #6366f1;
    background: rgba(99,102,241,0.1);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 100px;
    padding: 4px 14px;
    margin-bottom: 10px;
}
.big-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.2;
    margin-bottom: 22px;
    letter-spacing: -0.5px;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 14px;
    padding: 5px;
    gap: 3px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 0.83rem;
    color: rgba(255,255,255,0.4) !important;
    border-radius: 10px !important;
    padding: 9px 20px !important;
    border: none !important;
    background: transparent !important;
    letter-spacing: 0.3px;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.35) !important;
}

/* DIVIDER */
.div { height: 1px; background: linear-gradient(90deg, transparent, rgba(99,102,241,0.25), transparent); margin: 28px 0; }

/* RISK METER */
.risk-container {
    border-radius: 20px;
    padding: 32px 28px;
    text-align: center;
    position: relative;
    overflow: hidden;
    border: 1px solid;
    margin: 10px 0;
}
.risk-high { background: rgba(239,68,68,0.08); border-color: rgba(239,68,68,0.35); }
.risk-med  { background: rgba(245,158,11,0.08); border-color: rgba(245,158,11,0.35); }
.risk-low  { background: rgba(16,185,129,0.08); border-color: rgba(16,185,129,0.35); }
.risk-num-high { font-family:'JetBrains Mono',monospace; font-size:3.5rem; font-weight:700; color:#ef4444; line-height:1; }
.risk-num-med  { font-family:'JetBrains Mono',monospace; font-size:3.5rem; font-weight:700; color:#f59e0b; line-height:1; }
.risk-num-low  { font-family:'JetBrains Mono',monospace; font-size:3.5rem; font-weight:700; color:#10b981; line-height:1; }
.risk-label { font-size:0.8rem; color:rgba(255,255,255,0.4); text-transform:uppercase; letter-spacing:2px; margin-top:10px; }
.risk-badge-high { display:inline-block; background:rgba(239,68,68,0.15); color:#ef4444; border:1px solid rgba(239,68,68,0.3); border-radius:100px; padding:5px 18px; font-size:0.85rem; font-weight:600; margin-top:12px; }
.risk-badge-med  { display:inline-block; background:rgba(245,158,11,0.15); color:#f59e0b; border:1px solid rgba(245,158,11,0.3); border-radius:100px; padding:5px 18px; font-size:0.85rem; font-weight:600; margin-top:12px; }
.risk-badge-low  { display:inline-block; background:rgba(16,185,129,0.15); color:#10b981; border:1px solid rgba(16,185,129,0.3); border-radius:100px; padding:5px 18px; font-size:0.85rem; font-weight:600; margin-top:12px; }

/* SIDEBAR */
.sb-brand { font-family:'Space Grotesk',sans-serif; font-size:1.15rem; font-weight:700; color:#6366f1; letter-spacing:0.5px; }
.sb-sub { font-size:0.7rem; color:rgba(255,255,255,0.25); letter-spacing:2.5px; text-transform:uppercase; margin-bottom:22px; margin-top:2px; }

/* INPUT LABELS */
.stSlider label, .stSelectbox label, .stRadio label { color: rgba(255,255,255,0.6) !important; font-size: 0.85rem !important; }

/* SCROLLBAR */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #060910; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.4); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── PATHS ─────────────────────────────────────────────────────────────────────
BASE       = os.path.dirname(os.path.abspath(__file__))
ROOT       = os.path.dirname(BASE)
DATA_PATH  = os.path.join(ROOT, "data",   "European_Bank.csv")
MDL_PATH   = os.path.join(ROOT, "models")

CHART = dict(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(8,11,20,0.95)",
             font_color="#94a3b8", font_family="Space Grotesk")
BLUE  = "#6366f1"
GREEN = "#10b981"
RED   = "#ef4444"
AMBER = "#f59e0b"
SEQ   = [BLUE, GREEN, RED, AMBER, "#8b5cf6", "#06b6d4"]

def chl(fig, h=400, **kw):
    fig.update_layout(**CHART, height=h, margin=dict(l=15,r=15,t=40,b=15),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#64748b")),
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", zerolinecolor="rgba(255,255,255,0.04)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", zerolinecolor="rgba(255,255,255,0.04)"), **kw)
    return fig

# ── LOAD ──────────────────────────────────────────────────────────────────────
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
    df['Balance_Salary_Ratio']  = df['Balance'] / (df['EstimatedSalary'] + 1)
    df['Age_Tenure_Interaction'] = df['Age'] * df['Tenure']
    df['Product_Engagement']    = df['NumOfProducts'] * df['IsActiveMember']
    df['Zero_Balance']          = (df['Balance'] == 0).astype(int)
    return df

MODELS, SCALER, FEATURES, RESULTS = load_models()
df_raw = load_data()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='sb-brand'>🏦 ChurnIQ</div>", unsafe_allow_html=True)
    st.markdown("<div class='sb-sub'>Bank Churn Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='div'></div>", unsafe_allow_html=True)

    geo_filter    = st.multiselect("Geography", options=["France","Germany","Spain"], default=["France","Germany","Spain"])
    gender_filter = st.multiselect("Gender",    options=["Male","Female"],           default=["Male","Female"])
    age_range     = st.slider("Age Range", int(df_raw['Age'].min()), int(df_raw['Age'].max()), (18, 80))
    model_choice  = st.selectbox("Prediction Model", options=list(MODELS.keys()), index=0)

    st.markdown("<div class='div'></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.72rem;color:rgba(255,255,255,0.2);letter-spacing:1px;text-align:center;'>BEST MODEL: GRADIENT BOOSTING<br>AUC: 86.84%</div>", unsafe_allow_html=True)

# ── FILTER ────────────────────────────────────────────────────────────────────
df = df_raw[
    df_raw['Geography'].isin(geo_filter) &
    df_raw['Gender'].isin(gender_filter) &
    df_raw['Age'].between(age_range[0], age_range[1])
].copy()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:44px 0 32px;">
    <div style="font-size:0.68rem;font-weight:700;letter-spacing:4px;text-transform:uppercase;
                color:#6366f1;margin-bottom:12px;">European Central Bank · Predictive Analytics</div>
    <div style="font-family:'Space Grotesk',sans-serif;font-size:3rem;font-weight:700;
                color:#fff;line-height:1.05;letter-spacing:-1.5px;">
        Customer Churn<br>
        <span style="background:linear-gradient(90deg,#6366f1,#10b981);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            Risk Intelligence
        </span>
    </div>
    <div style="font-size:0.88rem;color:rgba(255,255,255,0.3);margin-top:14px;font-weight:400;letter-spacing:0.2px;">
        Predictive Modeling · Risk Scoring · Churn Prevention · ML-Powered Insights
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='div'></div>", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
churn_rate = df['Exited'].mean() * 100
avg_bal    = df[df['Exited']==1]['Balance'].mean()
top_model_auc = RESULTS['Gradient Boosting']['ROC-AUC']

c1,c2,c3,c4,c5 = st.columns(5)
for col,em,val,lbl in [
    (c1,"👥",f"{len(df):,}","Customers"),
    (c2,"🚨",f"{churn_rate:.1f}%","Churn Rate"),
    (c3,"💰",f"${avg_bal:,.0f}","Avg Churner Balance"),
    (c4,"🎯",f"{top_model_auc}%","Best Model AUC"),
    (c5,"🧠","4","ML Models Trained"),
]:
    col.markdown(f"""<div class='kpi-card'>
        <span class='kpi-emoji'>{em}</span>
        <div class='kpi-number'>{val}</div>
        <div class='kpi-text'>{lbl}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
t1,t2,t3,t4 = st.tabs([
    "  🔮  Risk Calculator  ",
    "  📊  EDA & Insights  ",
    "  🤖  Model Performance  ",
    "  🎮  What-If Simulator  ",
])

# ════════════════════════════════════════════════════════
# TAB 1 — RISK CALCULATOR
# ════════════════════════════════════════════════════════
with t1:
    st.markdown("<div class='tag'>Customer Risk Profile</div>", unsafe_allow_html=True)
    st.markdown("<div class='big-title'>Churn Risk Calculator</div>", unsafe_allow_html=True)

    col_inp, col_out = st.columns([1.2, 1])

    with col_inp:
        st.markdown("##### Enter Customer Details")
        i1,i2 = st.columns(2)
        credit_score  = i1.slider("Credit Score",   350, 850, 650)
        age           = i2.slider("Age",            18,  92,  40)
        i3,i4 = st.columns(2)
        tenure        = i3.slider("Tenure (years)", 0,   10,  5)
        num_products  = i4.selectbox("Num of Products", [1,2,3,4], index=1)
        i5,i6 = st.columns(2)
        balance       = i5.number_input("Account Balance ($)", min_value=0.0, max_value=300000.0, value=60000.0, step=1000.0)
        salary        = i6.number_input("Estimated Salary ($)", min_value=0.0, max_value=200000.0, value=100000.0, step=1000.0)
        i7,i8 = st.columns(2)
        geography     = i7.selectbox("Geography",       ["France","Germany","Spain"])
        gender        = i8.selectbox("Gender",          ["Male","Female"])
        i9,i10 = st.columns(2)
        has_cc        = i9.selectbox("Has Credit Card", ["Yes","No"])
        is_active     = i10.selectbox("Active Member",  ["Yes","No"])

        predict_btn = st.button("  🔮  Predict Churn Risk  ", use_container_width=True)

    with col_out:
        if predict_btn:
            row = {
                'CreditScore':    credit_score,
                'Age':            age,
                'Tenure':         tenure,
                'Balance':        balance,
                'NumOfProducts':  num_products,
                'HasCrCard':      1 if has_cc=="Yes" else 0,
                'IsActiveMember': 1 if is_active=="Yes" else 0,
                'EstimatedSalary': salary,
                'Balance_Salary_Ratio':   balance / (salary + 1),
                'Age_Tenure_Interaction': age * tenure,
                'Product_Engagement':     num_products * (1 if is_active=="Yes" else 0),
                'Zero_Balance':           1 if balance == 0 else 0,
                'Geography_France':  1 if geography=="France" else 0,
                'Geography_Germany': 1 if geography=="Germany" else 0,
                'Geography_Spain':   1 if geography=="Spain" else 0,
                'Gender_Female': 1 if gender=="Female" else 0,
                'Gender_Male':   1 if gender=="Male" else 0,
            }
            X_input = pd.DataFrame([row])[FEATURES]

            model = MODELS[model_choice]
            if model_choice == "Logistic Regression":
                X_input_sc = SCALER.transform(X_input)
                prob = model.predict_proba(X_input_sc)[0][1]
            else:
                prob = model.predict_proba(X_input)[0][1]

            pct = prob * 100

            if pct >= 60:
                cls, num_cls, badge = "high", "high", "⚠️ HIGH RISK — Immediate Action Required"
            elif pct >= 35:
                cls, num_cls, badge = "med",  "med",  "⚡ MODERATE RISK — Monitor Closely"
            else:
                cls, num_cls, badge = "low",  "low",  "✅ LOW RISK — Customer Likely to Stay"

            st.markdown(f"""
            <div class='risk-container risk-{cls}'>
                <div style='font-size:0.7rem;color:rgba(255,255,255,0.35);letter-spacing:3px;text-transform:uppercase;margin-bottom:16px;'>Churn Probability</div>
                <div class='risk-num-{num_cls}'>{pct:.1f}%</div>
                <div style='font-size:0.72rem;color:rgba(255,255,255,0.3);margin-top:6px;'>Using {model_choice}</div>
                <div class='risk-badge-{cls}'>{badge}</div>
            </div>
            """, unsafe_allow_html=True)

            # Gauge chart
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=pct,
                domain={'x':[0,1],'y':[0,1]},
                number={'suffix':"%",'font':{'size':28,'color':'white','family':'JetBrains Mono'}},
                gauge={
                    'axis':{'range':[0,100],'tickcolor':'#334155','tickfont':{'color':'#64748b'}},
                    'bar':{'color': RED if pct>=60 else AMBER if pct>=35 else GREEN, 'thickness':0.25},
                    'bgcolor':'rgba(0,0,0,0)',
                    'bordercolor':'rgba(0,0,0,0)',
                    'steps':[
                        {'range':[0,35],'color':'rgba(16,185,129,0.12)'},
                        {'range':[35,60],'color':'rgba(245,158,11,0.12)'},
                        {'range':[60,100],'color':'rgba(239,68,68,0.12)'},
                    ],
                    'threshold':{'line':{'color':'white','width':2},'thickness':0.8,'value':pct}
                }
            ))
            fig_gauge.update_layout(**CHART, height=240, margin=dict(l=20,r=20,t=20,b=10))
            st.plotly_chart(fig_gauge, use_container_width=True)

        else:
            st.markdown("""
            <div style='height:420px;display:flex;flex-direction:column;align-items:center;
                        justify-content:center;border:1px dashed rgba(99,102,241,0.2);
                        border-radius:20px;color:rgba(255,255,255,0.2);text-align:center;padding:30px;'>
                <div style='font-size:3rem;margin-bottom:16px;'>🔮</div>
                <div style='font-size:1rem;font-weight:600;color:rgba(255,255,255,0.3);'>Fill in customer details</div>
                <div style='font-size:0.8rem;margin-top:8px;'>and click Predict to see churn risk</div>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# TAB 2 — EDA & INSIGHTS
# ════════════════════════════════════════════════════════
with t2:
    st.markdown("<div class='tag'>Exploratory Analysis</div>", unsafe_allow_html=True)
    st.markdown("<div class='big-title'>Customer Churn Insights</div>", unsafe_allow_html=True)

    r1c1, r1c2, r1c3 = st.columns(3)

    with r1c1:
        geo_churn = df.groupby('Geography')['Exited'].mean().reset_index()
        geo_churn.columns = ['Geography','Churn Rate']
        geo_churn['Churn Rate'] = (geo_churn['Churn Rate']*100).round(1)
        fig = px.bar(geo_churn, x='Geography', y='Churn Rate', color='Geography',
                     color_discrete_sequence=SEQ, text='Churn Rate', title="Churn Rate by Geography")
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_line_width=0)
        chl(fig, 320, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with r1c2:
        gen_churn = df.groupby('Gender')['Exited'].mean().reset_index()
        gen_churn['Exited'] = (gen_churn['Exited']*100).round(1)
        fig2 = px.pie(gen_churn, values='Exited', names='Gender',
                      color_discrete_sequence=[BLUE, GREEN], title="Churn by Gender", hole=0.5)
        fig2.update_layout(**CHART, height=320, margin=dict(l=10,r=10,t=40,b=10),
                           legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#64748b")))
        st.plotly_chart(fig2, use_container_width=True)

    with r1c3:
        prod_churn = df.groupby('NumOfProducts')['Exited'].mean().reset_index()
        prod_churn['Exited'] = (prod_churn['Exited']*100).round(1)
        fig3 = px.bar(prod_churn, x='NumOfProducts', y='Exited',
                      color='Exited', color_continuous_scale=[[0,GREEN],[0.5,AMBER],[1,RED]],
                      text='Exited', title="Churn Rate by No. of Products",
                      labels={'NumOfProducts':'Products','Exited':'Churn Rate %'})
        fig3.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_line_width=0)
        chl(fig3, 320, showlegend=False)
        fig3.update_coloraxes(showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<div class='div'></div>", unsafe_allow_html=True)
    r2c1, r2c2 = st.columns(2)

    with r2c1:
        fig4 = px.histogram(df, x='Age', color='Exited',
                            color_discrete_map={0: BLUE, 1: RED},
                            barmode='overlay', opacity=0.75,
                            title="Age Distribution: Churned vs Retained",
                            labels={'Exited':'Churned'})
        fig4.update_layout(legend=dict(title='Churned'))
        chl(fig4, 360)
        st.plotly_chart(fig4, use_container_width=True)

    with r2c2:
        fig5 = px.box(df, x='Exited', y='Balance', color='Exited',
                      color_discrete_map={0:BLUE, 1:RED},
                      title="Account Balance: Churned vs Retained",
                      labels={'Exited':'Churned (1=Yes)'})
        chl(fig5, 360, showlegend=False)
        st.plotly_chart(fig5, use_container_width=True)

    st.markdown("<div class='div'></div>", unsafe_allow_html=True)

    r3c1, r3c2 = st.columns(2)
    with r3c1:
        active_churn = df.groupby('IsActiveMember')['Exited'].mean().reset_index()
        active_churn['Label'] = active_churn['IsActiveMember'].map({0:'Inactive',1:'Active'})
        active_churn['Exited'] = (active_churn['Exited']*100).round(1)
        fig6 = px.bar(active_churn, x='Label', y='Exited', color='Label',
                      color_discrete_sequence=[RED, GREEN], text='Exited',
                      title="Churn Rate: Active vs Inactive Members",
                      labels={'Exited':'Churn Rate %', 'Label':''})
        fig6.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_line_width=0)
        chl(fig6, 320, showlegend=False)
        st.plotly_chart(fig6, use_container_width=True)

    with r3c2:
        fig7 = px.scatter(df.sample(min(2000,len(df))), x='CreditScore', y='EstimatedSalary',
                          color='Exited', color_discrete_map={0:BLUE,1:RED},
                          opacity=0.5, title="Credit Score vs Salary (Colored by Churn)",
                          labels={'Exited':'Churned'})
        chl(fig7, 320)
        st.plotly_chart(fig7, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 3 — MODEL PERFORMANCE
# ════════════════════════════════════════════════════════
with t3:
    st.markdown("<div class='tag'>Machine Learning</div>", unsafe_allow_html=True)
    st.markdown("<div class='big-title'>Model Performance Comparison</div>", unsafe_allow_html=True)

    res_df = pd.DataFrame(RESULTS).T.reset_index()
    res_df.columns = ['Model','Accuracy','Precision','Recall','F1','ROC-AUC']

    mc1, mc2 = st.columns(2)
    with mc1:
        fig_acc = px.bar(res_df.sort_values('Accuracy'), x='Accuracy', y='Model',
                         orientation='h', color='Accuracy',
                         color_continuous_scale=[[0,BLUE],[1,GREEN]],
                         text='Accuracy', title="Accuracy (%)")
        fig_acc.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_line_width=0)
        chl(fig_acc, 340)
        fig_acc.update_layout(yaxis={'categoryorder':'total ascending'})
        fig_acc.update_coloraxes(showscale=False)
        st.plotly_chart(fig_acc, use_container_width=True)

    with mc2:
        fig_auc = px.bar(res_df.sort_values('ROC-AUC'), x='ROC-AUC', y='Model',
                         orientation='h', color='ROC-AUC',
                         color_continuous_scale=[[0,BLUE],[1,GREEN]],
                         text='ROC-AUC', title="ROC-AUC Score (%)")
        fig_auc.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_line_width=0)
        chl(fig_auc, 340)
        fig_auc.update_layout(yaxis={'categoryorder':'total ascending'})
        fig_auc.update_coloraxes(showscale=False)
        st.plotly_chart(fig_auc, use_container_width=True)

    st.markdown("<div class='div'></div>", unsafe_allow_html=True)

    mc3, mc4 = st.columns(2)
    with mc3:
        metrics = ['Accuracy','Precision','Recall','F1','ROC-AUC']
        fig_rad = go.Figure()
        colors_rad = [BLUE, GREEN, AMBER, RED]
        for i, (_, row) in enumerate(res_df.iterrows()):
            vals = [row[m] for m in metrics] + [row[metrics[0]]]
            fig_rad.add_trace(go.Scatterpolar(
                r=vals, theta=metrics+[metrics[0]],
                fill='toself', name=row['Model'],
                line=dict(color=colors_rad[i], width=2),
                fillcolor=colors_rad[i].replace('#','rgba(').replace(')',',0.08)') if '#' in colors_rad[i] else colors_rad[i],
                opacity=0.85
            ))
        fig_rad.update_layout(**CHART, height=380, polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True, range=[0,100], gridcolor='rgba(255,255,255,0.06)', tickfont=dict(color='#475569')),
            angularaxis=dict(gridcolor='rgba(255,255,255,0.06)', tickfont=dict(color='#94a3b8'))
        ), legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#64748b')))
        st.plotly_chart(fig_rad, use_container_width=True)

    with mc4:
        fig_f1 = px.bar(res_df.sort_values('F1'), x='F1', y='Model',
                        orientation='h', color='F1',
                        color_continuous_scale=[[0,RED],[0.5,AMBER],[1,GREEN]],
                        text='F1', title="F1 Score (%) — Precision vs Recall Balance")
        fig_f1.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_line_width=0)
        chl(fig_f1, 380)
        fig_f1.update_layout(yaxis={'categoryorder':'total ascending'})
        fig_f1.update_coloraxes(showscale=False)
        st.plotly_chart(fig_f1, use_container_width=True)

    st.markdown("<div class='div'></div>", unsafe_allow_html=True)
    st.markdown("<div class='big-title'>Feature Importance</div>", unsafe_allow_html=True)

    gb_model = MODELS['Gradient Boosting']
    importances = pd.DataFrame({
        'Feature': FEATURES,
        'Importance': gb_model.feature_importances_
    }).sort_values('Importance', ascending=True).tail(12)

    fig_fi = px.bar(importances, x='Importance', y='Feature', orientation='h',
                    color='Importance', color_continuous_scale=[[0,BLUE],[1,GREEN]],
                    title="Top Feature Importances — Gradient Boosting Model")
    fig_fi.update_traces(marker_line_width=0)
    chl(fig_fi, 420)
    fig_fi.update_coloraxes(showscale=False)
    st.plotly_chart(fig_fi, use_container_width=True)

    st.markdown("<div class='div'></div>", unsafe_allow_html=True)
    st.markdown("<div class='big-title'>All Model Metrics</div>", unsafe_allow_html=True)
    st.dataframe(res_df.set_index('Model').style.highlight_max(color='rgba(99,102,241,0.3)'), use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 4 — WHAT-IF SIMULATOR
# ════════════════════════════════════════════════════════
with t4:
    st.markdown("<div class='tag'>Scenario Analysis</div>", unsafe_allow_html=True)
    st.markdown("<div class='big-title'>What-If Churn Simulator</div>", unsafe_allow_html=True)
    st.markdown("<div style='color:rgba(255,255,255,0.4);font-size:0.88rem;margin-bottom:24px;'>Adjust customer parameters and see how churn probability changes in real time.</div>", unsafe_allow_html=True)

    w1, w2, w3 = st.columns(3)
    with w1:
        w_age      = st.slider("Age",              18,  92,  40, key='w_age')
        w_bal      = st.slider("Balance ($k)",     0,   300, 60, key='w_bal')
        w_score    = st.slider("Credit Score",     350, 850, 650, key='w_score')
    with w2:
        w_products = st.selectbox("Num of Products", [1,2,3,4], index=1, key='w_prod')
        w_tenure   = st.slider("Tenure (years)",   0, 10, 5, key='w_ten')
        w_salary   = st.slider("Salary ($k)",      10, 200, 100, key='w_sal')
    with w3:
        w_geo      = st.selectbox("Geography",       ["France","Germany","Spain"], key='w_geo')
        w_active   = st.selectbox("Active Member",   ["Yes","No"], key='w_act')
        w_gender   = st.selectbox("Gender",          ["Male","Female"], key='w_gen')

    bal = w_bal * 1000
    sal = w_salary * 1000

    row = {
        'CreditScore': w_score, 'Age': w_age, 'Tenure': w_tenure,
        'Balance': bal, 'NumOfProducts': w_products,
        'HasCrCard': 1, 'IsActiveMember': 1 if w_active=="Yes" else 0,
        'EstimatedSalary': sal,
        'Balance_Salary_Ratio': bal / (sal + 1),
        'Age_Tenure_Interaction': w_age * w_tenure,
        'Product_Engagement': w_products * (1 if w_active=="Yes" else 0),
        'Zero_Balance': 1 if bal == 0 else 0,
        'Geography_France':  1 if w_geo=="France" else 0,
        'Geography_Germany': 1 if w_geo=="Germany" else 0,
        'Geography_Spain':   1 if w_geo=="Spain" else 0,
        'Gender_Female': 1 if w_gender=="Female" else 0,
        'Gender_Male':   1 if w_gender=="Male" else 0,
    }
    X_sim = pd.DataFrame([row])[FEATURES]

    probs = {}
    for nm, mdl in MODELS.items():
        if nm == "Logistic Regression":
            probs[nm] = round(mdl.predict_proba(SCALER.transform(X_sim))[0][1] * 100, 1)
        else:
            probs[nm] = round(mdl.predict_proba(X_sim)[0][1] * 100, 1)

    st.markdown("<div class='div'></div>", unsafe_allow_html=True)
    st.markdown("##### Live Churn Probability — All Models")

    sim_cols = st.columns(4)
    for (nm, prob), col in zip(probs.items(), sim_cols):
        cls = "high" if prob >= 60 else "med" if prob >= 35 else "low"
        col.markdown(f"""
        <div class='risk-container risk-{cls}' style='padding:20px 15px;'>
            <div style='font-size:0.65rem;color:rgba(255,255,255,0.3);letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;'>{nm}</div>
            <div class='risk-num-{cls}' style='font-size:2.2rem;'>{prob}%</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    prob_df = pd.DataFrame({'Model': list(probs.keys()), 'Churn Probability %': list(probs.values())})
    fig_sim = px.bar(prob_df, x='Model', y='Churn Probability %',
                     color='Churn Probability %',
                     color_continuous_scale=[[0,GREEN],[0.35,AMBER],[0.6,RED],[1,RED]],
                     text='Churn Probability %', title="Churn Probability Across All Models")
    fig_sim.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_line_width=0)
    fig_sim.add_hline(y=50, line_dash="dash", line_color="rgba(255,255,255,0.2)",
                      annotation_text="Decision Threshold (50%)", annotation_font_color="#64748b")
    chl(fig_sim, 380)
    fig_sim.update_coloraxes(showscale=False)
    st.plotly_chart(fig_sim, use_container_width=True)

    st.markdown("<div class='div'></div>", unsafe_allow_html=True)
    st.markdown("##### Sensitivity: How Balance Affects Churn Risk")
    bal_range = list(range(0, 260000, 10000))
    sens_probs = []
    gb = MODELS['Gradient Boosting']
    for b in bal_range:
        r2 = row.copy()
        r2['Balance'] = b
        r2['Balance_Salary_Ratio'] = b / (sal + 1)
        r2['Zero_Balance'] = 1 if b == 0 else 0
        X2 = pd.DataFrame([r2])[FEATURES]
        sens_probs.append(round(gb.predict_proba(X2)[0][1]*100, 1))

    fig_sens = px.line(x=[b/1000 for b in bal_range], y=sens_probs,
                       labels={'x':'Balance ($k)','y':'Churn Probability %'},
                       title="Balance vs Churn Probability (Gradient Boosting)")
    fig_sens.update_traces(line=dict(color=BLUE, width=2.5), mode='lines')
    fig_sens.add_hline(y=50, line_dash="dash", line_color="rgba(239,68,68,0.4)",
                       annotation_text="50% Threshold", annotation_font_color="#64748b")
    chl(fig_sens, 380)
    st.plotly_chart(fig_sens, use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("<div class='div'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;padding:14px 0 28px;font-size:0.7rem;
            color:rgba(255,255,255,0.15);letter-spacing:1.5px;font-family:'Space Grotesk',sans-serif;">
    CHURNIQ &nbsp;·&nbsp; EUROPEAN CENTRAL BANK &nbsp;·&nbsp; PREDICTIVE CHURN INTELLIGENCE &nbsp;·&nbsp; UNIFIED MENTOR
</div>
""", unsafe_allow_html=True)
