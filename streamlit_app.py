import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go   # already there
import plotly.express as px         # NEW – for potential future use

# ==================== PAGE CONFIG ====================
st.set_page_config(page_title="UK Bank Churn Analysis", page_icon="🏦", layout="wide")

# ==================== DATA LOAD (only for overview metrics) ====================
@st.cache_resource
def get_connection():
    return sqlite3.connect('V2_Bank_Churn__SQL_data_base.db', check_same_thread=False)
conn = get_connection()

@st.cache_data
def load_data():
    query = """
    SELECT ch.has_exited
    FROM churn ch
    """
    return pd.read_sql_query(query, conn)
df = load_data()

# ==================== TITLE & OVERVIEW ====================
st.title("🏦 UK Bank Customer Churn Analysis")
st.markdown("### Strategic Retention Insights Dashboard")

# Add nice font (optional but looks 10× more professional)
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    body {font-family: 'Inter', sans-serif;}
    .stMetric {font-weight: 600;}
</style>
""", unsafe_allow_html=True)

st.markdown("---")
st.subheader("📊 Executive Overview")

# === REPLACING the 4 columns with GAUGE + cleaner metrics ===
col_gauge, col_stats = st.columns([1.2, 1])

total_customers = 10000
churned = df['has_exited'].sum()
churn_rate = (churned / total_customers) * 100
retained = total_customers - churned

with col_gauge:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=churn_rate,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "<b>Overall Churn Rate</b>", 'font': {'size': 26}},
        delta={'reference': 15, 'relative': False},
        gauge={
            'axis': {'range': [None, 50], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#e74c3c"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 15], 'color': '#d5f5e3'},
                {'range': [15, 25], 'color': '#ffeaa7'},
                {'range': [25, 50], 'color': '#fab1a0'}
            ],
            'threshold': {'line': {'color': "red", 'width': 8}, 'thickness': 0.75, 'value': churn_rate}
        }
    ))
    fig_gauge.update_layout(height=400, margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_stats:
    st.metric("Total Customers", f"{total_customers:,}")
    st.metric("Churned Customers", f"{churned:,}", delta=f"{churn_rate:.1f}% churn")
    st.metric("Retained Customers", f"{retained:,}")
    st.metric("Complaint → Churn Rate", "65.0%", delta="3.16× risk", delta_color="inverse")

st.markdown("---")

# ==================== TOP 5 CHURN DRIVERS – UPGRADED HORIZONTAL BAR (horizontal + smart colours) ====================
st.subheader("⚠️ Top 5 Churn Drivers")

churn_drivers_data = {
    'rank': [1, 2, 3, 4, 5],
    'churn_driver': [
        'Has Complaint: Yes',
        'Number of Products: 1',
        'NPS Band: Detractor',
        'Active Member: No',
        'Age Group: 18-25'
    ],
    'churn_percentage': ['65.00%', '36.90%', '35.67%', '28.48%', '26.49%'],
    'risk_multiplier': ['3.16x', '1.79x', '1.73x', '1.38x', '1.29x'],
    'total_customers': [300, 4734, 1643, 4027, 1412],
    'churned_customers': [195, 1747, 586, 1147, 374]
}
churn_drivers_df = pd.DataFrame(churn_drivers_data)
st.dataframe(churn_drivers_df, use_container_width=True, height=250)

# Horizontal bar with conditional colouring
colors = ['#e74c3c' if driver == 'Has Complaint: Yes' else '#ff7675' for driver in churn_drivers_df['churn_driver']]

fig_drivers = go.Figure()
fig_drivers.add_trace(go.Bar(
    x=churn_drivers_df['churned_customers'],
    y=churn_drivers_df['churn_driver'],
    orientation='h',
    marker_color=colors,
    text=churn_drivers_df['churn_percentage'],
    textposition='outside',
    hovertemplate='<b>%{y}</b><br>Churned: %{x:,}<br>Rate: %{text}<extra></extra>'
))
fig_drivers.update_layout(
    title="Top 5 Churn Drivers – Ranked by Volume Impact",
    xaxis_title="Number of Churned Customers",
    height=420,
    showlegend=False,
    yaxis={'categoryorder': 'total ascending'}
)
st.plotly_chart(fig_drivers, use_container_width=True)

pandas.errors.DatabaseError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:
File "/mount/src/uk-bank-customer-churn-data-analysis-project-mock-data-/streamlit_app.py", line 141, in <module>
    heat_df = load_heatmap()
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/caching/cache_utils.py", line 228, in __call__
    return self._get_or_create_cached_value(args, kwargs, spinner_message)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/caching/cache_utils.py", line 270, in _get_or_create_cached_value
    return self._handle_cache_miss(cache, value_key, func_args, func_kwargs)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/caching/cache_utils.py", line 329, in _handle_cache_miss
    computed_value = self._info.func(*func_args, **func_kwargs)
File "/mount/src/uk-bank-customer-churn-data-analysis-project-mock-data-/streamlit_app.py", line 139, in load_heatmap
    return pd.read_sql_query(query, conn)
           ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/pandas/io/sql.py", line 528, in read_sql_query
    return pandas_sql.read_query(
           ~~~~~~~~~~~~~~~~~~~~~^
        sql,
        ^^^^
    ...<6 lines>...
        dtype_backend=dtype_backend,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
File "/home/adminuser/venv/lib/python3.13/site-packages/pandas/io/sql.py", line 2728, in read_query
    cursor = self.execute(sql, params)
File "/home/adminuser/venv/lib/python3.13/site-packages/pandas/io/sql.py", line 2676, in execute
    raise ex from exc
# ==================== HIGH-RISK SEGMENTS (100% UNCHANGED – your original tables) ====================
st.subheader("🎯 High-Risk Combination Segments")
st.markdown("#### Volume Retention (Top 10 by Number of Churned Customers)")
st.markdown("**Focus: Prevent the largest volume of churn through scalable interventions**")
volume_data = {
    'rank': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'at_risk_segment': [
        'Single Product Only + No Complaint',
        'Single Product Only + Balance £30-80k',
        'Inactive Member + No Complaint',
        'Tenure 0-2 years + Single Product Only',
        'Single Product Only + Inactive Member',
        'Single Product Only + NPS Not Surveyed',
        'Gender Female + Single Product Only',
        'Gender Male + Single Product Only',
        'Card Credit + Single Product Only',
        'Card Debit + Single Product Only'
    ],
    'total_customers': [4535, 3067, 3876, 2347, 1888, 2418, 2381, 2353, 2224, 1966],
    'churned_customers': [1582, 1117, 1033, 954, 905, 888, 882, 865, 815, 755],
    'churn_percentage': ['34.88%', '36.42%', '26.65%', '40.65%', '47.93%', '36.72%', '37.04%', '36.76%', '36.65%', '38.40%'],
    'risk_multiplier': ['1.7x', '1.8x', '1.3x', '2.0x', '2.3x', '1.8x', '1.8x', '1.8x', '1.8x', '1.9x']
}
st.dataframe(pd.DataFrame(volume_data), use_container_width=True, height=420)
st.markdown("---")
st.markdown("#### Crisis Management (Top 10 by Churn Percentage)")
st.markdown("**🔥 Key Insight: 9 of the top 10 highest-churn segments involve an active complaint** \nComplaints are the #1 predictor of imminent churn — resolving them fast is non-negotiable.")
crisis_data = {
    'rank': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'at_risk_segment': [
        'NPS Detractor + Has Complaint',
        'Single Product Only + Has Complaint',
        'Inactive Member + Has Complaint',
        'Age 18-25 + Has Complaint',
        'Has Complaint + Balance £30-80k',
        'Age 41-60 + Has Complaint',
        'NPS Not Surveyed + Has Complaint',
        'Age 26-40 + Has Complaint',
        'Has Complaint + Balance £0',
        'Single Product Only + NPS Detractor'
    ],
    'total_customers': [92, 199, 151, 55, 178, 115, 123, 111, 53, 807],
    'churned_customers': [81, 165, 114, 41, 127, 78, 78, 68, 32, 461],
    'churn_percentage': ['88.04%', '82.91%', '75.50%', '74.55%', '71.35%', '67.83%', '63.41%', '61.26%', '60.38%', '57.13%'],
    'risk_multiplier': ['4.3x', '4.0x', '3.7x', '3.6x', '3.5x', '3.3x', '3.1x', '3.0x', '2.9x', '2.8x']
}
st.dataframe(pd.DataFrame(crisis_data), use_container_width=True, height=420)
st.markdown("---")

# ==================== DUAL STRATEGY (unchanged) ====================
st.subheader("💡 Recommended Retention Strategy")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    ### 📈 Volume Retention
    **Goal: Reduce churn at scale**
    **Primary Target Segments:**
    - Single Product
    - Inactive Member
    **Recommended Actions:**
    - Cross-sell & product bundling campaigns
    - Automated re-engagement journeys
    - Loyalty incentives for adding a second product
    """)
with col2:
    st.markdown("""
    ### 🚨 Crisis Management
    **Goal: Stop customers about to leave now**
    **Primary Target Segments:**
    - Has Active Complaint
    **Recommended Actions:**
    - 48-hour complaint resolution SLA
    - Dedicated retention team
    - Service recovery offers
    - Root-cause analysis & process fixes
    """)
st.info("""
**Core Principle:**
→ Single-product and inactive customers → fix at scale with proactive programmes
→ Complaining customers → fix immediately with reactive retention
This dual approach delivers maximum retention ROI.
""")

# ==================== FOOTER (unchanged) ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 30px;'>
    <p>Dashboard built with Streamlit • Analysis of 10,000 UK banking customers</p>
    <p>Built by Colm Kelly | <a href="https://www.linkedin.com/in/colm-kelly96/">LinkedIn</a> | <a href="https://github.com/Colm-Kelly96">GitHub</a></p>
</div>
""", unsafe_allow_html=True)
