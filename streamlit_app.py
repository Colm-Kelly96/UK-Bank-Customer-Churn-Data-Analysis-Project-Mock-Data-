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

# Title and intro
st.title("🏦 UK Bank Customer Churn Analysis")
st.markdown("### Data-Driven Insights for Customer Retention Strategy")
st.markdown("---")

# Executive metrics
col1, col2, col3, col4 = st.columns(4)

total_customers = len(df)
churned = df['has_exited'].sum()
churn_rate = (churned / total_customers) * 100
at_risk = len(df[(df['num_products'] == 1) & (df['is_active_member'] == 0)])
avg_products = df['num_products'].mean()

with col1:
    st.metric("Total Customers", f"{total_customers:,}")
with col2:
    st.metric("Churn Rate", f"{churn_rate:.1f}%", delta=f"{churned:,} churned", delta_color="inverse")
with col3:
    st.metric("High-Risk Customers", f"{at_risk:,}", help="Single product + inactive")
with col4:
    st.metric("Avg Products/Customer", f"{avg_products:.2f}")

st.markdown("---")

# Section 1: Churn by Product Count
st.subheader("📊 Product Adoption Impact on Churn")

churn_by_products = df.groupby('num_products').agg({
    'has_exited': ['sum', 'count', 'mean']
}).reset_index()
churn_by_products.columns = ['num_products', 'churned', 'total', 'churn_rate']
churn_by_products['churn_rate'] = churn_by_products['churn_rate'] * 100

fig1 = px.bar(
    churn_by_products, 
    x='num_products', 
    y='churn_rate',
    text='churn_rate',
    labels={'num_products': 'Number of Products', 'churn_rate': 'Churn Rate (%)'},
    color='churn_rate',
    color_continuous_scale='Reds'
)
fig1.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig1.update_layout(showlegend=False, height=400)

col1, col2 = st.columns([2, 1])
with col1:
    st.plotly_chart(fig1, use_container_width=True)
with col2:
    st.markdown("""
    **Key Insight:**
    
    Customers with only 1 product have a **36.9% churn rate** - nearly **6x higher** than multi-product customers.
    
    **Strategic Action:**
    - Target 4,734 single-product customers
    - Cross-sell campaign with incentives
    - Expected savings: ~1,500 customers
    """)

st.markdown("---")

# Section 2: Engagement & Activity Impact
st.subheader("🎯 Customer Engagement Analysis")

engagement_churn = df.groupby('is_active_member')['has_exited'].agg(['sum', 'count', 'mean']).reset_index()
engagement_churn.columns = ['is_active_member', 'churned', 'total', 'churn_rate']
engagement_churn['churn_rate'] = engagement_churn['churn_rate'] * 100
engagement_churn['status'] = engagement_churn['is_active_member'].map({1: 'Active', 0: 'Inactive'})

fig2 = go.Figure(data=[
    go.Bar(name='Churned', x=engagement_churn['status'], y=engagement_churn['churned'], marker_color='#ff6b6b'),
    go.Bar(name='Retained', x=engagement_churn['status'], y=engagement_churn['total'] - engagement_churn['churned'], marker_color='#51cf66')
])
fig2.update_layout(barmode='stack', height=400, xaxis_title='Customer Status', yaxis_title='Number of Customers')

col1, col2 = st.columns([2, 1])
with col1:
    st.plotly_chart(fig2, use_container_width=True)
with col2:
    inactive_churn = engagement_churn[engagement_churn['is_active_member'] == 0]['churn_rate'].values[0]
    st.markdown(f"""
    **Key Insight:**
    
    Inactive members have a **{inactive_churn:.1f}% churn rate** - 1.4x the baseline.
    
    **Strategic Action:**
    - Re-activation campaign for 4,027 inactive members
    - Push notifications, gamification
    - Target 20% reactivation = save 229 customers
    """)

st.markdown("---")

# Section 3: Regional Performance
st.subheader("🗺️ Regional Churn Distribution")

regional_churn = df.groupby('region')['has_exited'].agg(['sum', 'count', 'mean']).reset_index()
regional_churn.columns = ['region', 'churned', 'total', 'churn_rate']
regional_churn['churn_rate'] = regional_churn['churn_rate'] * 100
regional_churn = regional_churn.sort_values('churn_rate', ascending=False)

