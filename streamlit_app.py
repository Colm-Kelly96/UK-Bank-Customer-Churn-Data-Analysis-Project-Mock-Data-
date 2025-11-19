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
🔗 Actionable Recommendations
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


# ==================== TOP CHURN DRIVERS SECTION (FULLY WRAPPED) ====================
st.markdown("""
<div style='background-color: #f8f9fa; padding: 30px; border-radius: 10px; border-left: 5px solid #d62728; margin-bottom: 30px;'>
    <h2 style='color: #333; margin-top: 0;'>⚠️ Top Churn Drivers</h2>
    <p style='color: #666; font-size: 16px;'>Understanding which customer segments are most at risk</p>
</div>
""", unsafe_allow_html=True)

# Create columns for layout
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("#### 📊 Churn by Percentage")
    
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
    
    # Convert percentage strings to floats for sorting
    churn_drivers_df['churn_pct_value'] = churn_drivers_df['churn_percentage'].str.rstrip('%').astype(float)
    
    # Sort by percentage descending
    churn_drivers_df_sorted = churn_drivers_df.sort_values(by='churn_pct_value', ascending=True)
    
    fig_pct = go.Figure()
    
    fig_pct.add_trace(go.Bar(
        y=churn_drivers_df_sorted['churn_driver'],
        x=churn_drivers_df_sorted['churn_pct_value'],
        orientation='h',
        marker=dict(
            color=churn_drivers_df_sorted['churn_pct_value'],
            colorscale='Reds',
            reversescale=False,
            showscale=False,
            line=dict(color='rgba(255, 255, 255, 1.0)', width=1)
        ),
        text=[f"{round(pct)}% ({vol:,})" for pct, vol in zip(
            churn_drivers_df_sorted['churn_pct_value'],
            churn_drivers_df_sorted['churned_customers']
        )],
        textposition='outside'
    ))
    
    fig_pct.update_layout(
        xaxis_title="Churn Percentage (%)",
        yaxis_title="",
        yaxis=dict(tickmode='linear'),
        height=250,
        margin=dict(l=10, r=40, t=20, b=40),
        template='plotly_white'
    )
    
    st.plotly_chart(fig_pct, use_container_width=True)
    
