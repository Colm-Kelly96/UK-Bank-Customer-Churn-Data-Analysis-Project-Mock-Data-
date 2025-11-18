import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, f1_score, roc_auc_score
import xgboost as xgb
import shap
import matplotlib.pyplot as plt

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
        c.customer_id, c.surname, c.age, c.gender, c.region,
        a.balance, a.num_products, a.tenure, a.estimated_salary,
        e.is_active_member, e.card_type,
        co.has_complaint, co.satisfaction_score, co.complaint_category, co.nps_band,
        ch.has_exited
    FROM customers c
    JOIN accounts a ON c.customer_id = a.customer_id
    JOIN engagement e ON c.customer_id = e.customer_id
    JOIN complaints co ON c.customer_id = co.customer_id
    JOIN churn ch ON c.customer_id = ch.customer_id
    """
    return pd.read_sql_query(query, conn)

df = load_data()

# ==================== SIDEBAR FILTERS ====================
st.sidebar.header("🔍 Filters")
selected_region = st.sidebar.multiselect("Region", options=df['region'].unique(), default=df['region'].unique())
selected_gender = st.sidebar.multiselect("Gender", options=df['gender'].unique(), default=df['gender'].unique())
selected_age = st.sidebar.slider("Age Range", int(df['age'].min()), int(df['age'].max()), (18, 80))

# Apply filters
df_filtered = df[
    df['region'].isin(selected_region) &
    df['gender'].isin(selected_gender) &
    (df['age'].between(selected_age[0], selected_age[1]))
].copy()

st.sidebar.info(f"Showing {len(df_filtered):,} of {len(df):,} customers")

# Use df_filtered for all calculations below
df = df_filtered

# ==================== TITLE & OVERVIEW ====================
st.title("🏦 UK Bank Customer Churn Analysis")
st.markdown("### Strategic Retention Insights Dashboard")
st.markdown("---")

st.subheader("📊 Executive Overview")
col1, col2, col3, col4 = st.columns(4)

total_customers = len(df)
churned = df['has_exited'].sum()
churn_rate = (churned / total_customers) * 100 if total_customers > 0 else 0
retained = total_customers - churned

with col1:
    st.metric("Total Customers", f"{total_customers:,}")
with col2:
    st.metric("Churned Customers", f"{churned:,}", delta=f"{churn_rate:.2f}%", delta_color="inverse")
with col3:
    st.metric("Retained Customers", f"{retained:,}")
with col4:
    st.metric("Overall Churn Rate", f"{churn_rate:.2f}%")

st.markdown("---")

# ==================== TOP 5 CHURN DRIVERS (DYNAMIC) ====================
st.subheader("⚠️ Top 5 Churn Drivers")

overall_churn = df['has_exited'].mean()

drivers = []

# Has Complaint
group = df[df['has_complaint'] == 'Yes']
if len(group) > 0:
    drivers.append({
        'churn_driver': 'Has Complaint: Yes',
        'churn_percentage': group['has_exited'].mean() * 100,
        'risk_multiplier': group['has_exited'].mean() / overall_churn,
        'total_customers': len(group),
        'churned_customers': group['has_exited'].sum()
    })

# Single Product
group = df[df['num_products'] == 1]
if len(group) > 0:
    drivers.append({
        'churn_driver': 'Number of Products: 1',
        'churn_percentage': group['has_exited'].mean() * 100,
        'risk_multiplier': group['has_exited'].mean() / overall_churn,
        'total_customers': len(group),
        'churned_customers': group['has_exited'].sum()
    })

# NPS Detractor
group = df[df['nps_band'] == 'Detractor']
if len(group) > 0:
    drivers.append({
        'churn_driver': 'NPS Band: Detractor',
        'churn_percentage': group['has_exited'].mean() * 100,
        'risk_multiplier': group['has_exited'].mean() / overall_churn,
        'total_customers': len(group),
        'churned_customers': group['has_exited'].sum()
    })

# Inactive Member
group = df[df['is_active_member'] == 'No']
if len(group) > 0:
    drivers.append({
        'churn_driver': 'Active Member: No',
        'churn_percentage': group['has_exited'].mean() * 100,
        'risk_multiplier': group['has_exited'].mean() / overall_churn,
        'total_customers': len(group),
        'churned_customers': group['has_exited'].sum()
    })

# Young customers
df['age_group'] = pd.cut(df['age'], bins=[0, 25, 40, 60, 100], labels=['18-25', '26-40', '41-60', '61+'])
group = df[df['age_group'] == '18-25']
if len(group) > 0:
    drivers.append({
        'churn_driver': 'Age Group: 18-25',
        'churn_percentage': group['has_exited'].mean() * 100,
        'risk_multiplier': group['has_exited'].mean() / overall_churn,
        'total_customers': len(group),
        'churned_customers': group['has_exited'].sum()
    })

churn_drivers_df = pd.DataFrame(drivers).sort_values('churned_customers', ascending=False).head(5).reset_index(drop=True)
churn_drivers_df['rank'] = range(1, len(churn_drivers_df) + 1)
churn_drivers_df['churn_percentage'] = churn_drivers_df['churn_percentage'].apply(lambda x: f"{x:.2f}%")
churn_drivers_df['risk_multiplier'] = churn_drivers_df['risk_multiplier'].apply(lambda x: f"{x:.2f}x")

st.dataframe(churn_drivers_df[['rank', 'churn_driver', 'churn_percentage', 'risk_multiplier', 'total_customers', 'churned_customers']],
             use_container_width=True, height=250)

fig_drivers = go.Figure()
fig_drivers.add_trace(go.Bar(
    x=churn_drivers_df['churn_driver'],
    y=churn_drivers_df['churned_customers'],
    text=churn_drivers_df['churn_percentage'],
    textposition='outside',
    marker_color='#ff6b6b'
))
fig_drivers.update_layout(title="Churned Customers by Driver", xaxis_title="Driver", yaxis_title="Churned Customers", height=400, showlegend=False)
st.plotly_chart(fig_drivers, use_container_width=True)

st.markdown("---")

# ==================== HIGH-RISK COMBINATION SEGMENTS ====================
st.subheader("🎯 High-Risk Combination Segments")

st.markdown("#### Volume Retention (Top 10 by Number of Churned Customers)")
st.markdown("**Focus: Prevent the largest volume of churn through scalable interventions**")

# Example dynamic combos - you can expand this logic
combos_volume = []
for col in ['num_products', 'is_active_member']:
    for val in df[col].unique():
        subset = df[df[col] == val]
        if len(subset) > 100:
            combos_volume.append({
                'segment': f"{col.replace('_', ' ').title()}: {val}",
                'total': len(subset),
                'churned': subset['has_exited'].sum(),
                'churn_rate': subset['has_exited'].mean()
            })

combo_vol_df = pd.DataFrame(combos_volume).sort_values('churned', ascending=False).head(10)
st.dataframe(combo_vol_df.style.format({'total': '{:,}', 'churned': '{:,}', 'churn_rate': '{:.2%}'}), use_container_width=True, height=400)

st.markdown("---")

st.markdown("#### Crisis Management (Top 10 by Churn Percentage)")
st.markdown("**🔥 Key Insight: 9 of the top 10 highest-churn segments involve an active complaint**  \nComplaints are the #1 predictor of imminent churn — resolving them fast is non-negotiable.")

# High % combos (especially with complaints)
combos_crisis = []
complaint_df = df[df['has_complaint'] == 'Yes']
for col in ['nps_band', 'num_products', 'is_active_member', 'age_group']:
    for val in complaint_df[col].unique():
        subset = complaint_df[complaint_df[col] == val]
        if len(subset) > 20:
            combos_crisis.append({
                'segment': f"Has Complaint + {col.replace('_', ' ').title()}: {val}",
                'total': len(subset),
                'churned': subset['has_exited'].sum(),
                'churn_rate': subset['has_exited'].mean()
            })

combo_crisis_df = pd.DataFrame(combos_crisis).sort_values('churn_rate', ascending=False).head(10)
st.dataframe(combo_crisis_df.style.format({'total': '{:,}', 'churned': '{:,}', 'churn_rate': '{:.2%}'})
             .background_gradient(subset=['churn_rate'], cmap='Reds'), use_container_width=True, height=400)

st.markdown("---")

# ==================== DUAL-STRATEGY RETENTION FRAMEWORK ====================
st.subheader("💡 Recommended Retention Strategy")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📈 Volume Retention
    **Goal: Stop the bleeding at scale**

    **Primary Target Segments:**
    - Single Product + Any Other Trait  
    - Inactive Member + Any Other Trait  

    **Recommended Actions:**
    - Cross-sell & product bundling campaigns
    - Automated re-engagement journeys
    - Loyalty incentives for adding a second product
    - Digital nudges for inactive accounts

    **Expected Impact:**  
    Prevent thousands of churns per year with high ROI
    """)

