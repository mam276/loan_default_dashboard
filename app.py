import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Loan Default Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">📊 Loan Default Analysis Dashboard</h1>', unsafe_allow_html=True)

# Load data with error handling
@st.cache_data
def load_data():
    try:
        df = pd.read_parquet('data/loan_data_cleaned.parquet')
        st.success(f"✅ Loaded {len(df):,} records from Parquet file")
        return df
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        st.info("Please make sure your Parquet file is in the 'data' folder")
        return None

# Load summary statistics
@st.cache_data
def load_summary():
    try:
        summary = pd.read_parquet('data/loan_summary_statistics.parquet')
        return summary
    except:
        return None

# Load default rates
@st.cache_data
def load_default_rates():
    try:
        default_rates = pd.read_csv('data/default_rates_by_purpose.csv')
        return default_rates
    except:
        return None

# Load analysis report
@st.cache_data
def load_report():
    try:
        with open('data/loan_analysis_report.txt', 'r') as f:
            report = f.read()
        return report
    except:
        return "Analysis report not found."

# Load all data
df = load_data()
summary = load_summary()
default_rates = load_default_rates()
report = load_report()

if df is None:
    st.stop()

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3441/3441358.png", width=100)
    st.markdown("# 📊 Filters")
    
    st.markdown("---")
    
    # Loan status filter
    loan_status = st.selectbox(
        "Loan Status",
        ["All", "Defaults Only", "Non-Defaults Only"]
    )
    
    # Loan amount filter
    loan_min = int(df['loan_amnt'].min())
    loan_max = int(df['loan_amnt'].max())
    loan_range = st.slider(
        "Loan Amount Range ($)",
        loan_min, loan_max,
        (loan_min, loan_max)
    )
    
    # Credit score filter
    credit_min = int(df['credit_score'].min())
    credit_max = int(df['credit_score'].max())
    credit_range = st.slider(
        "Credit Score Range",
        credit_min, credit_max,
        (credit_min, credit_max)
    )
    
    # Loan purpose filter
    all_purposes = df['loan_intent'].unique()
    selected_purposes = st.multiselect(
        "Loan Purpose",
        options=all_purposes,
        default=all_purposes
    )
    
    st.markdown("---")
    st.markdown("### 📊 Data Info")
    st.info(f"""
    - **Total Records**: {len(df):,}
    - **Columns**: {len(df.columns)}
    - **Default Rate**: {(df['loan_status'].mean()*100):.1f}%
    - **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    """)

# Apply filters
filtered_df = df.copy()

# Loan status filter
if loan_status == "Defaults Only":
    filtered_df = filtered_df[filtered_df['loan_status'] == 1]
elif loan_status == "Non-Defaults Only":
    filtered_df = filtered_df[filtered_df['loan_status'] == 0]

# Other filters
filtered_df = filtered_df[
    (filtered_df['loan_amnt'] >= loan_range[0]) &
    (filtered_df['loan_amnt'] <= loan_range[1]) &
    (filtered_df['credit_score'] >= credit_range[0]) &
    (filtered_df['credit_score'] <= credit_range[1]) &
    (filtered_df['loan_intent'].isin(selected_purposes))
]

