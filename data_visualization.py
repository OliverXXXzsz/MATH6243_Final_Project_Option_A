import streamlit as st
import pandas as pd
import plotly.express as px
from huggingface_hub import hf_hub_download

# Set page layout to wide
st.set_page_config(page_title="Tax Shift Simulation", layout="wide")

st.title("🏛️ Cook County Land Tax Shift Simulation (2025)")
st.markdown("This application demonstrates the **Distributional Impact** of shifting from the current property tax system to a **Pure Land Value Tax (LVT)**.")

# 1. Load data (use caching for performance)
@st.cache_data
def load_data():
    file_path = hf_hub_download(
        repo_id="OliverZSZ/math6243-cook-county-tax-shift-data",
        filename="dist_2025_df.csv",
        repo_type="dataset"
    )
    return pd.read_csv(file_path)

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
df["dynamic_pct_change"] = df["dynamic_tax_diff"] / df["tax_current_2025"]
df["dynamic_hurt"] = (df["dynamic_tax_diff"] > 0).astype(int)

# 3. Top Key Performance Indicators (KPIs)
col1, col2, col3 = st.columns(3)
col1.metric("Dynamic Land-Only Rate", f"{dynamic_land_rate:.4%}", f"Baseline: 7.9868%", delta_color="inverse")
share_helped = df["dynamic_helped"].mean()
col2.metric("Share Helped (Paying Less)", f"{share_helped:.2%}")
col3.metric("Share Hurt (Paying More)", f"{1 - share_helped:.2%}", delta_color="inverse")

st.divider()

# 4. Use Tabs to categorize the Plots
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Impact by Value Decile", 
    "📉 Distribution Shape",
    "🏠 Impact by Residence Type", 
    "🏗️ Impact by Building Size",
    "🌲 Feature Importance"
])

with tab1:
    st.subheader("Impact by Property Value Decile")

    decile_summary = df.groupby("value_decile_2025").agg(
        median_tax_diff=("dynamic_tax_diff", "median"),
        share_helped=("dynamic_helped", "mean")
    ).reset_index()

    # Plot 1A: Share helped by value decile
    fig_share_decile = px.bar(
        decile_summary,
        x="value_decile_2025",
        y="share_helped",
        labels={
            "value_decile_2025": "Property Value Decile (1=Lowest, 10=Highest)",
            "share_helped": "Share Paying Less"
        },
        title="Share Helped by Property Value Decile"
    )
    fig_share_decile.update_layout(yaxis_tickformat=".0%")
    st.plotly_chart(fig_share_decile, use_container_width=True)

    # Plot 1B: Median tax change by value decile
    decile_summary["Impact"] = decile_summary["median_tax_diff"].apply(
        lambda x: "Tax Decrease (Helped)" if x < 0 else "Tax Increase (Hurt)"
    )

    fig_decile = px.bar(
        decile_summary,
        x="value_decile_2025",
        y="median_tax_diff",
        color="Impact",
        color_discrete_map={
            "Tax Decrease (Helped)": "#2ca02c",
            "Tax Increase (Hurt)": "#d62728"
        },
        labels={
            "value_decile_2025": "Property Value Decile (1=Lowest, 10=Highest)",
            "median_tax_diff": "Median Tax Change ($)"
        },
        title="Median Tax Change by Property Value Decile"
    )
    st.plotly_chart(fig_decile, use_container_width=True)

with tab2:
    st.subheader("Distribution of Percent Tax Change")

    # Trim extreme 1% tails for readability, matching notebook logic
    lower = df["dynamic_pct_change"].quantile(0.01)
    upper = df["dynamic_pct_change"].quantile(0.99)

    hist_df = df[
        (df["dynamic_pct_change"] >= lower) &
        (df["dynamic_pct_change"] <= upper)
    ].copy()

    fig_hist = px.histogram(
        hist_df,
        x="dynamic_pct_change",
        nbins=50,
        labels={"dynamic_pct_change": "Percent Change in Simulated Tax Burden"},
        title="Distribution of Simulated Percent Tax Change"
    )

    fig_hist.add_vline(x=0, line_dash="dash", line_color="red")
    fig_hist.update_layout(
        xaxis_tickformat=".0%",
        yaxis_title="Number of Parcels"
    )

    st.plotly_chart(fig_hist, use_container_width=True)

    st.caption(
        f"Displaying observations between the 1st and 99th percentiles "
        f"for readability: {lower:.2%} to {upper:.2%}."
    )

