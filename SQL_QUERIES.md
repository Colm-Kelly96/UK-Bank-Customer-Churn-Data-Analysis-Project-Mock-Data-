# Key SQL Queries - UK Bank Churn Analysis

## Overview
This document showcases advanced SQL techniques used in the churn analysis project. All queries demonstrate actionable SQL for financial services analytics.

---

## 1. Variables to Churn
**Purpose:** Identify high-risk customer segments for targeted retention campaigns
Prompt:genrate SQL code that shows data variables and their link to churn, include churn rate percentage, difference from average, and baseline churm rate. (cateogries of variables -> Age = 18-25, 26-40, 41-60, 61-85 / Balance = 0, 1-30,000, 30,001-45,000, 45,001-70,000, 70,001-150,000 / Salary = 18,000-30,000, 30,001-45,000, 45,001-70,000, 70,001-150,000) , (Data base scheme context *overview of table names, column names)

```sql
-- Query: Calculate churn rate by customer data variablesWITH churn_analysis AS (
  SELECT
    -- Overall churn rate for reference
    (SELECT 
       ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2) 
     FROM churn) AS overall_churn_rate,
    
    'Age Group' AS category,
      WHEN c.age BETWEEN 18 AND 25 THEN '18-25'
      WHEN c.age BETWEEN 26 AND 40 THEN '26-40'
      WHEN c.age BETWEEN 61 AND 85 THEN '61-85'
    END AS category_value,
    COUNT(*) AS total_customers,
    SUM(ch.has_exited) AS churned_customers,
    ROUND(
    ) AS churn_rate_diff
  FROM customers c
  JOIN churn ch ON c.customer_id = ch.customer_id
  GROUP BY 
    CASE 
      WHEN c.age BETWEEN 26 AND 40 THEN '26-40'
      WHEN c.age BETWEEN 61 AND 85 THEN '61-85'
  UNION ALL
  -- Gender analysis
    (SELECT ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2) FROM churn),
    c.gender,
    COUNT(*),
    SUM(ch.has_exited),
    ROUND(AVG(CAST(ch.has_exited AS FLOAT)) * 100, 2),
    ROUND(
      (AVG(CAST(ch.has_exited AS FLOAT)) - 
       (SELECT AVG(CAST(has_exited AS FLOAT)) FROM churn)) * 100, 
2
    )
  UNION ALL
    'Region',
    c.region,
    COUNT(*),
    SUM(ch.has_exited),
    ROUND(AVG(CAST(ch.has_exited AS FLOAT)) * 100, 2),
    ROUND(
      (AVG(CAST(ch.has_exited AS FLOAT)) - 
       (SELECT AVG(CAST(has_exited AS FLOAT)) FROM churn)) * 100, 
2
    )
  FROM customers c
  JOIN churn ch ON c.customer_id = ch.customer_id
  GROUP BY c.region
  
  UNION ALL
  
  -- Balance categories (4-Tier)
  SELECT
    (SELECT ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2) FROM churn),
    'Balance Category',
    CASE 
      WHEN a.balance = 0 THEN '£0 (Zero/Dormant)'
      WHEN a.balance >= 1 AND a.balance <= 30000 THEN '£1-30k (Low)'
      WHEN a.balance >= 30001 AND a.balance <= 80000 THEN '£30-80k (Medium)'
      WHEN a.balance >= 80001 AND a.balance <= 250000 THEN '£80-250k (High)'
    END,
    COUNT(*),
    SUM(ch.has_exited),
    ROUND(AVG(CAST(ch.has_exited AS FLOAT)) * 100, 2),
    ROUND(
      (AVG(CAST(ch.has_exited AS FLOAT)) - 
       (SELECT AVG(CAST(has_exited AS FLOAT)) FROM churn)) * 100, 
2
    )
  FROM accounts a
  JOIN churn ch ON a.customer_id = ch.customer_id
  GROUP BY 
    CASE 
      WHEN a.balance = 0 THEN '£0 (Zero/Dormant)'
      WHEN a.balance >= 1 AND a.balance <= 30000 THEN '£1-30k (Low)'
      WHEN a.balance >= 30001 AND a.balance <= 80000 THEN '£30-80k (Medium)'
      WHEN a.balance >= 80001 AND a.balance <= 250000 THEN '£80-250k (High)'
    END
  
  UNION ALL
  
  -- Salary categories (4-Tier)
  SELECT
    (SELECT ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2) FROM churn),
    'Salary Category',
    CASE 
      WHEN a.estimated_salary >= 18000 AND a.estimated_salary <= 30000 THEN '£18-30k (Low Income)'
      WHEN a.estimated_salary >= 30001 AND a.estimated_salary <= 45000 THEN '£30-45k (Middle Income)'
      WHEN a.estimated_salary >= 45001 AND a.estimated_salary <= 70000 THEN '£45-70k (Upper Middle)'
      WHEN a.estimated_salary >= 70001 AND a.estimated_salary <= 150000 THEN '£70-150k (High Income)'
    END,
    COUNT(*),
    SUM(ch.has_exited),
    ROUND(AVG(CAST(ch.has_exited AS FLOAT)) * 100, 2),
    ROUND(
      (AVG(CAST(ch.has_exited AS FLOAT)) - 
       (SELECT AVG(CAST(has_exited AS FLOAT)) FROM churn)) * 100, 
2
    )
  FROM accounts a
  JOIN churn ch ON a.customer_id = ch.customer_id
  GROUP BY 
    CASE 
      WHEN a.estimated_salary >= 18000 AND a.estimated_salary <= 30000 THEN '£18-30k (Low Income)'
      WHEN a.estimated_salary >= 30001 AND a.estimated_salary <= 45000 THEN '£30-45k (Middle Income)'
      WHEN a.estimated_salary >= 45001 AND a.estimated_salary <= 70000 THEN '£45-70k (Upper Middle)'
      WHEN a.estimated_salary >= 70001 AND a.estimated_salary <= 150000 THEN '£70-150k (High Income)'
    END
  
  UNION ALL
  
  -- Number of products analysis
  SELECT
    (SELECT ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2) FROM churn),
    'Number of Products',
    CAST(a.num_products AS TEXT),
    COUNT(*),
    SUM(ch.has_exited),
    ROUND(AVG(CAST(ch.has_exited AS FLOAT)) * 100, 2),
    ROUND(
      (AVG(CAST(ch.has_exited AS FLOAT)) - 
       (SELECT AVG(CAST(has_exited AS FLOAT)) FROM churn)) * 100, 
2
    )
  FROM accounts a
  JOIN churn ch ON a.customer_id = ch.customer_id
  GROUP BY a.num_products
  
  UNION ALL
  
  -- Tenure categories
  SELECT
    (SELECT ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2) FROM churn),
    'Tenure',
    CASE 
      WHEN a.tenure BETWEEN 0 AND 2 THEN '0-2 years'
      WHEN a.tenure BETWEEN 3 AND 5 THEN '3-5 years'
      WHEN a.tenure BETWEEN 6 AND 10 THEN '6-10 years'
      WHEN a.tenure BETWEEN 11 AND 15 THEN '11-15 years'
    END,
    COUNT(*),
    SUM(ch.has_exited),
    ROUND(AVG(CAST(ch.has_exited AS FLOAT)) * 100, 2),
    ROUND(
      (AVG(CAST(ch.has_exited AS FLOAT)) - 
       (SELECT AVG(CAST(has_exited AS FLOAT)) FROM churn)) * 100, 
2
    )
  FROM accounts a
  JOIN churn ch ON a.customer_id = ch.customer_id
  GROUP BY 
    CASE 
      WHEN a.tenure BETWEEN 0 AND 2 THEN '0-2 years'
      WHEN a.tenure BETWEEN 3 AND 5 THEN '3-5 years'
      WHEN a.tenure BETWEEN 6 AND 10 THEN '6-10 years'
      WHEN a.tenure BETWEEN 11 AND 15 THEN '11-15 years'
    END
  
  UNION ALL
  
  -- Active member status
  SELECT
    (SELECT ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2) FROM churn),
    'Active Member',
    CASE WHEN e.is_active_member = 1 THEN 'Yes' ELSE 'No' END,
    COUNT(*),
    SUM(ch.has_exited),
    ROUND(AVG(CAST(ch.has_exited AS FLOAT)) * 100, 2),
    ROUND(
      (AVG(CAST(ch.has_exited AS FLOAT)) - 
       (SELECT AVG(CAST(has_exited AS FLOAT)) FROM churn)) * 100, 
2
    )
  FROM engagement e
  JOIN churn ch ON e.customer_id = ch.customer_id
  GROUP BY e.is_active_member
  
  UNION ALL
  
  -- Card type analysis
  SELECT
    (SELECT ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2) FROM churn),
    'Card Type',
    e.card_type,
    COUNT(*),
    SUM(ch.has_exited),
    ROUND(AVG(CAST(ch.has_exited AS FLOAT)) * 100, 2),
    ROUND(
      (AVG(CAST(ch.has_exited AS FLOAT)) - 
       (SELECT AVG(CAST(has_exited AS FLOAT)) FROM churn)) * 100, 
2
    )
  FROM engagement e
  JOIN churn ch ON e.customer_id = ch.customer_id
  GROUP BY e.card_type
  
  UNION ALL
  
  -- Has Complaint (Yes/No only)
  SELECT
    (SELECT ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2) FROM churn),
    'Has Complaint',
    CASE WHEN comp.has_complaint = 1 THEN 'Yes' ELSE 'No' END,
    COUNT(*),
    SUM(ch.has_exited),
    ROUND(AVG(CAST(ch.has_exited AS FLOAT)) * 100, 2),
    ROUND(
      (AVG(CAST(ch.has_exited AS FLOAT)) - 
       (SELECT AVG(CAST(has_exited AS FLOAT)) FROM churn)) * 100, 
2
    )
  FROM complaints comp
  JOIN churn ch ON comp.customer_id = ch.customer_id
  GROUP BY comp.has_complaint
  
  UNION ALL
  
  -- Satisfaction score (for all customers)
  SELECT
    (SELECT ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2) FROM churn),
    'Satisfaction Score',
    CAST(comp.satisfaction_score AS TEXT),
    COUNT(*),
    SUM(ch.has_exited),
    ROUND(AVG(CAST(ch.has_exited AS FLOAT)) * 100, 2),
    ROUND(
      (AVG(CAST(ch.has_exited AS FLOAT)) - 
       (SELECT AVG(CAST(has_exited AS FLOAT)) FROM churn)) * 100, 
2
    )
  FROM complaints comp
  JOIN churn ch ON comp.customer_id = ch.customer_id
  GROUP BY comp.satisfaction_score
  
  UNION ALL
  
  -- NPS Band
  SELECT
    (SELECT ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2) FROM churn),
    'NPS Band',
    COALESCE(comp.nps_band, 'Not Surveyed'),
    COUNT(*),
    SUM(ch.has_exited),
    ROUND(AVG(CAST(ch.has_exited AS FLOAT)) * 100, 2),
    ROUND(
      (AVG(CAST(ch.has_exited AS FLOAT)) - 
       (SELECT AVG(CAST(has_exited AS FLOAT)) FROM churn)) * 100, 
2
    )
  FROM complaints comp
  JOIN churn ch ON comp.customer_id = ch.customer_id
  GROUP BY comp.nps_band
  
  UNION ALL
  
  -- Complaint category (only for those with complaints)
  SELECT
    (SELECT ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2) FROM churn),
    'Complaint Category',
    comp.complaint_category,
    COUNT(*),
    SUM(ch.has_exited),
    ROUND(AVG(CAST(ch.has_exited AS FLOAT)) * 100, 2),
    ROUND(
      (AVG(CAST(ch.has_exited AS FLOAT)) - 
       (SELECT AVG(CAST(has_exited AS FLOAT)) FROM churn)) * 100, 
2
    )
  FROM complaints comp
  JOIN churn ch ON comp.customer_id = ch.customer_id
  WHERE comp.has_complaint = 1
  GROUP BY comp.complaint_category
)

SELECT 
  category,
  category_value,
  total_customers,
  churned_customers,
  churn_rate || '%' AS churn_rate_pct,
  churn_rate_diff || '%' AS diff_from_avg,
  CASE 
    WHEN ABS(churn_rate_diff) >= 10 THEN 'Strong'
    WHEN ABS(churn_rate_diff) >= 5 THEN 'Moderate'
    WHEN ABS(churn_rate_diff) >= 2 THEN 'Weak'
    ELSE 'Minimal'
  END AS correlation_strength,
  overall_churn_rate || '%' AS baseline_churn_rate
FROM churn_analysis
ORDER BY 
  category,
  ABS(churn_rate_diff) DESC;
```

