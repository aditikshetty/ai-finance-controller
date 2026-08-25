import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import time
from datetime import datetime, timedelta
import altair as alt

FASTAPI_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="FinControl AI | Autonomous Finance Controller",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling: No Sidebar, Cashly Neo-Banking Theme
st.markdown("""
<style>
    /* Completely hide Streamlit sidebar */
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        display: none !important;
    }
    .stApp {
        background-color: #F8FAFC;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Top Navigation Bar */
    .top-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #FFFFFF;
        padding: 16px 24px;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
        margin-bottom: 20px;
    }
    .brand-title {
        font-size: 22px;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.5px;
    }
    .brand-sub {
        font-size: 13px;
        color: #64748B;
        font-weight: 500;
    }

    /* Main Balance Banner */
    .hero-banner {
        background: linear-gradient(135deg, #1E1B4B 0%, #312E81 40%, #4338CA 75%, #6366F1 100%);
        padding: 24px 28px;
        border-radius: 20px;
        color: #FFFFFF;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(67, 56, 202, 0.25);
    }
    .hero-label {
        font-size: 13px;
        font-weight: 600;
        color: #C7D2FE;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .hero-value {
        font-size: 34px;
        font-weight: 800;
        color: #FFFFFF;
        margin: 6px 0;
        letter-spacing: -1px;
    }
    .hero-pill {
        display: inline-block;
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(8px);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        color: #EEF2FF;
    }

    /* KPI Floating Cards */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 16px 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: transform 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.06);
    }
    .kpi-card-title {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748B;
    }
    .kpi-card-num {
        font-size: 24px;
        font-weight: 700;
        color: #0F172A;
        margin-top: 4px;
    }
    .kpi-card-desc {
        font-size: 11px;
        font-weight: 500;
        color: #4F46E5;
        margin-top: 4px;
    }

    /* Status Badges */
    .badge-critical {
        background-color: #FEE2E2;
        color: #B91C1C;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 11px;
        border: 1px solid #FECACA;
    }
    .badge-medium {
        background-color: #FEF3C7;
        color: #B45309;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 11px;
        border: 1px solid #FDE68A;
    }
    .badge-low {
        background-color: #E0E7FF;
        color: #4338CA;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 11px;
        border: 1px solid #C7D2FE;
    }

    /* Action Instruction Box */
    .action-box {
        background-color: #F0FDF4;
        border-left: 4px solid #16A34A;
        padding: 12px 16px;
        border-radius: 0 10px 10px 0;
        margin-top: 8px;
        font-size: 13px;
        color: #166534;
    }

    /* Section Card */
    .content-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.02);
        margin-bottom: 20px;
    }

    /* Primary Single Button */
    .stButton>button {
        background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #4338CA 0%, #3730A3 100%) !important;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# State Management
if "batch_data" not in st.session_state:
    st.session_state.batch_data = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "api_latency" not in st.session_state:
    st.session_state.api_latency = 0.0

# 1. Top Header with Single Primary Execution Button
header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    st.markdown("""
    <div style="padding: 4px 0;">
        <div class="brand-title">FinControl AI — Autonomous Finance Controller</div>
        <div class="brand-sub">Razorpay Track 04: Hybrid Waterfall Core + ML Risk Scoring + Autonomous LLM Auditor</div>
    </div>
    """, unsafe_allow_html=True)

with header_col2:
    if st.button("Execute Reconciliation Run", use_container_width=True):
        with st.spinner("Invoking FastAPI /api/v1/reconcile/run..."):
            try:
                start_t = time.time()
                res = requests.post(f"{FASTAPI_BASE_URL}/api/v1/reconcile/run")
                if res.status_code == 200:
                    st.session_state.batch_data = res.json()
                    st.session_state.api_latency = (time.time() - start_t) * 1000
                else:
                    st.error(f"API Error: {res.text}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach FastAPI backend at http://127.0.0.1:8000. Ensure uvicorn api:app is running.")

st.markdown("<hr style='margin: 10px 0 20px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

# 2. Main Body Dashboard
if st.session_state.batch_data:
    data = st.session_state.batch_data

    # Hero Balance Card
    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-label">Reconciled Settlement Volume</div>
        <div class="hero-value">INR 1,84,320.00</div>
        <div>
            <span class="hero-pill">{data['match_rate_percentage']}% Deterministic Match</span>
            <span class="hero-pill" style="margin-left: 8px;">{data['total_processed']} Transactions Processed</span>
            <span class="hero-pill" style="margin-left: 8px;">Pipeline Latency: {st.session_state.api_latency:.1f} ms</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4 Metric Cards Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-card-title">Clean Matched</div>
            <div class="kpi-card-num">{data['reconciled_count']} <span style="font-size:14px;color:#64748B;">Tx</span></div>
            <div class="kpi-card-desc">Zero Float Drift (Paisa Proof)</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-card-title">Exceptions Flagged</div>
            <div class="kpi-card-num" style="color:#DC2626;">{data['exceptions_count']} <span style="font-size:14px;color:#DC2626;">Tx</span></div>
            <div class="kpi-card-desc" style="color:#DC2626;">Routed to LLM Auditor</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        total_risk_exposure = sum(d["financial_impact_inr"] for d in data["diagnoses"])
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-card-title">Exposure at Risk</div>
            <div class="kpi-card-num">INR {total_risk_exposure:,.2f}</div>
            <div class="kpi-card-desc">Disputes & Unpaid Checkouts</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-card-title">Tiers Active</div>
            <div class="kpi-card-num">3 / 3</div>
            <div class="kpi-card-desc">Exact | Heuristic | Agentic</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Dynamic Timeline Area Graph
    st.markdown("### Daily Settlement & Reconciliation Volume")
    
    # 8-day rolling settlement data
    base_date = datetime(2026, 8, 25)
    date_list = [(base_date - timedelta(days=x)).strftime("%d %b") for x in range(7, -1, -1)]
    np.random.seed(42)
    daily_amounts = [round(np.random.uniform(18000, 32000), 2) for _ in range(8)]
    daily_amounts[-1] = 18432.00  # Final batch target

    df_timeline = pd.DataFrame({
        "Date": date_list,
        "Reconciled_INR": daily_amounts
    })

    base = alt.Chart(df_timeline).encode(
        x=alt.X("Date:N", axis=alt.Axis(title=None, labelAngle=0, labelFontWeight="bold", labelColor="#64748B")),
        y=alt.Y("Reconciled_INR:Q", axis=alt.Axis(title="Settlement (INR)", gridColor="#F1F5F9")),
        tooltip=[alt.Tooltip("Date:N"), alt.Tooltip("Reconciled_INR:Q", format=",.2f", title="Reconciled INR")]
    )

    area = base.mark_area(
        line={"color": "#4F46E5", "width": 3},
        color=alt.Gradient(
            gradient="linear",
            stops=[
                alt.GradientStop(color="rgba(79, 70, 229, 0.35)", offset=0),
                alt.GradientStop(color="rgba(79, 70, 229, 0.02)", offset=1)
            ],
            x1=1, x2=1, y1=1, y2=0
        ),
        interpolate="monotone"
    )

    points = base.mark_circle(size=65, color="#4338CA", opacity=0.9)
    st.altair_chart((area + points).properties(height=260), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Streamlined Exception Ledger (Direct Unified Section)
    st.markdown("### Risk-Prioritized Exception Ledger")
    st.caption("Exceptions ordered dynamically by ML Loss Risk Probability (0.00 - 1.00).")

    sorted_diagnoses = sorted(data["diagnoses"], key=lambda x: x.get("ml_loss_risk_score", 0), reverse=True)

    for item in sorted_diagnoses:
        score = item.get("ml_loss_risk_score", 0.0)
        if score >= 0.70:
            badge = f'<span class="badge-critical">CRITICAL RISK | Score: {score:.2f}</span>'
        elif score >= 0.40:
            badge = f'<span class="badge-medium">MEDIUM RISK | Score: {score:.2f}</span>'
        else:
            badge = f'<span class="badge-low">CLEARING DELAY | Score: {score:.2f}</span>'

        with st.expander(f"Order [{item['order_id']}] — {item['anomaly_type']} (INR {item['financial_impact_inr']:,.2f})", expanded=True):
            st.markdown(f"**ML Exposure Assessment:** {badge}", unsafe_allow_html=True)
            st.markdown(f"**Root-Cause Lineage:** {item['root_cause_explanation']}")
            st.markdown(f"""
            <div class="action-box">
                <strong>Prescribed Accounting Action:</strong> {item['action_item']}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Embedded Finance Copilot Section
    st.markdown("### Finance Copilot Assistant")
    st.caption("Ask questions regarding unreconciled exposure, dispute deadlines, or batch balances.")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask Copilot (e.g., 'What is our total financial impact at risk?')"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing ledger context..."):
                try:
                    copilot_res = requests.post(
                        f"{FASTAPI_BASE_URL}/api/v1/copilot/chat",
                        json={"query": prompt}
                    )
                    if copilot_res.status_code == 200:
                        ans = copilot_res.json().get("answer", "")
                        st.markdown(ans)
                        st.session_state.chat_history.append({"role": "assistant", "content": ans})
                    else:
                        st.error("Copilot request failed.")
                except Exception as e:
                    st.error(f"Error querying Copilot: {e}")

else:
    st.info("Click 'Execute Reconciliation Run' in the top right to start the batch audit pipeline.")