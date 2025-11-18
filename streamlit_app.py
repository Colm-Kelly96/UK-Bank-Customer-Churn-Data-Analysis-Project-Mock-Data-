import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go

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
st.markdown("""
<div style='font-size:16px; color: #555; margin-bottom: 20px;'>
    ♻️ <em>Work In Progress - Building out analysis and visualisations using a mock data set.</em>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<a href="#recommended-retention-strategy" style="font-size:16px; text-decoration:none; color:#007bff;">
🔥 Actionable Recommendations
</a>
""", unsafe_allow_html=True)

st.subheader("📊 Executive Overview")
col1, col2, col3, col4 = st.columns(4)

total_customers = 10000  # Fixed for your dataset
churned = df['has_exited'].sum()
churn_rate = (churned / total_customers) * 100
retained = total_customers - churned

with col1:
    st.metric("Total Customers", f"{total_customers:,}")
with col2:
    st.metric("Churned Customers", f"{churned:,}", delta=f"{churn_rate:.2f}%", delta_color="inverse")
with col3:
    st.metric("Retained Customers", f"{retained:,}")
with col4:
    st.metric("Baseline Churn Rate", f"{churn_rate:.2f}%")

st.markdown("---")


# ==================== TOP 5 CHURN DRIVERS (TABLE ONLY - HARDCODED) ====================
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

st.markdown("---")

# ==================== 💥 CHURNED CUSTOMERS BY VOLUME (Horizontal Ranked Bar + Color Scale) ====================


# Prepare data ordered by churned customers descending
churn_drivers_df_sorted = churn_drivers_df.sort_values(by='churned_customers', ascending=True)

fig = go.Figure()

fig.add_trace(go.Bar(
    y=churn_drivers_df_sorted['churn_driver'],
    x=churn_drivers_df_sorted['churned_customers'],
    orientation='h',
    marker=dict(
        color=churn_drivers_df_sorted['churned_customers'],
        colorscale='Reds',
        reversescale=False,
        colorbar=dict(title="Churn Volume"),
        line=dict(color='rgba(248, 248, 249, 1.0)', width=1)
    ),
    text=churn_drivers_df_sorted['churned_customers'],
    textposition='outside'
))

fig.update_layout(
    title="💥 Churned Customers by Volume",
    xaxis_title="Churned Customers",
    yaxis_title="Churn Driver",
    yaxis=dict(tickmode='linear'),
    height=400,
    margin=dict(l=150, r=40, t=70, b=40),
    template='plotly_white'
)

st.plotly_chart(fig, use_container_width=True)

# ==================== HIGH-RISK SEGMENTS (HARDCODED) ====================
st.subheader("🎯 High-Risk Combination Segments")

st.markdown("#### Volume Retention (Top 10 by Number of Churned Customers)")
st.markdown("**🔥 Key Insight: 9 of the top 10 high-volume churn segments involve customers with only a single product**  \nSingle-product customers are the biggest driver of churn volume — focusing on them with proactive retention will have the biggest impact")

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
st.markdown("**🔥 Key Insight: 9 of the top 10 highest-churn segments involve an active complaint**  \nComplaints are the #1 predictor of imminent churn — resolving them fast is non-negotiable.")

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

# ==================== DUAL STRATEGY ====================
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

# ==================== BUSINESS RECOMMENDATIONS ====================
st.markdown("---")
st.subheader("💡 Business Recommendations")

st.markdown("""
### Priorty Actions

1. **Cross-Sell Blitz**  
_Target:_ 4,734 single-product customers  
_Offer:_ Second product with incentive (e.g., fee waiver, cashback)  
_Expected impact:_ Reduce churn from 36.9% to 6-7% → save ~1,500 customers  

2. **Complaint Fast-Track**  
_Target:_ 300 complainers (especially Card Issues, Access, Fraud)  
_SLA:_ Resolve within 48 hours for severity 4-5 issues  
_Expected impact:_ Reduce complaint-driven churn from 65% to 40% → save ~75 customers  

3. **Inactive Re-activation**  
_Target:_ 4,027 inactive members  
_Campaign:_ Push notifications, special offers, gamification  
_Expected impact:_ Reactivate 20% → reduce churn by 229 customers  
""")


# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 30px;'>
    <p>Dashboard built with Streamlit • Analysis of 10,000 UK banking customers</p>
    <p>Built by Colm Kelly | <a href="https://www.linkedin.com/in/colm-kelly96/">LinkedIn</a> | <a href="https://github.com/Colm-Kelly96">GitHub</a></p>
</div>
""", unsafe_allow_html=True)