**Key Techniques:**
- Complex CASE statements for segment logic
- Multi-table joins (5 tables)
- Aggregate functions with GROUP BY
- Subquery for clean data preparation

**Business Value:**
- Identifies area's most linked to churn
- Enables targeted retention campaigns

---


## 2. Churn Combo variables
**Purpose:** Identify combo variables (2 variables combined) that are most likely to churn - deeper insight that only looking at 1 variable

Prompt: write an SQL query that returns linkage between the top variables i.e A+B - link all combiniation of 2 variables to show key at risk segements of chruning: Single Product Only, Inactive Member, NPS Detractor, Has Complaint, Age 18-25

WITH overall_churn AS (
  SELECT ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2) AS baseline_churn_rate
  FROM churn
),

=-- Define all categorical variables
categorized_customers AS (
  SELECT 
    c.customer_id,
    ch.has_exited,
    
    -- Age Group
    CASE 
      WHEN c.age BETWEEN 18 AND 25 THEN 'Age 18-25'
      WHEN c.age BETWEEN 26 AND 40 THEN 'Age 26-40'
      WHEN c.age BETWEEN 41 AND 60 THEN 'Age 41-60'
      WHEN c.age BETWEEN 61 AND 85 THEN 'Age 61-85'
    END AS age_group,
    
    -- Gender
    'Gender ' || c.gender AS gender,
    
    -- Region
    'Region ' || c.region AS region,
    
    -- Balance Category
    CASE 
      WHEN a.balance = 0 THEN 'Balance £0 (Zero/Dormant)'
      WHEN a.balance >= 1 AND a.balance <= 30000 THEN 'Balance £1-30k (Low)'
      WHEN a.balance >= 30001 AND a.balance <= 80000 THEN 'Balance £30-80k (Medium)'
      WHEN a.balance >= 80001 THEN 'Balance £80k+ (High)'
    END AS balance_category,
    
    -- Salary Category
    CASE 
      WHEN a.estimated_salary >= 18000 AND a.estimated_salary <= 30000 THEN 'Salary £18-30k (Low)'
      WHEN a.estimated_salary >= 30001 AND a.estimated_salary <= 45000 THEN 'Salary £30-45k (Middle)'
      WHEN a.estimated_salary >= 45001 AND a.estimated_salary <= 70000 THEN 'Salary £45-70k (Upper Middle)'
      WHEN a.estimated_salary >= 70001 THEN 'Salary £70k+ (High)'
    END AS salary_category,
    
    -- Number of Products
    CASE 
      WHEN a.num_products = 1 THEN 'Single Product Only'
      WHEN a.num_products = 2 THEN '2 Products'
      WHEN a.num_products = 3 THEN '3 Products'
      WHEN a.num_products = 4 THEN '4 Products'
    END AS products,


## 2.5 Churn Combo variables
**Purpose:** Add in priorty score - to help make clear key areas for actions. (to the  combo variables analysis above)

Prompt: add in an additional column that shows the reltive importance based on total customers and risk multipler i.e so i can order it to see the most valuable at risk segements to target - rank the priorty score out of 10 to 1decimal place
  SELECT 
    age_group AS variable_1,
    products AS variable_2,
    COUNT(*) AS total_customers,
    SUM(has_exited) AS churned_customers,
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2) AS churn_rate
  FROM categorized_customers
  WHERE age_group IS NOT NULL AND products IS NOT NULL
  GROUP BY age_group, products
  
  UNION ALL
  
  -- Age Group + Active Status
  SELECT 
    age_group,
    active_status,
    COUNT(*),
    SUM(has_exited),
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2)
  FROM categorized_customers
  WHERE age_group IS NOT NULL AND active_status IS NOT NULL
  GROUP BY age_group, active_status
  
  UNION ALL
  
  -- Age Group + NPS Band
  SELECT 
    age_group,
    nps_band,
    COUNT(*),
    SUM(has_exited),
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2)
  FROM categorized_customers
  WHERE age_group IS NOT NULL AND nps_band IS NOT NULL
  GROUP BY age_group, nps_band
  
  UNION ALL
  
  -- Age Group + Complaint Status
  SELECT 
    age_group,
    complaint_status,
    COUNT(*),
    SUM(has_exited),
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2)
  FROM categorized_customers
  WHERE age_group IS NOT NULL AND complaint_status IS NOT NULL
  GROUP BY age_group, complaint_status
  
  UNION ALL
  
  -- Age Group + Balance Category
  SELECT 
    age_group,
    balance_category,
    COUNT(*),
    SUM(has_exited),
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2)
  FROM categorized_customers
  WHERE age_group IS NOT NULL AND balance_category IS NOT NULL
  GROUP BY age_group, balance_category
  
  UNION ALL
  
  -- Products + Active Status
  SELECT 
    products,
    active_status,
    COUNT(*),
    SUM(has_exited),
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2)
  FROM categorized_customers
  WHERE products IS NOT NULL AND active_status IS NOT NULL
  GROUP BY products, active_status
  
  UNION ALL
  
  -- Products + NPS Band
  SELECT 
    products,
    nps_band,
    COUNT(*),
    SUM(has_exited),
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2)
  FROM categorized_customers
  WHERE products IS NOT NULL AND nps_band IS NOT NULL
  GROUP BY products, nps_band
  
  UNION ALL
  
  -- Products + Complaint Status
  SELECT 
    products,
    complaint_status,
    COUNT(*),
    SUM(has_exited),
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2)
  FROM categorized_customers
  WHERE products IS NOT NULL AND complaint_status IS NOT NULL
  GROUP BY products, complaint_status
  
  UNION ALL
  
  -- Products + Balance Category
  SELECT 
    products,
    balance_category,
    COUNT(*),
    SUM(has_exited),
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2)
  FROM categorized_customers
  WHERE products IS NOT NULL AND balance_category IS NOT NULL
  GROUP BY products, balance_category
  
  UNION ALL
  
  -- Active Status + NPS Band
  SELECT 
    active_status,
    nps_band,
    COUNT(*),
    SUM(has_exited),
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2)
  FROM categorized_customers
  WHERE active_status IS NOT NULL AND nps_band IS NOT NULL
  GROUP BY active_status, nps_band
  
  UNION ALL
  
  -- Active Status + Complaint Status
  SELECT 
    active_status,
    complaint_status,
    COUNT(*),
    SUM(has_exited),
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2)
  FROM categorized_customers
  WHERE active_status IS NOT NULL AND complaint_status IS NOT NULL
  GROUP BY active_status, complaint_status
  
  UNION ALL
  
  -- Active Status + Balance Category
  SELECT 
    active_status,
    balance_category,
    COUNT(*),
    SUM(has_exited),
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2)
  FROM categorized_customers
  WHERE active_status IS NOT NULL AND balance_category IS NOT NULL
  GROUP BY active_status, balance_category
  
  UNION ALL
  
  -- NPS Band + Complaint Status
  SELECT 
    nps_band,
    complaint_status,
    COUNT(*),
    SUM(has_exited),
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2)
  FROM categorized_customers
  WHERE nps_band IS NOT NULL AND complaint_status IS NOT NULL
  GROUP BY nps_band, complaint_status
  
  UNION ALL
  
  -- NPS Band + Balance Category
  SELECT 
    nps_band,
    balance_category,
    COUNT(*),
    SUM(has_exited),
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2)
  FROM categorized_customers
  WHERE nps_band IS NOT NULL AND balance_category IS NOT NULL
  GROUP BY nps_band, balance_category
  
  UNION ALL
  
  -- Complaint Status + Balance Category
  SELECT 
    complaint_status,
    balance_category,
    COUNT(*),
    SUM(has_exited),
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2)
  FROM categorized_customers
  WHERE complaint_status IS NOT NULL AND balance_category IS NOT NULL
  GROUP BY complaint_status, balance_category
  
  UNION ALL
  
  -- Gender + Products
  SELECT 
    gender,
    products,
    COUNT(*),
    SUM(has_exited),
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2)
  FROM categorized_customers
  WHERE gender IS NOT NULL AND products IS NOT NULL
  GROUP BY gender, products
  
  UNION ALL
  
  -- Gender + Active Status
  SELECT 
    gender,
    active_status,
    COUNT(*),
    SUM(has_exited),
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2)
  FROM categorized_customers
  WHERE gender IS NOT NULL AND active_status IS NOT NULL
  GROUP BY gender, active_status
  
  UNION ALL
  
  -- Gender + NPS Band
  SELECT 
    gender,
    nps_band,
    COUNT(*),
    SUM(has_exited),
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2)
  FROM categorized_customers
  WHERE gender IS NOT NULL AND nps_band IS NOT NULL
  GROUP BY gender, nps_band
  
  UNION ALL
  
  -- Tenure + Products
  SELECT 
    tenure,
    products,
    COUNT(*),
    SUM(has_exited),
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2)
  FROM categorized_customers
  WHERE tenure IS NOT NULL AND products IS NOT NULL
  GROUP BY tenure, products
  
  UNION ALL
  
  -- Tenure + Active Status
  SELECT 
    tenure,
    active_status,
    COUNT(*),
    SUM(has_exited),
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2)
  FROM categorized_customers
  WHERE tenure IS NOT NULL AND active_status IS NOT NULL
  GROUP BY tenure, active_status
  
  UNION ALL
  
  -- Card Type + Products
  SELECT 
    card_type,
    products,
    COUNT(*),
    SUM(has_exited),
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2)
  FROM categorized_customers
  WHERE card_type IS NOT NULL AND products IS NOT NULL
  GROUP BY card_type, products
  
  UNION ALL
  
  -- Card Type + Active Status
  SELECT 
    card_type,
    active_status,
    COUNT(*),
    SUM(has_exited),
    ROUND(AVG(CAST(has_exited AS FLOAT)) * 100, 2)
  FROM categorized_customers
  WHERE card_type IS NOT NULL AND active_status IS NOT NULL
  GROUP BY card_type, active_status
)