# Display KPI Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_loans = len(filtered_df)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_loans:,}</div>
        <div class="metric-label">Total Loans</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    default_rate = filtered_df['loan_status'].mean() * 100
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{default_rate:.1f}%</div>
        <div class="metric-label">Default Rate</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    avg_interest = filtered_df['loan_int_rate'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{avg_interest:.1f}%</div>
        <div class="metric-label">Avg Interest Rate</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    avg_income = filtered_df['person_income'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">${avg_income:,.0f}</div>
        <div class="metric-label">Avg Income</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Create tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📈 Charts", "📊 Analysis Files", "🔍 Data Explorer", "📋 Report"])

with tab1:
    st.subheader("Visual Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Default rate by loan purpose
        st.markdown("**Default Rate by Loan Purpose**")
        default_by_purpose = filtered_df.groupby('loan_intent')['loan_status'].mean() * 100
        
        fig = px.bar(
            x=default_by_purpose.index,
            y=default_by_purpose.values,
            labels={'x': 'Loan Purpose', 'y': 'Default Rate (%)'},
            color=default_by_purpose.values,
            color_continuous_scale='RdYlGn_r'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Credit score distribution
        st.markdown("**Credit Score Distribution**")
        fig = px.histogram(
            filtered_df,
            x='credit_score',
            nbins=30,
            color='loan_status',
            color_discrete_map={0: 'green', 1: 'red'},
            title='Credit Score by Loan Status'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Scatter plot: Income vs Loan Amount
    st.markdown("**Income vs Loan Amount**")
    fig = px.scatter(
        filtered_df,
        x='person_income',
        y='loan_amnt',
        color='loan_status',
        size='loan_int_rate',
        hover_data=['person_age', 'person_education', 'credit_score'],
        color_discrete_map={0: 'green', 1: 'red'},
        opacity=0.7
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Analysis Files from Initial Project")
    
    # Show default rates from file
    if default_rates is not None:
        st.markdown("### Default Rates by Purpose (from file)")
        st.dataframe(default_rates, use_container_width=True)
        
        # Visualize
        fig = px.bar(
            default_rates,
            x='Loan Purpose',
            y='Default Rate (%)',
            color='Default Rate (%)',
            color_continuous_scale='RdYlGn_r'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Show summary statistics
    if summary is not None:
        st.markdown("### Summary Statistics")
        st.dataframe(summary, use_container_width=True)
    
    # Download buttons
    st.markdown("### 📥 Download Files")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Download Cleaned Data", use_container_width=True):
            st.download_button(
                label="Click to download",
                data=df.to_csv(index=False),
                file_name="loan_data_cleaned.csv",
                mime="text/csv"
            )
    
    with col2:
        if default_rates is not None:
            if st.button("Download Default Rates", use_container_width=True):
                st.download_button(
                    label="Click to download",
                    data=default_rates.to_csv(index=False),
                    file_name="default_rates_by_purpose.csv",
                    mime="text/csv"
                )
    
    with col3:
        if st.button("Download Analysis Report", use_container_width=True):
            st.download_button(
                label="Click to download",
                data=report,
                file_name="loan_analysis_report.txt",
                mime="text/plain"
            )

with tab3:
    st.subheader("Data Explorer")
    
    # Show filtered data
    st.markdown(f"### Filtered Data ({len(filtered_df):,} records)")
    
    # Column selector
    all_columns = filtered_df.columns.tolist()
    selected_columns = st.multiselect(
        "Select columns to display:",
        options=all_columns,
        default=all_columns[:8]  # Show first 8 columns by default
    )
    
    if selected_columns:
        st.dataframe(filtered_df[selected_columns], use_container_width=True, height=400)
    else:
        st.dataframe(filtered_df, use_container_width=True, height=400)
    
    # Statistics for selected column
    st.markdown("### Column Statistics")
    numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        selected_stat_col = st.selectbox("Select column for statistics:", numeric_cols)
        if selected_stat_col:
            col_stats = filtered_df[selected_stat_col].describe()
            st.dataframe(col_stats)

with tab4:
    st.subheader("Analysis Report")
    st.markdown("### Executive Summary")
    st.text_area("Report Content", report, height=400)
    
    # Key findings section
    st.markdown("### 🔑 Key Insights")
    
    insights = [
        f"• Overall default rate: **{(df['loan_status'].mean()*100):.1f}%**",
        f"• Total loans analyzed: **{len(df):,}**",
        f"• Average interest rate: **{df['loan_int_rate'].mean():.1f}%**",
        f"• Average credit score: **{df['credit_score'].mean():.0f}**",
        f"• Average loan amount: **${df['loan_amnt'].mean():,.0f}**"
    ]
    
    for insight in insights:
        st.markdown(insight)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>📊 Loan Default Analysis Dashboard | Built with Streamlit</p>
    <p>Using output files from initial analysis project</p>
</div>

""", unsafe_allow_html=True)