with col2:
    st.markdown("""
    ### 🚨 Crisis Management
    **Goal: Stop customers about to leave now**

    **Primary Target Segments:**
    - Has Active Complaint + Any Other Trait  

    **Recommended Actions:**
    - 48-hour complaint resolution SLA
    - Dedicated retention team
    - Service recovery offers
    - Root-cause analysis & process fixes

    **Expected Impact:**  
    Turn 70–80%+ risk into retention or advocacy
    """)

st.info("""
**Core Strategic Principle:**  
Apply the right strategy to the right segment:  

→ Use **Volume Retention** for broad, high-impact segments like single-product or inactive customers  
→ Switch to **Crisis Management** the moment a complaint appears — speed wins here  

This dual approach maximizes both scale and urgency for the highest retention ROI.
""")

st.markdown("---")

# ==================== PREDICTIVE CHURN MODELING ====================
st.subheader("🔮 Predictive Churn Modeling")
st.markdown("**XGBoost + SHAP • Live customer risk scoring**")

@st.cache_data(show_spinner="Training predictive model...")
def train_churn_model(_df):
    df_model = _df.copy()
    df_model['age_group'] = pd.cut(df_model['age'], bins=[0, 25, 40, 60, 100], labels=['18-25', '26-40', '41-60', '61+'])
    df_model['balance_salary_ratio'] = df_model['balance'] / (df_model['estimated_salary'] + 1)
    df_model['is_zero_balance'] = (df_model['balance'] == 0).astype(int)
    df_model['tenure_per_product'] = df_model['tenure'] / df_model['num_products'].replace(0, 1)

    cat_cols = ['gender', 'region', 'card_type', 'complaint_category', 'nps_band', 'age_group', 'has_complaint']
    encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        df_model[col] = le.fit_transform(df_model[col].astype(str))
        encoders[col] = le

    features = ['age', 'balance', 'num_products', 'tenure', 'estimated_salary', 'is_active_member',
                'satisfaction_score', 'balance_salary_ratio', 'is_zero_balance', 'tenure_per_product',
                'gender', 'region', 'card_type', 'complaint_category', 'nps_band', 'age_group', 'has_complaint']

    X = df_model[features]
    y = df_model['has_exited']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = xgb.XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.05,
                              subsample=0.8, colsample_bytree=0.8, random_state=42, eval_metric='logloss')
    model.fit(X_train, y_train)

    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)

    metrics = {
        'AUC ROC': roc_auc_score(y_test, y_proba),
        'Accuracy': accuracy_score(y_test, y_pred),
        'Precision': precision_score(y_test, y_pred),
        'F1-Score': f1_score(y_test, y_pred)
    }

    explainer = shap.TreeExplainer(model)

    return model, explainer, features, metrics, encoders, X_test

