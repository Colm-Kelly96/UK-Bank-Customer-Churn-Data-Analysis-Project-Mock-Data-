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
st.markdown("### Executive Dashboard - Strategic Insights for Retention")
st.markdown("---")

# =============================================================================
# SECTION 1: EXECUTIVE OVERVIEW
# =============================================================================
st.header("📊 Executive Overview")

col1, col2, col3, col4 = st.columns(4)

total_customers = len(df)
churned = df['has_exited'].sum()
churn_rate = (churned / total_customers) * 100
retained = total_customers - churned

with col1:
    st.metric("Total Customers", f"{total_customers:,}")
with col2:
    st.metric("Churn Rate", f"{churn_rate:.2f}%", delta=f"-{churned:,} lost", delta_color="inverse")
with col3:
    st.metric("Churned Customers", f"{churned:,}")
with col4:
    st.metric("Retained Customers", f"{retained:,}")

st.markdown("---")

# =============================================================================
# SECTION 2: TOP 5 CHURN DRIVERS
# =============================================================================
st.header("⚠️ Top 5 Churn Drivers")

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

# Display as formatted table
st.dataframe(
    churn_drivers_df.style.background_gradient(subset=['churned_customers'], cmap='Reds'),
    use_container_width=True,
    height=250
)

# Visualize top drivers
fig_drivers = go.Figure()

fig_drivers.add_trace(go.Bar(
    name='Churned',
    x=churn_drivers_df['churn_driver'],
    y=churn_drivers_df['churned_customers'],
    marker_color='#ff6b6b',
    text=churn_drivers_df['churned_customers'],
    textposition='auto',
))

fig_drivers.update_layout(
    title="Churned Customers by Driver",
    xaxis_title="Churn Driver",
    yaxis_title="Churned Customers",
    height=400,
    showlegend=False
)

st.plotly_chart(fig_drivers, use_container_width=True)

st.markdown("---")

# =============================================================================
# SECTION 3: AT-RISK SEGMENTS (COMBO VARIABLES)
# =============================================================================
st.header("🎯 High-Risk Customer Segments (Combination Analysis)")

st.subheader("Strategy A: Volume Retention (Priority Score 8-10)")
st.markdown("**Target for broad campaigns and cross-sell programs**")

