import streamlit as st
import pandas as pd
import plotly.express as px

# Set page layout to wide
st.set_page_config(page_title="Tax Shift Simulation", layout="wide")

st.title("🏛️ Chicago / Cook County Land Tax Shift Simulation (2025)")
st.markdown("This application demonstrates the **Distributional Impact** of shifting from the current property tax system to a **Pure Land Value Tax (LVT)**.")

# 1. Load data (use caching for performance)
@st.cache_data
def load_data():
    return pd.read_csv("dist_2025_df.csv")

df = load_data()

# 2. Sidebar: Interactive Policy Parameters
st.sidebar.header("⚙️ Policy Parameters")
# Allow users to adjust the target revenue ratio (1.0 represents absolute Revenue Neutrality)
revenue_target = st.sidebar.slider(
    "Revenue Target Ratio", 
    min_value=0.8, 
    max_value=1.2, 
    value=1.0, 
    step=0.01,
    help="1.0 = Revenue Neutral. >1.0 generates a surplus, <1.0 generates a deficit."
)

# Dynamically recalculate tax rate and differences
current_total_tax = df["tax_current_2025"].sum()
target_tax = current_total_tax * revenue_target
dynamic_land_rate = target_tax / df["land_av"].sum()

df["dynamic_tax_land_only"] = dynamic_land_rate * df["land_av"]
df["dynamic_tax_diff"] = df["dynamic_tax_land_only"] - df["tax_current_2025"]
df["dynamic_helped"] = (df["dynamic_tax_diff"] < 0).astype(int)

# 3. Top Key Performance Indicators (KPIs)
col1, col2, col3 = st.columns(3)
col1.metric("Dynamic Land-Only Rate", f"{dynamic_land_rate:.4%}", f"Baseline: 7.9868%", delta_color="inverse")
share_helped = df["dynamic_helped"].mean()
col2.metric("Share Helped (Paying Less)", f"{share_helped:.2%}")
col3.metric("Share Hurt (Paying More)", f"{1 - share_helped:.2%}", delta_color="inverse")

st.divider()

# 4. Use Tabs to categorize the Plots
tab1, tab2, tab3 = st.tabs([
    "📊 Impact by Value Decile", 
    "🏠 Impact by Residence Type", 
    "🌲 Feature Importance"
])

with tab1:
    st.subheader("Median Tax Change by Property Value Decile")
    # Dynamically aggregate data (corresponds to decile_summary_2025)
    decile_summary = df.groupby("value_decile_2025").agg(
        median_tax_diff=("dynamic_tax_diff", "median"),
        share_helped=("dynamic_helped", "mean")
    ).reset_index()
    
    # Use Plotly to draw an interactive bar chart
    decile_summary["Impact"] = decile_summary["median_tax_diff"].apply(
        lambda x: "Tax Decrease (Helped)" if x < 0 else "Tax Increase (Hurt)"
    )
    
    fig_decile = px.bar(
        decile_summary, 
        x="value_decile_2025", 
        y="median_tax_diff", 
        color="Impact",
        color_discrete_map={"Tax Decrease (Helped)": "#2ca02c", "Tax Increase (Hurt)": "#d62728"},
        labels={
            "value_decile_2025": "Property Value Decile (1=Lowest, 10=Highest)", 
            "median_tax_diff": "Median Tax Change ($)"
        },
        title="Distributional Impact by Property Value Decile"
    )
    st.plotly_chart(fig_decile, use_container_width=True)

with tab2:
    st.subheader("Share Helped by Residence Type")
    # Corresponds to res_summary
    res_summary = df.dropna(subset=["type_of_residence"]).groupby("type_of_residence").agg(
        share_helped=("dynamic_helped", "mean"),
        n_parcels=("pin", "count")
    ).reset_index().sort_values("share_helped", ascending=True)
    
    fig_res = px.bar(
        res_summary, 
        x="share_helped", 
        y="type_of_residence", 
        orientation='h',
        hover_data=["n_parcels"], # Hover to show sample size
        labels={
            "share_helped": "Share Paying Less", 
            "type_of_residence": "Type of Residence"
        },
        title="Proportion of Benefiting Parcels by Residence Type"
    )
    fig_res.update_layout(xaxis_tickformat='.1%')
    st.plotly_chart(fig_res, use_container_width=True)

with tab3:
    st.subheader("Decision Tree Model Feature Importance")
    # Hardcoded results from the Notebook, or load importance_df as csv
    feature_data = {
        "Feature": ["building_sqft", "single_family", "year_built", "num_full_baths", "land_sqft"],
        "Importance": [0.5724, 0.0901, 0.0812, 0.0699, 0.0628]
    }
    imp_df = pd.DataFrame(feature_data).sort_values("Importance", ascending=True)
    fig_imp = px.bar(
        imp_df, 
        x="Importance", 
        y="Feature", 
        orientation='h',
        labels={"Importance": "Gini Importance", "Feature": "Property Feature"},
        title="Top 5 Most Important Features in Predicting 2025 Assessed Value"
    )
    st.plotly_chart(fig_imp, use_container_width=True)