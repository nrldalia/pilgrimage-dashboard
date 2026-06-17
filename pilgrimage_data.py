import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Islamic Pilgrimage Insights Dashboard (2000-2026)", 
    page_icon="🕋", 
    layout="wide"
)

# 2. Robust Data Loading Function
@st.cache_data
def load_data():
    try:
        # Tries to read it directly if it's in the same folder
        return pd.read_csv("Islamic_Pilgrimage_2000_2026_Dataset.csv")
    except FileNotFoundError:
        return None

df = load_data()

# Fallback: If it's not in the same folder, allow a drag-and-drop upload
if df is None:
    st.warning("⚠️ 'Islamic_Pilgrimage_2000_2026_Dataset.csv' was not automatically detected in your folder.")
    uploaded_file = st.file_uploader("Please upload your dataset file here:", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        st.info("💡 Place the CSV file in the same folder as this script, or upload it above to start.")
        st.stop()

# 3. Sidebar Filter Interface
st.sidebar.header("🎯 Dashboard Filters")
st.sidebar.markdown("Use these filters to slice the data across different views.")

# Filter A: Year Range Slider
min_year, max_year = int(df["Year"].min()), int(df["Year"].max())
selected_years = st.sidebar.slider("Select Year Range:", min_year, max_year, (min_year, max_year))

# Filter B: Country Multi-Select (Defaulted to top major countries)
all_countries = sorted(df["Country"].unique())
default_countries = [c for c in ["Saudi Arabia", "Pakistan", "India", "Indonesia", "Malaysia"] if c in all_countries]
selected_countries = st.sidebar.multiselect("Select Countries:", all_countries, default=default_countries if default_countries else all_countries[:5])

# Filter C: Pilgrimage Type Multi-Select
all_types = sorted(df["Pilgrimage_Type"].unique())
selected_types = st.sidebar.multiselect("Select Pilgrimage Types:", all_types, default=all_types)

# Apply All Active Sidebar Filters to the Dataframe
filtered_df = df[
    (df["Year"] >= selected_years[0]) & 
    (df["Year"] <= selected_years[1]) & 
    (df["Country"].isin(selected_countries if selected_countries else all_countries)) & 
    (df["Pilgrimage_Type"].isin(selected_types if selected_types else all_types))
]

# Add this underneath your sidebar filters
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Data Attribution")
st.sidebar.markdown(
    """
    Data sourced from **Kaggle**:  
    [Islamic Pilgrimage 2000-2026 Dataset](https://www.kaggle.com/datasets/muhammadwaqas023/islamic-pilgrimage-dataset-2000-2026/data)  
    *Acknowledge the original author/publisher for compiling this resource.*
    """
)

# 4. Main Dashboard Hero Section
st.title("🕋 Islamic Pilgrimage Global Analytics Dashboard")
st.markdown(f"Visualizing data points for **{selected_years[0]} – {selected_years[1]}** based on your sidebar selections.")
st.markdown("---")

# --- HELPER FUNCTION FOR LARGE NUMBERS ---
def format_summary_number(num):
    if num >= 1e12:
        return f"${num / 1e12:.2f}T"  # Trillions
    elif num >= 1e9:
        return f"${num / 1e9:.2f}B"   # Billions
    elif num >= 1e6:
        return f"${num / 1e6:.2f}M"   # Millions
    return f"${num:,.2f}"

# Safety Check: If filters produce an empty dataframe
if filtered_df.empty:
    st.error("❌ No data matches your active filters. Please adjust your selections in the sidebar.")
else:
    # 5. Core Operational KPIs (Top Row Metrics)
    total_pilgrims = filtered_df["Total_Pilgrims"].sum()
    total_economic_impact = filtered_df["Economic_Impact_USD"].sum()
    avg_satisfaction = filtered_df["Satisfaction_Rating"].mean()
    avg_visa_rate = filtered_df["Visa_Approval_Rate"].mean()


    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(label="Total Pilgrims", value=f"{total_pilgrims:,}")
    with m2:
    # Uses the new summary formatter
        st.metric(label="Total Economic Impact", value=format_summary_number(total_economic_impact))
    with m3:
        st.metric(label="Avg Satisfaction Score", value=f"{avg_satisfaction:.2f} / 5.00")
    with m4:
        st.metric(label="Avg Visa Approval Rate", value=f"{avg_visa_rate:.1f}%")

    st.markdown("---")

    # 6. Interactive Tab Layout for Clean Organization
    tab1, tab2, tab3 = st.tabs(["📈 Growth & Macro Trends", "🕌 Category Breakdown", "👥 Demographics & Costs"])

    with tab1:
        st.subheader("Pilgrimage Volume Growth Over Time")
        yearly_pilgrims = filtered_df.groupby("Year")["Total_Pilgrims"].sum().reset_index()
        st.line_chart(yearly_pilgrims, x="Year", y="Total_Pilgrims", use_container_width=True)
        
        st.subheader("Economic Contribution Trend ($ USD)")
        yearly_economic = filtered_df.groupby("Year")["Economic_Impact_USD"].sum().reset_index()
        st.line_chart(yearly_economic, x="Year", y="Economic_Impact_USD", use_container_width=True)

    with tab2:
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("Distribution by Pilgrimage Type")
            type_data = filtered_df.groupby("Pilgrimage_Type")["Total_Pilgrims"].sum().reset_index()
            st.bar_chart(type_data, x="Pilgrimage_Type", y="Total_Pilgrims", use_container_width=True)
            
        with col_right:
            st.subheader("Top Contributing Countries (by Pilgrim Volume)")
            country_data = filtered_df.groupby("Country")["Total_Pilgrims"].sum().reset_index().sort_values(by="Total_Pilgrims", ascending=False)
            st.bar_chart(country_data.head(10), x="Country", y="Total_Pilgrims", use_container_width=True)

    with tab3:
        col_d1, col_d2, col_d3 = st.columns(3)
        
        with col_d1:
            st.markdown("### 🎂 Age Profile")
            mean_age = filtered_df['Average_Age'].mean()
            st.metric(label="Average Pilgrim Age", value=f"{mean_age:.1f} Years Old")
            
        with col_d2:
            st.markdown("### 👥 Gender Breakdown")
            avg_male = filtered_df["Male_Percentage"].mean()
            avg_female = filtered_df["Female_Percentage"].mean()
            st.progress(int(avg_male), text=f"👨 Male: {avg_male:.1f}%")
            st.progress(int(avg_female), text=f"👩 Female: {avg_female:.1f}%")
            
        with col_d3:
            st.markdown("### 💰 Financials")
            mean_cost = filtered_df['Average_Travel_Cost_USD'].mean()
            st.metric(label="Average Travel Cost", value=f"${mean_cost:,.2f}")

    # 7. Exploratory Raw Data Table at the bottom
    st.markdown("---")
    st.subheader("📋 Filtered Raw Data Explorer")
    st.markdown("This spreadsheet updates automatically as you interact with the filters.")
    st.dataframe(filtered_df, use_container_width=True)