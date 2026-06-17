import sys
import os

import streamlit as st
import pandas as pd
import plotly.express as px

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from optimizer import optimize_inventory
from heuristic import heuristic_inventory
from ai_explainer import generate_explanation

st.set_page_config(
    page_title="AI Retail Inventory Optimizer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Retail Inventory Optimization System")
st.caption("Machine Learning + Optimization for Retail Profit Planning")

st.sidebar.markdown(
"""
### AI Retail Optimizer

Machine Learning + Optimization
for Retail Inventory Planning

Features:
• Demand Forecasting
• Inventory Optimization
• AI Insights
• Scenario Simulation
"""
)

st.sidebar.title("⚙️ Scenario Simulation")

budget = st.sidebar.slider("Inventory Budget", 50000, 500000, 150000)
warehouse = st.sidebar.slider("Warehouse Capacity", 50, 500, 200)

data = pd.read_csv("data/StockRecommendation.csv")

data = data.rename(columns={
    "Product Type": "Product",
    "Recommended_Units": "Forecast_Demand"
})

cost_map = {
"Dupatta":300,
"Jeans":800,
"Kurti":600,
"Lehenga":2500,
"Nightwear":700,
"Salwar Suit":1200,
"Saree":1500,
"Skirt":500,
"T-shirt":400,
"Top/Blouse":450
}

sell_map = {
"Dupatta":700,
"Jeans":1600,
"Kurti":1300,
"Lehenga":5000,
"Nightwear":1400,
"Salwar Suit":2500,
"Saree":3000,
"Skirt":1100,
"T-shirt":900,
"Top/Blouse":1000
}

data["Cost_Price"] = data["Product"].map(cost_map)
data["Selling_Price"] = data["Product"].map(sell_map)
data["Storage_Space"] = 2

data = data.dropna()
data = data.reset_index(drop=True)
# Product Filter
product_filter = st.multiselect(
    "Select Products",
    data["Product"].unique(),
    default=data["Product"].unique()
)

filtered_data = data[data["Product"].isin(product_filter)].reset_index(drop=True)

if filtered_data.empty:
    st.warning("Please select at least one product.")
    st.stop()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Forecast Dashboard",
    "📦 Inventory Optimization",
    "🧠 AI Insights",
    "⚖️ AI vs Heuristic",
    "📈 Profit Sensitivity"
])