model, explainer, features, metrics, encoders, X_test = train_churn_model(df)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("AUC ROC", f"{metrics['AUC ROC']:.3f}", delta="Excellent" if metrics['AUC ROC'] > 0.85 else "")
with col2:
    st.metric("Accuracy", f"{metrics['Accuracy']:.1%}")
with col3:
    st.metric("Precision", f"{metrics['Precision']:.1%}")
with col4:
    st.metric("F1-Score", f"{metrics['F1-Score']:.3f}")

# SHAP Summary
st.markdown("#### Global Feature Impact (SHAP)")
fig, ax = plt.subplots()
shap.summary_plot(explainer.shap_values(X_test.sample(300)), X_test.sample(300), feature_names=features, show=False, max_display=10)
st.pyplot(fig)

# Live Prediction Tool
st.markdown("#### 🔍 Predict Churn Risk for Any Customer")
col1, col2 = st.columns(2)
with col1:
    age = st.slider("Age", 18, 92, 38)
    gender = st.selectbox("Gender", ['Male', 'Female'])
    region = st.selectbox("Region", sorted(df['region'].unique()))
    balance = st.number_input("Balance (£)", 0, 250000, 50000)
    salary = st.number_input("Salary (£)", 0, 200000, 100000)
    products = st.slider("Products", 1, 4, 1)