fig3 = px.bar(
    regional_churn,
    x='churn_rate',
    y='region',
    orientation='h',
    text='churn_rate',
    labels={'churn_rate': 'Churn Rate (%)', 'region': 'Region'},
    color='churn_rate',
    color_continuous_scale='RdYlGn_r'
)
fig3.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig3.update_layout(showlegend=False, height=500)

st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# Section 4: Complaint Analysis
st.subheader("⚠️ Complaint Impact on Churn")

complaint_analysis = df[df['has_complaint'] == 1].groupby('complaint_category')['has_exited'].agg(['sum', 'count', 'mean']).reset_index()
complaint_analysis.columns = ['category', 'churned', 'total', 'churn_rate']
complaint_analysis['churn_rate'] = complaint_analysis['churn_rate'] * 100
complaint_analysis = complaint_analysis.sort_values('churn_rate', ascending=False)

col1, col2 = st.columns([2, 1])

with col1:
    fig4 = px.bar(
        complaint_analysis,
        x='category',
        y='churn_rate',
        text='churn_rate',
        labels={'category': 'Complaint Category', 'churn_rate': 'Churn Rate (%)'},
        color='churn_rate',
        color_continuous_scale='Reds'
    )
    fig4.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig4.update_layout(showlegend=False, height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    overall_complaint_churn = (df[df['has_complaint'] == 1]['has_exited'].sum() / df[df['has_complaint'] == 1]['has_exited'].count()) * 100
    st.markdown(f"""
    **Key Insight:**
    
    Customers with complaints have a **{overall_complaint_churn:.1f}% churn rate** - 3.2x the baseline.
    
    Top priority categories:
    - Card Issues/Fraud
    - Account Access/Online
    - Payment/Transfer Failure
    
    **Strategic Action:**
    - 48-hour resolution SLA
    - Priority support queue
    - Expected savings: ~75 customers
    """)

st.markdown("---")

# Section 5: High-Risk Customer Segments
st.subheader("🎯 High-Risk Customer Identification")

# Create risk scoring
df['risk_score'] = 0
df.loc[df['num_products'] == 1, 'risk_score'] += 3
df.loc[df['is_active_member'] == 0, 'risk_score'] += 2
df.loc[df['has_complaint'] == 1, 'risk_score'] += 3
df.loc[df['nps_band'] == 'Detractor', 'risk_score'] += 2
df.loc[df['age'] < 30, 'risk_score'] += 1

high_risk = df[df['risk_score'] >= 5].sort_values('risk_score', ascending=False)

st.markdown(f"**{len(high_risk):,} customers identified as high-risk** (score ≥ 5)")

# Show top 50 high-risk customers
display_cols = ['customer_id', 'region', 'age', 'num_products', 'is_active_member', 
                'has_complaint', 'nps_band', 'risk_score', 'has_exited']
st.dataframe(
    high_risk[display_cols].head(50).style.background_gradient(subset=['risk_score'], cmap='Reds'),
    use_container_width=True,
    height=400
)

st.markdown("---")

# Section 6: Strategic Recommendations
st.subheader("💡 Strategic Recommendations")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 🎯 Immediate Actions (0-30 days)
    
    **1. Cross-Sell Blitz**
    - Target: 4,734 single-product customers
    - Offer: Fee waiver for 2nd product
    - Impact: Save ~1,500 customers
    
    **2. Complaint Fast-Track**
    - Target: 300 complainers
    - SLA: 48-hour resolution
    - Impact: Save ~75 customers
    """)

with col2:
    st.markdown("""
    ### 📈 Mid-Term Initiatives (1-3 months)
    
    **3. Inactive Re-activation**
    - Target: 4,027 inactive members
    - Tactics: Push notifications, gamification
    - Impact: Save ~229 customers
    
    **4. NPS Detractor Recovery**
    - Target: 1,643 detractors
    - Outreach within 7 days of survey
    - Impact: Save ~88 customers/year
    """)

with col3:
    st.markdown("""
    ### 🚀 Strategic Initiatives (3-12 months)
    
    **5. Digital Experience Overhaul**
    - Focus: Account Access/Online issues
    - Goal: 99.9% uptime SLA
    - Impact: 30-50 customers/year
    
    **6. Youth Retention Strategy**
    - Target: 18-25 age group
    - Offer: Fee-free accounts, education
    - Impact: Save ~97 customers/year
    """)

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Dashboard built using Streamlit | SQL queries documented in repository | Data: 10,000 UK banking customers</p>
    <p><em>Demonstrating data-driven product analysis and LLM-assisted development workflows</em></p>
</div>
""", unsafe_allow_html=True)