SELECT 
  variable_1 || ' + ' || variable_2 AS at_risk_segment,
  total_customers,
  churned_customers,
  churn_rate || '%' AS churn_percentage,
  ROUND(churn_rate / (SELECT baseline_churn_rate FROM overall_churn), 2) || 'x' AS risk_multiplier,
  (SELECT baseline_churn_rate || '%' FROM overall_churn) AS baseline_churn_rate
FROM two_variable_combinations
WHERE total_customers >= 50  -- Minimum sample size for statistical significance
  AND churn_rate > (SELECT baseline_churn_rate FROM overall_churn)  -- Only show above-average churn segments
ORDER BY churn_rate DESC

---

## 3. Complaint Category Impact Analysis
**Purpose:** Prioritize complaint resolution by churn impact

```sql
-- Query: Analyze churn rate by complaint category with time-to-churn
SELECT 
    co.complaint_category,
    COUNT(*) as total_complaints,
    SUM(ch.has_exited) as resulted_in_churn,
    ROUND(AVG(ch.has_exited) * 100, 1) as churn_rate_pct,
    ROUND(AVG(co.satisfaction_score), 2) as avg_satisfaction,
    -- Calculate average days between complaint and churn
    ROUND(AVG(
        CASE 
            WHEN ch.has_exited = 1 AND co.complaint_date IS NOT NULL 
            THEN JULIANDAY('2024-06-30') - JULIANDAY(co.complaint_date)
            ELSE NULL 
        END
    ), 0) as avg_days_to_churn,
    -- Calculate financial impact
    ROUND(SUM(CASE WHEN ch.has_exited = 1 THEN a.balance ELSE 0 END) / 1000, 0) 
        as lost_balance_thousands
FROM complaints co
JOIN churn ch ON co.customer_id = ch.customer_id
JOIN accounts a ON co.customer_id = a.customer_id
WHERE co.has_complaint = 1
GROUP BY co.complaint_category
ORDER BY churn_rate_pct DESC;
```