with tab3:
    st.subheader("Impact by Residence Type")

    res_summary = (
        df.dropna(subset=["type_of_residence"])
        .groupby("type_of_residence")
        .agg(
            share_helped=("dynamic_helped", "mean"),
            median_tax_diff=("dynamic_tax_diff", "median"),
            n_parcels=("pin", "count")
        )
        .reset_index()
        .sort_values("share_helped", ascending=True)
    )

    # Share helped
    fig_res_share = px.bar(
        res_summary,
        x="share_helped",
        y="type_of_residence",
        orientation="h",
        hover_data=["n_parcels"],
        labels={
            "share_helped": "Share Paying Less",
            "type_of_residence": "Type of Residence"
        },
        title="Share Helped by Residence Type"
    )
    fig_res_share.update_layout(xaxis_tickformat=".1%")
    st.plotly_chart(fig_res_share, use_container_width=True)

    # Median tax change
    fig_res_median = px.bar(
        res_summary,
        x="median_tax_diff",
        y="type_of_residence",
        orientation="h",
        hover_data=["n_parcels"],
        labels={
            "median_tax_diff": "Median Tax Change ($)",
            "type_of_residence": "Type of Residence"
        },
        title="Median Tax Change by Residence Type"
    )
    fig_res_median.add_vline(x=0, line_dash="dash", line_color="red")
    st.plotly_chart(fig_res_median, use_container_width=True)

    # Building size Quintile tab
with tab4:
    st.subheader("Impact by Building Size Quintile")

    size_df = df.dropna(subset=["building_sqft"]).copy()
    size_df = size_df[size_df["building_sqft"] > 0].copy()

    size_df["building_sqft_quintile"] = pd.qcut(
        size_df["building_sqft"],
        q=5,
        labels=False,
        duplicates="drop"
    ) + 1

    size_summary = (
        size_df.groupby("building_sqft_quintile")
        .agg(
            n_parcels=("pin", "count"),
            share_helped=("dynamic_helped", "mean"),
            median_tax_diff=("dynamic_tax_diff", "median")
        )
        .reset_index()
    )

    # Share helped by building size quintile
    fig_size_share = px.bar(
        size_summary,
        x="building_sqft_quintile",
        y="share_helped",
        labels={
            "building_sqft_quintile": "Building Square Footage Quintile",
            "share_helped": "Share Paying Less"
        },
        title="Share Helped by Building Size Quintile"
    )
    fig_size_share.update_layout(yaxis_tickformat=".0%")
    st.plotly_chart(fig_size_share, use_container_width=True)

    # Median tax change by building size quintile
    fig_size_median = px.bar(
        size_summary,
        x="building_sqft_quintile",
        y="median_tax_diff",
        labels={
            "building_sqft_quintile": "Building Square Footage Quintile",
            "median_tax_diff": "Median Tax Change ($)"
        },
        title="Median Tax Change by Building Size Quintile"
    )
    fig_size_median.add_hline(y=0, line_dash="dash", line_color="red")
    st.plotly_chart(fig_size_median, use_container_width=True)

    # Feature importance tab
with tab5:
    st.subheader("Decision Tree Model Feature Importance")

    feature_data = {
        "Feature": [
            "building_sqft",
            "single_v_multi_family (Single-Family)",
            "year_built",
            "num_full_baths",
            "land_sqft"
        ],
        "Importance": [0.5724, 0.0901, 0.0812, 0.0699, 0.0628]
    }

    imp_df = pd.DataFrame(feature_data).sort_values("Importance", ascending=True)

    fig_imp = px.bar(
        imp_df,
        x="Importance",
        y="Feature",
        orientation="h",
        labels={"Importance": "Gini Importance", "Feature": "Property Feature"},
        title="Top 5 Most Important Features in Predicting 2025 Assessed Value"
    )
    st.plotly_chart(fig_imp, use_container_width=True)