with col2:
    st.markdown("#### 💥 Churn by Volume")
    
    
    # Prepare data
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
            showscale=False,
            line=dict(color='rgba(248, 248, 249, 1.0)', width=1)
        ),
        text=churn_drivers_df_sorted['churned_customers'],
        textposition='outside'
    ))
    
    fig.update_layout(
        xaxis_title="Churned Customers",
        yaxis_title="",
        yaxis=dict(tickmode='linear'),
        height=250,
        margin=dict(l=10, r=40, t=20, b=40),
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.markdown("---")

# ==================== TOP RETENTION DRIVERS SECTION ====================
st.markdown("""
<div style='background-color: #e8f5e9; padding: 30px; border-radius: 10px; border-left: 5px solid #66bb6a; margin-bottom: 30px;'>
    <h2 style='color: #333; margin-top: 0;'>💪 Top Retention Drivers</h2>
    <p style='color: #666; font-size: 16px;'>Customer characteristics associated with lowest churn rates</p>
</div>
""", unsafe_allow_html=True)

# Create columns for layout
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("#### 📊 Retention by Percentage")
    
    retention_drivers_data = {
        'category': [
            'Number of Products',
            'NPS Band',
            'Tenure'
        ],
        'category_value': [
            'Multi Products',
            'Promoter',
            '11-15 years'
        ],
        'total_customers': [5266, 2140, 666],
        'churned_customers': [310, 21, 83],
        'churn_rate_pct': [5.89, 0.98, 12.46]
    }
    
    retention_drivers_df = pd.DataFrame(retention_drivers_data)
    
    # Create display label
    retention_drivers_df['driver_label'] = retention_drivers_df['category'] + ': ' + retention_drivers_df['category_value']
    
    # Sort by churn rate ascending (lowest churn = best retention)
    retention_drivers_df_sorted = retention_drivers_df.sort_values(by='churn_rate_pct', ascending=False)
    
    fig_ret_pct = go.Figure()
    
    fig_ret_pct.add_trace(go.Bar(
        y=retention_drivers_df_sorted['driver_label'],
        x=retention_drivers_df_sorted['churn_rate_pct'],
        orientation='h',
        marker=dict(
            color=retention_drivers_df_sorted['churn_rate_pct'],
            colorscale='Greens',
            reversescale=True,  # Darker green = lower churn = better
            showscale=False,
            line=dict(color='rgba(255, 255, 255, 1.0)', width=1)
        ),
        text=[f"{round(pct)}% ({vol:,})" for pct, vol in zip(
            retention_drivers_df_sorted['churn_rate_pct'],
            retention_drivers_df_sorted['churned_customers']
        )],
        textposition='outside'
    ))
    
    fig_ret_pct.update_layout(
        xaxis_title="Churn Rate (%)",
        yaxis_title="",
        yaxis=dict(tickmode='linear'),
        height=250,
        margin=dict(l=10, r=40, t=20, b=40),
        template='plotly_white'
    )
    
    st.plotly_chart(fig_ret_pct, use_container_width=True)

with col2:
    st.markdown("#### 💥 Retained Customers by Volume")
    
    # Calculate retained customers
    retention_drivers_df_sorted['retained_customers'] = retention_drivers_df_sorted['total_customers'] - retention_drivers_df_sorted['churned_customers']
    
    # Sort by retained customers for volume chart
    retention_vol_sorted = retention_drivers_df_sorted.sort_values(by='retained_customers', ascending=True)
    
    fig_ret_vol = go.Figure()
    
    fig_ret_vol.add_trace(go.Bar(
        y=retention_vol_sorted['driver_label'],
        x=retention_vol_sorted['retained_customers'],
        orientation='h',
        marker=dict(
            color=retention_vol_sorted['retained_customers'],
            colorscale='Greens',
            reversescale=False,
            showscale=False,
            line=dict(color='rgba(255, 255, 255, 1.0)', width=1)
        ),
        text=retention_vol_sorted['retained_customers'],
        textposition='outside'
    ))
    
    fig_ret_vol.update_layout(
        xaxis_title="Retained Customers",
        yaxis_title="",
        yaxis=dict(tickmode='linear'),
        height=250,
        margin=dict(l=10, r=40, t=20, b=40),
        template='plotly_white'
    )
    
    st.plotly_chart(fig_ret_vol, use_container_width=True)

st.markdown("---")


# ==================== DUAL STRATEGY (WRAPPED - ORANGE) ====================
st.markdown("""
<div style='background-color: #fff3e0; padding: 30px; border-radius: 10px; border-left: 5px solid #ff9800; margin-bottom: 30px;'>
    <h2 style='color: #333; margin-top: 0;'>💡 Recommended Retention Strategy</h2>
    <p style='color: #666; font-size: 16px;'>Dual approach for maximum retention ROI</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📈 Volume Retention
    **Goal: Reduce churn at scale**

    **Primary Target:**
    - Single Product   
    - Inactive Member 

    **Recommended Actions:**
    
    **Cross-Sell Blitz**  
    - **Target:** 4,734 single-product customers  
    - **Offer:** Second product incentive (e.g., Interest rate boost, fee waiver, cashback)  
    - **Communication:** Marketing campaign - In-app Banners, Push Notifications, Emails
    
    **Inactive Re-activation**  
    - **Target:** 4,027 inactive members  
    - **Campaign:** Push notifications, special offers, gamification
    """)

with col2:
    st.markdown("""
    ### 🚨 Crisis Management
    **Goal: Stop customers about to leave now**

    **Primary Target:**
    - Has Active Complaint  

    **Recommended Actions:**
    
    - Root-cause analysis & process fixes  
    - Uplifted complaint handling process – remediation and proactive follow ups
    """)

st.info("""
**Core Principle:**  
→ Single-product and inactive customers → fix at scale with proactive programmes  
→ Complaining customers → fix immediately with reactive retention 

This dual approach delivers maximum retention ROI.
""")

st.markdown("---")

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
# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 30px;'>
    <p>Dashboard built with Streamlit • Analysis of 10,000 UK banking customers</p>
    <p>Built by Colm Kelly | <a href="https://www.linkedin.com/in/colm-kelly96/">LinkedIn</a> | <a href="https://github.com/Colm-Kelly96">GitHub</a></p>
</div>
""", unsafe_allow_html=True)
