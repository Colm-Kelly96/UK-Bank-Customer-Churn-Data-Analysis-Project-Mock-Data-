import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="UK Bank Churn Analysis",
    page_icon="🏦",
    layout="wide"
)

# Database connection
@st.cache_resource
def get_connection():
    return sqlite3.connect('V2_Bank_Churn__SQL_data_base.db', check_same_thread=False)

conn = get_connection()

# Load master dataset
@st.cache_data
def load_data():
    query = """
    SELECT 
        c.customer_id,
        c.surname,
        c.age,
        c.gender,
        c.region,
        a.balance,
        a.num_products,
        a.tenure,
        a.estimated_salary,
        e.is_active_member,
        e.card_type,
        co.has_complaint,
        co.satisfaction_score,
        co.complaint_date,
        co.complaint_category,
        co.nps_response,
        co.nps_band,
        ch.has_exited
    FROM customers c
    JOIN accounts a ON c.customer_id = a.customer_id
    JOIN engagement e ON c.customer_id = e.customer_id
    JOIN complaints co ON c.customer_id = co.customer_id
    JOIN churn ch ON c.customer_id = ch.customer_id
    """
    return pd.read_sql_query(query, conn)

df = load_data()

# Calculate baseline churn rate
baseline_churn = (df['has_exited'].sum() / len(df)) * 100

# Title
st.title("🏦 UK Bank Customer Churn Analysis")
st.markdown("### Strategic Retention Insights Dashboard")
st.markdown("---")

# ==================== SECTION 1: OVERVIEW ====================
st.subheader("📊 Executive Overview")

col1, col2, col3, col4 = st.columns(4)

total_customers = len(df)
churned = df['has_exited'].sum()
churn_rate = (churned / total_customers) * 100
retained = total_customers - churned

with col1:
    st.metric("Total Customers", f"{total_customers:,}")
with col2:
    st.metric("Churned Customers", f"{churned:,}", delta=f"{churn_rate:.2f}%", delta_color="inverse")
with col3:
    st.metric("Retained Customers", f"{retained:,}", delta=f"{100-churn_rate:.2f}%", delta_color="normal")
with col4:
    st.metric("Baseline Churn Rate", f"{churn_rate:.2f}%")

st.markdown("---")

# ==================== SECTION 2: TOP 5 CHURN DRIVERS ====================
st.subheader("⚠️ Top 5 Churn Drivers")