volume_segments = {
    'at_risk_segment': [
        'Single Product Only + No Complaint',
        'Single Product Only + Inactive Member',
        'Single Product Only + Balance £30-80k',
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
    'priority_score': [10, 7.8, 7.4, 7.0, 5.9, 5.9, 5.7, 5.4, 5.2, 5.0]
}

volume_df = pd.DataFrame(volume_segments)

st.dataframe(
    volume_df.style.background_gradient(subset=['priority_score'], cmap='YlOrRd'),
    use_container_width=True,
    height=400
)

col1, col2 = st.columns(2)
with col1:
    st.metric("Total At-Risk (Volume)", f"{volume_df['total_customers'].sum():,}")
with col2:
    st.metric("Expected Churn (No Action)", f"{volume_df['churned_customers'].sum():,}")

st.markdown("**💡 Recommendation:** Cross-sell campaign with fee waivers, engagement initiatives → Expected savings: **~1,500 customers**")

st.markdown("---")

st.subheader("Strategy B: Crisis Management (Churn Rate 65%+)")
st.markdown("**Emergency complaint resolution - Critical for brand reputation**")

crisis_segments = {
    'at_risk_segment': [
        'NPS Detractor + Has Complaint',
        'Single Product Only + Has Complaint',
        'Inactive Member + Has Complaint',
        'Age 18-25 + Has Complaint',
        'Has Complaint + Balance £30-80k',
        'Age 41-60 + Has Complaint'
    ],
    'total_customers': [92, 199, 151, 55, 178, 115],
    'churned_customers': [81, 165, 114, 41, 127, 78],
    'churn_percentage': ['88.04%', '82.91%', '75.50%', '74.55%', '71.35%', '67.83%'],
    'risk_multiplier': ['4.3x', '4.0x', '3.7x', '3.6x', '3.5x', '3.3x'],
    'priority_score': [1.2, 2.4, 1.5, 0.5, 1.6, 0.9]
}

crisis_df = pd.DataFrame(crisis_segments)

st.dataframe(
    crisis_df.style.background_gradient(subset=['churn_percentage'], cmap='Reds'),
    use_container_width=True,
    height=300
)

col1, col2 = st.columns(2)
with col1:
    st.metric("Total At-Risk (Crisis)", f"{crisis_df['total_customers'].sum():,}")
with col2:
    st.metric("Expected Churn (No Action)", f"{crisis_df['churned_customers'].sum():,}")

st.markdown("**💡 Recommendation:** 48-hour complaint resolution SLA, dedicated support queue → Fix systemic issue causing 70-88% churn")

st.markdown("---")

# =============================================================================
# SECTION 4: STRATEGIC RECOMMENDATIONS
# =============================================================================
st.header("💡 Strategic Recommendations")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Strategy A: Volume Retention")
    st.markdown("""
    **Target:** Single Product + No Complaint, Single Product + Inactive, etc.
    
    **Actions:**
    - Broad cross-sell campaigns with incentives
    - Re-engagement programs (push notifications, gamification)
    - Fee waivers for 2nd product adoption
    - Digital engagement initiatives
    
    **Expected Impact:**
    - Save **~1,500+ customers**
    - Revenue protection: **£37.5M** (£25K LTV × 1,500)
    - ROI: High volume, moderate intervention cost
    
    **Timeline:** 0-90 days
    """)

with col2:
    st.subheader("🚨 Strategy B: Crisis Management")
    st.markdown("""
    **Target:** Any segment with "Has Complaint"
    
    **Actions:**
    - Emergency complaint resolution process overhaul
    - 48-hour resolution SLA for all complaints
    - Dedicated priority support queue
    - Root cause analysis by complaint category
    - Proactive outreach to complainers
    
    **Expected Impact:**
    - Fix systemic issue (70-88% churn rate)
    - Prevent future complaints
    - Critical for **brand reputation**
    - Smaller numbers but highest urgency
    
    **Timeline:** Immediate (0-30 days)
    """)

st.markdown("---")

# =============================================================================
# SECTION 5: TOP RETENTION DRIVERS
# =============================================================================
st.header("✅ Top 3 Retention Drivers - What Keeps Customers")

retention_data = {
    'retention_driver': [
        'Multi-Product (2-4 products)',
        'NPS Promoter',
        'Long Tenure (11-15 years)'
    ],
    'total_customers': [5266, 2140, 666],
    'churned_customers': [310, 211, 83],
    'churn_rate': ['5.89%', '9.86%', '12.46%'],
    'vs_baseline': ['-14.68%', '-10.71%', '-8.11%'],
    'retention_impact': ['Strong', 'Strong', 'Moderate']
}

retention_df = pd.DataFrame(retention_data)

st.dataframe(
    retention_df.style.background_gradient(subset=['churned_customers'], cmap='Greens_r'),
    use_container_width=True,
    height=200
)

# Visualization comparing retention vs churn drivers
fig_retention = go.Figure()

retention_categories = retention_df['retention_driver'].tolist()
retention_churn_rates = [5.89, 9.86, 12.46]
driver_churn_rates = [65.00, 36.90, 35.67]  # Top 3 churn drivers

fig_retention.add_trace(go.Bar(
    name='Retention Drivers',
    x=retention_categories,
    y=retention_churn_rates,
    marker_color='#51cf66',
    text=[f"{x:.1f}%" for x in retention_churn_rates],
    textposition='auto'
))

fig_retention.add_hline(y=baseline_churn, line_dash="dash", line_color="red", 
                       annotation_text=f"Baseline: {baseline_churn:.1f}%")

fig_retention.update_layout(
    title="Retention Driver Effectiveness (Lower is Better)",
    xaxis_title="Retention Driver",
    yaxis_title="Churn Rate (%)",
    height=400,
    showlegend=False
)

st.plotly_chart(fig_retention, use_container_width=True)

st.markdown("""
### 🎯 Key Takeaway: Product Adoption is Critical

Customers with **multiple products** have an **86% lower churn rate** (5.89% vs 36.90%).

**Action:** Make multi-product adoption the #1 KPI for retention strategy.
""")

st.markdown("---")

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>UK Bank Customer Churn Analysis Dashboard</strong></p>
    <p>Built using SQL, Python (Streamlit/Plotly), and LLM-assisted development workflows</p>
    <p>Data: 10,000 UK banking customers | 5 normalized tables | 20.57% baseline churn rate</p>
</div>
""", unsafe_allow_html=True)