**Key Techniques:**
- Date arithmetic (JULIANDAY function)
- Conditional aggregation with CASE
- NULL handling in calculations
- Financial impact quantification

**Business Value:**
- "Product Terms Changes" complaints have 75% churn rate
- Average 120-150 days between complaint and churn (early warning window)
- Lost balance quantified: £2.4M from churned complainers
- Prioritizes complaint resolution SLAs

---

## 4. Cohort Retention Analysis
**Purpose:** Track customer retention by tenure cohort

```sql
-- Query: Cohort analysis by years as customer
WITH tenure_cohorts AS (
    SELECT 
        CASE 
            WHEN tenure <= 2 THEN '0-2 years'
            WHEN tenure <= 5 THEN '3-5 years'
            WHEN tenure <= 10 THEN '6-10 years'
            ELSE '10+ years'
        END as tenure_cohort,
        COUNT(*) as cohort_size,
        SUM(has_exited) as churned,
        ROUND(AVG(has_exited) * 100, 1) as churn_rate_pct,
        ROUND(AVG(balance), 0) as avg_balance,
        ROUND(AVG(num_products), 2) as avg_products
    FROM customers c
    JOIN accounts a ON c.customer_id = a.customer_id
    JOIN churn ch ON c.customer_id = ch.customer_id
    GROUP BY tenure_cohort
)
SELECT 
    tenure_cohort,
    cohort_size,
    churned,
    churn_rate_pct,
    avg_balance,
    avg_products,
    -- Calculate lifetime value proxy
    ROUND(avg_balance * avg_products * (1 - churn_rate_pct/100) / 1000, 1) 
        as ltv_proxy_thousands
FROM tenure_cohorts
ORDER BY 
    CASE tenure_cohort
        WHEN '0-2 years' THEN 1
        WHEN '3-5 years' THEN 2
        WHEN '6-10 years' THEN 3
        ELSE 4
    END;
```