# Create churn drivers data
churn_drivers_data = {
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

# Display as styled table
st.dataframe(
    churn_drivers_df,
    use_container_width=True,
    height=250
)

# Visualization
fig_drivers = go.Figure()

fig_drivers.add_trace(go.Bar(
    x=churn_drivers_df['churn_driver'],
    y=churn_drivers_df['churned_customers'],
    name='Churned Customers',
    marker_color='#ff6b6b',
    text=churn_drivers_df['churn_percentage'],
    textposition='outside'
))

fig_drivers.update_layout(
    title="Churned Customers by Driver",
    xaxis_title="Churn Driver",
    yaxis_title="Number of Churned Customers",
    height=400,
    showlegend=False
)

st.plotly_chart(fig_drivers, use_container_width=True)

st.markdown("---")

# ==================== SECTION 3: HIGH-RISK COMBO SEGMENTS ====================
st.subheader("🎯 High-Risk Combination Segments")

st.markdown("#### Top 10 At-Risk Segments by Priority Score")
st.markdown("*Priority Score = Churned Customers × Risk Multiplier*")

# Top 10 by priority score
combo_priority_data = {
    'at_risk_segment': [
        'Single Product Only + No Complaint',
        'Single Product Only + Inactive Member',
        'Single Product Only + Balance £30-80k (Medium)',
        'Tenure 0-2 years + Single Product Only',
        'Single Product Only + NPS Not Surveyed',
        'Gender Female + Single Product Only',
        'Gender Male + Single Product Only',
        'Card Credit + Single Product Only',
        'Card Debit + Single Product Only',
        'Inactive Member + No Complaint'
    ],
    'total_customers': [4535, 1888, 3067, 2347, 2418, 2381, 2353, 2224, 1966, 3876],
    'churned_customers': [1582, 905, 1117, 954, 888, 882, 865, 815, 755, 1033],
    'churn_percentage': ['34.88%', '47.93%', '36.42%', '40.65%', '36.72%', '37.04%', '36.76%', '36.65%', '38.40%', '26.65%'],
    'risk_multiplier': ['1.7x', '2.3x', '1.8x', '2.0x', '1.8x', '1.8x', '1.8x', '1.8x', '1.9x', '1.3x'],
    'priority_score': [10.0, 7.8, 7.4, 7.0, 5.9, 5.9, 5.7, 5.4, 5.2, 5.0]
}

combo_priority_df = pd.DataFrame(combo_priority_data)

st.dataframe(
    combo_priority_df,
    use_container_width=True,
    height=400
)

st.markdown("---")

st.markdown("#### Top 6 Crisis Segments by Churn Rate (65%+)")
st.markdown("*Critical: Requires immediate intervention*")

# Top 6 by churn percentage
combo_crisis_data = {
    'at_risk_segment': [
        'NPS Detractor + Has Complaint',
        'Single Product Only + Has Complaint',
        'Inactive Member + Has Complaint',
        'Age 18-25 + Has Complaint',
        'Has Complaint + Balance £30-80k (Medium)',
        'Age 41-60 + Has Complaint'
    ],
    'total_customers': [92, 199, 151, 55, 178, 115],
    'churned_customers': [81, 165, 114, 41, 127, 78],
    'churn_percentage': ['88.04%', '82.91%', '75.50%', '74.55%', '71.35%', '67.83%'],
    'risk_multiplier': ['4.3x', '4.0x', '3.7x', '3.6x', '3.5x', '3.3x'],
    'priority_score': [1.2, 2.4, 1.5, 0.5, 1.6, 0.9]
}

combo_crisis_df = pd.DataFrame(combo_crisis_data)

st.dataframe(
    combo_crisis_df,
    use_container_width=True,
    height=300
)

st.markdown("---")

# ==================== SECTION 4: STRATEGY RECOMMENDATIONS ====================
st.subheader("💡 Dual-Strategy Retention Framework")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📈 Strategy A: Volume Retention
    **Priority Score 8-10 Segments**
    
    **Target Segments:**
    - Single Product + No Complaint (1,582 churned)
    - Single Product + Inactive (905 churned)
    - Single Product + Medium Balance (1,117 churned)
    
    **Actions:**
    - Broad cross-sell campaigns
    - Product bundling incentives
    - Re-engagement initiatives
    - Proactive outreach programs
    
    **Expected Impact:**
    - Save 1,500+ customers annually
    - High-volume, moderate intervention cost
    - ROI: Strong due to scale
    
    **Timeline:** 0-3 months for rollout
    """)

with col2:
    st.markdown("""
    ### 🚨 Strategy B: Crisis Management
    **Churn Rate 65%+ Segments**
    
    **Target Segments:**
    - NPS Detractor + Has Complaint (88% churn)
    - Single Product + Has Complaint (83% churn)
    - Any segment with complaints (70%+ churn)
    
    **Actions:**
    - Emergency complaint resolution overhaul
    - 48-hour resolution SLA
    - Root cause analysis by category
    - Process improvement initiatives
    
    **Expected Impact:**
    - Fix systemic issues
    - Protect brand reputation
    - Prevent future complaints
    
    **Timeline:** Immediate (0-30 days)
    """)

st.markdown("---")

st.info("""
**Strategic Insight:** Your priority score formula optimally balances BOTH strategies:
- **High priority scores** (8-10) = volume opportunity → broad retention campaigns
- **High churn rates** (65%+) = crisis segments → emergency interventions

This dual approach addresses both operational scale and critical risk management.
""")

st.markdown("---")

# ==================== SECTION 5: TOP 3 RETENTION DRIVERS ====================
st.subheader("✅ Top Retention Drivers")
st.markdown("*What keeps customers loyal?*")

# Retention drivers data (combined multi-product)
retention_combined_data = {
    'category': ['Number of Products', 'NPS Band', 'Tenure'],
    'category_value': ['Multi-Product (2+)', 'Promoter', '11-15 years'],
    'total_customers': [5266, 2140, 666],
    'churned_customers': [310, 211, 83],
    'churn_rate_pct': ['5.89%', '9.86%', '12.46%'],
    'diff_from_avg': ['-14.68%', '-10.71%', '-8.11%'],
    'correlation_strength': ['Strong', 'Strong', 'Moderate']
}

retention_combined_df = pd.DataFrame(retention_combined_data)

st.dataframe(
    retention_combined_df,
    use_container_width=True,
    height=200
)

# Visualization
fig_retention = go.Figure()

fig_retention.add_trace(go.Bar(
    y=retention_combined_df['category_value'],
    x=retention_combined_df['churned_customers'],
    orientation='h',
    marker_color='#51cf66',
    text=retention_combined_df['churn_rate_pct'],
    textposition='outside'
))

fig_retention.update_layout(
    title="Retention Driver Performance",
    xaxis_title="Churned Customers (Lower = Better)",
    yaxis_title="Retention Driver",
    height=350
)

st.plotly_chart(fig_retention, use_container_width=True)

st.success("""
**Key Insight:** Customers with 2+ products have a churn rate of just 5.89% - that's **71% lower** than single-product customers (36.9%). 

**Action:** Cross-sell is the single most powerful retention lever available.
""")

st.markdown("---")

# ==================== FOOTER ====================
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Dashboard built using Streamlit + Python | Analysis of 10,000 UK banking customers</p>
    <p><em>Demonstrating SQL proficiency, data visualization, and LLM-assisted development workflows</em></p>
    <p>Built by Colm Kelly | <a href="https://www.linkedin.com/in/colm-kelly96/" target="_blank">LinkedIn</a> | <a href="https://github.com/Colm-Kelly96" target="_blank">GitHub</a></p>
</div>
""", unsafe_allow_html=True)