with tab1:

    st.subheader("Forecast Demand by Product")

    chart_type = st.radio(
        "Select Visualization",
        ["Bar Chart","Pie Chart"],
        horizontal=True,
        key="forecast_chart"
    )

    if chart_type == "Bar Chart":

        fig = px.bar(
            filtered_data,
            x="Product",
            y="Forecast_Demand",
            color="Forecast_Demand",
            title="Forecast Demand by Product"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:

        fig = px.pie(
            filtered_data,
            names="Product",
            values="Forecast_Demand",
            title="Demand Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
    "Total Demand",
    int(filtered_data["Forecast_Demand"].sum())
    )

    col2.metric(
    "Products Selected",
    len(filtered_data["Product"].unique())
    )

    col3.metric(
    "Average Demand",
    int(filtered_data["Forecast_Demand"].mean())
    )

    col4.metric(
    "Peak Demand",
    int(filtered_data["Forecast_Demand"].max())
    )

with tab2:

    if st.button("Run Optimization"):
        st.session_state.results = optimize_inventory(
            filtered_data.copy(),
            budget,
            warehouse
        )

    # ✅ ALWAYS SHOW RESULTS IF THEY EXIST
    if "results" in st.session_state:

        st.subheader("Optimal Inventory Plan")
        st.dataframe(st.session_state.results)

        st.download_button(
            label="📥 Download Inventory Plan",
            data=st.session_state.results.to_csv(index=False).encode("utf-8"),
            file_name="inventory_plan.csv",
            mime="text/csv"
        )

        total_profit = st.session_state.results["Expected_Profit"].sum()
        st.success(f"Expected Profit: ₹{int(total_profit)}")

        # TOP PRODUCT SAFE
        if (st.session_state.results["Expected_Profit"] > 0).any():
            best_product = st.session_state.results.loc[
                st.session_state.results["Expected_Profit"].idxmax()
            ]

            st.info(
                f"Top Product: {best_product['Product']} "
                f"(Profit ₹{int(best_product['Expected_Profit'])})"
            )

        # ✅ SLIDER NOW SAFE
        top_n = st.slider(
            "Show Top N Products",
            1,
            len(st.session_state.results),
            5
        )

        top_products = st.session_state.results[
            st.session_state.results["Expected_Profit"] > 0
        ].sort_values(
            "Expected_Profit",
            ascending=False
        ).head(top_n)

        fig = px.bar(
            top_products,
            x="Product",
            y="Expected_Profit",
            color="Expected_Profit",
            title="Top Profitable Products"
        )

        st.plotly_chart(fig, use_container_width=True)

with tab3:

    st.subheader("AI Decision Insights")

    if "results" not in st.session_state:

        st.warning("⚠️ Run Inventory Optimization first.")

    else:

        if st.button("Generate AI Explanation"):
            try:
                explanation = generate_explanation(st.session_state.results)

                st.info("AI Recommendation")

                st.markdown(
                    f"""
                    ### AI Inventory Strategy

                    {explanation}
                    """
                )

            except Exception as e:
                st.error("AI explanation could not be generated")

with tab4:
    st.subheader("AI vs Heuristic Comparison")

    if "results" not in st.session_state:
        st.warning("⚠️ Run Inventory Optimization first.")
    else:
        # Run heuristic
        heuristic_products = heuristic_inventory(filtered_data, budget)

        # AI results (already computed)
        ai_results = st.session_state.results.copy()

        # -----------------------------
        # ✅ SAFE PROFIT CALCULATION
        # -----------------------------

        # Heuristic profit (safe)
        heuristic_df = filtered_data[filtered_data["Product"].isin(heuristic_products)].copy()
        if not heuristic_df.empty:
            heuristic_df["Profit"] = heuristic_df["Selling_Price"] - heuristic_df["Cost_Price"]
            heuristic_profit = heuristic_df["Profit"].sum()
        else:
            heuristic_profit = 0

        # AI profit (safe)
        if "Expected_Profit" in ai_results.columns:
            ai_profit = ai_results["Expected_Profit"].sum()
        else:
            ai_profit = 0

        # -----------------------------
        # 📊 COMPARISON TABLE
        # -----------------------------
        comparison = pd.DataFrame({
            "Method": ["Heuristic", "AI Optimization"],
            "Total Profit": [heuristic_profit, ai_profit]
        })

        st.dataframe(comparison)

        # -----------------------------
        # 📈 GRAPH (NO ERRORS GUARANTEED)
        # -----------------------------
        fig = px.bar(
            comparison,
            x="Method",
            y="Total Profit",
            color="Method",
            title="AI vs Heuristic Profit Comparison"
        )

        st.plotly_chart(fig, use_container_width=True)

        # -----------------------------
        # 🧠 EXTRA INSIGHT (VIVA BOOST)
        # -----------------------------
        if heuristic_profit > 0:
            improvement = ((ai_profit - heuristic_profit) / heuristic_profit) * 100
        else:
            improvement = 0

        st.success(f"📈 AI Improvement over Heuristic: {improvement:.2f}%")


with tab5:

    st.subheader("Profit Sensitivity Analysis")

    st.write("This analysis shows how profit changes with different budgets and warehouse capacities.")

    # Budget vs Profit
    budget_range = [50000, 100000, 150000, 200000, 250000]

    budget_profit = []

    for b in budget_range:

        sim_results = optimize_inventory(filtered_data.copy().reset_index(drop=True) , b, warehouse)

        profit = sim_results["Expected_Profit"].sum()

        budget_profit.append(profit)

    budget_df = pd.DataFrame({
        "Budget": budget_range,
        "Expected_Profit": budget_profit
    })

    fig_budget = px.line(
        budget_df,
        x="Budget",
        y="Expected_Profit",
        markers=True,
        title="Budget vs Profit"
    )

    st.plotly_chart(fig_budget, use_container_width=True)

    st.divider()

    # Warehouse vs Profit
    warehouse_range = [50, 100, 200, 300, 400]

    warehouse_profit = []

    for w in warehouse_range:

        sim_results = optimize_inventory(filtered_data.copy().reset_index(drop=True) , budget, w)

        profit = sim_results["Expected_Profit"].sum()

        warehouse_profit.append(profit)

    warehouse_df = pd.DataFrame({
        "Warehouse_Capacity": warehouse_range,
        "Expected_Profit": warehouse_profit
    })

    fig_storage = px.line(
        warehouse_df,
        x="Warehouse_Capacity",
        y="Expected_Profit",
        markers=True,
        title="Warehouse Capacity vs Profit"
    )

    st.plotly_chart(fig_storage, use_container_width=True)

    st.divider()
    
    #HeatMap
    st.subheader("Profit Scenario Analysis")

    budget_range = [50000,100000,150000,200000,250000]
    warehouse_range = [50,100,200,300,400]

    scenario_data = []

    for b in budget_range:
        for w in warehouse_range:

            sim_results = optimize_inventory(filtered_data.copy(), b, w)

            profit = sim_results["Expected_Profit"].sum()

            scenario_data.append({
                "Budget": b,
                "Warehouse_Capacity": w,
                "Expected_Profit": profit
            })

    scenario_df = pd.DataFrame(scenario_data)

    scenario_df = scenario_df.fillna(0)

    st.dataframe(scenario_df)

    scenario_df["Safe_Profit"] = scenario_df["Expected_Profit"].clip(lower=1)

    fig = px.scatter(
        scenario_df,
        x="Budget",
        y="Warehouse_Capacity",
        size="Safe_Profit",
        color="Expected_Profit",
        title="Profit Scenario Simulation",
        labels={
            "Warehouse_Capacity":"Warehouse Capacity",
            "Expected_Profit":"Profit"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