**Key Techniques:**
- Cohort bucketing with CASE
- Lifetime value calculation
- Custom sorting with CASE in ORDER BY
- Derived metrics from aggregates

**Business Value:**
- 0-2 year cohort has highest churn (26.4%)
- Long-tenured customers (10+) extremely loyal (12.7% churn)
- Early engagement critical for retention

---

## 5. High-Value Customer At-Risk Alert
**Purpose:** Real-time identification of high-value customers showing churn signals

```sql
-- Query: Flag high-value customers with multiple churn risk factors
SELECT 
    c.customer_id,
    c.surname,
    c.age,
    c.region,
    a.balance,
    a.num_products,
    a.tenure,
    e.is_active_member,
    e.card_type,
    co.has_complaint,
    co.satisfaction_score,
    co.nps_band,
    -- Create risk score
    (CASE WHEN a.num_products = 1 THEN 3 ELSE 0 END) +
    (CASE WHEN e.is_active_member = 0 THEN 2 ELSE 0 END) +
    (CASE WHEN co.has_complaint = 1 THEN 3 ELSE 0 END) +
    (CASE WHEN co.nps_band = 'Detractor' THEN 2 ELSE 0 END) +
    (CASE WHEN c.age < 30 THEN 1 ELSE 0 END) 
        as risk_score,
    -- Estimate value at risk
    ROUND(a.balance * 0.025, 0) as estimated_annual_revenue,
    -- Days since last complaint (if any)
    CASE 
        WHEN co.complaint_date IS NOT NULL 
        THEN CAST(JULIANDAY('2024-06-30') - JULIANDAY(co.complaint_date) AS INTEGER)
        ELSE NULL 
    END as days_since_complaint
FROM customers c
JOIN accounts a ON c.customer_id = a.customer_id
JOIN engagement e ON c.customer_id = e.customer_id
JOIN complaints co ON c.customer_id = co.customer_id
JOIN churn ch ON c.customer_id = ch.customer_id
WHERE 
    ch.has_exited = 0  -- Current customers only
    AND a.balance >= 50000  -- High balance threshold
    AND (
        (a.num_products = 1 AND e.is_active_member = 0) OR  -- Critical: Single + Inactive
        (co.has_complaint = 1 AND co.satisfaction_score <= 2) OR  -- Critical: Unhappy complainers
        (co.nps_band = 'Detractor' AND e.is_active_member = 0)  -- Critical: Detractor + Inactive
    )
ORDER BY risk_score DESC, a.balance DESC
LIMIT 100;
```

**Key Techniques:**
- Multi-factor risk scoring
- Revenue estimation modeling
- Complex WHERE clause filtering
- Date difference calculation
- Business rule implementation in SQL

**Business Value:**
- Identifies top 100 at-risk high-value customers
- Combined balance at risk: £12.3M
- Enables proactive outreach before churn occurs
- Prioritization by both risk and value

---

## Summary

These queries demonstrate:

✅ **Technical Proficiency**
- Complex joins across 5 normalized tables
- CTEs for query organization
- Window functions and date arithmetic
- Aggregate functions with grouping
- CASE statements for business logic
- Financial calculations and modeling

✅ **Business Acumen**
- Customer segmentation strategies
- Risk scoring algorithms
- Revenue impact quantification
- Cohort analysis methodologies
- Prioritization frameworks

✅ **Production Readiness**
- Performance-optimized queries
- NULL handling
- Consistent naming conventions
- Clear commenting
- Scalable design patterns

---

*SQL queries developed for UK Bank Customer Churn Analysis portfolio project*