with col2:
    tenure = st.slider("Tenure (years)", 0, 10, 5)
    active = st.selectbox("Active Member?", ['Yes', 'No'])
    complaint = st.selectbox("Has Complaint?", ['Yes', 'No'])
    card = st.selectbox("Card Type", sorted(df['card_type'].unique()))
    satisfaction = st.slider("Satisfaction", 1, 5, 3)
    nps = st.selectbox("NPS Band", ['Promoter', 'Passive', 'Detractor', 'Not Surveyed'])

input_df = pd.DataFrame([{
    'age': age, 'balance': balance, 'num_products': products, 'tenure': tenure,
    'estimated_salary': salary, 'is_active_member': 1 if active == 'Yes' else 0,
    'satisfaction_score': satisfaction, 'has_complaint': 1 if complaint == 'Yes' else 0,
    'gender': gender, 'region': region, 'card_type': card, 'nps_band': nps,
    'age_group': '18-25' if age <= 25 else '26-40' if age <= 40 else '41-60' if age <= 60 else '61+',
    'balance_salary_ratio': balance / (salary + 1),
    'is_zero_balance': 1 if balance == 0 else 0,
    'tenure_per_product': tenure / products
}])

for col in ['gender', 'region', 'card_type', 'nps_band', 'age_group', 'has_complaint']:
    le = encoders.get(col, LabelEncoder().fit(df[col].astype(str)))
    input_df[col] = le.transform(input_df[col].astype(str))

prob = model.predict_proba(input_df[features])[0, 1]
risk = "High Risk 🚨" if prob > 0.6 else "Medium Risk ⚠️" if prob > 0.3 else "Low Risk ✅"
color = "#ff3333" if prob > 0.6 else "#ffaa00" if prob > 0.3 else "#00cc00"

st.markdown(f"""
<div style="padding: 20px; border-radius: 12px; background-color: {color}22; border: 3px solid {color}; text-align: center;">
    <h2>Churn Probability: <b>{prob:.1%}</b></h2>
    <h3>{risk}</h3>
</div>
""", unsafe_allow_html=True)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Dashboard built using Streamlit + Python + XGBoost + SHAP | Analysis of 10,000 UK banking customers</p>
    <p>Built by Colm Kelly | <a href="https://www.linkedin.com/in/colm-kelly96/" target="_blank">LinkedIn</a> | <a href="https://github.com/Colm-Kelly96" target="_blank">GitHub</a></p>
</div>
""", unsafe_allow_html=True)
