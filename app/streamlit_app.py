import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Vehicle Cost Analysis", layout="wide")

st.title("🚗 Vehicle Lifecycle Cost Analysis")

# Load Data Safely
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/vehicles.csv")
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_data()

if df is None or df.empty:
    st.warning("Dataset not found or empty. Please check vehicles.csv")
    st.stop()

# Sidebar Inputs
st.sidebar.header("User Inputs")

years = st.sidebar.slider("Ownership Period (years)", 5, 20, 20)
annual_km = st.sidebar.slider("Annual Distance (km)", 5000, 30000, 12000)

body_type = st.sidebar.selectbox(
    "Select Body Type",
    df["Body_Type"].unique()
)

# Filter Data
filtered_df = df[df["Body_Type"] == body_type].copy()

if filtered_df.empty:
    st.warning("No data available for selected body type")
    st.stop()

# TCO Calculation
def calculate_tco(row):
    total_km = years * annual_km

    fuel_cost = (total_km / row["Mileage"]) * row["Fuel_Price"]
    maintenance_cost = row["Maintenance_Year"] * years
    insurance_cost = row["Insurance_Year"] * years
    tyre_cost = row["Tyre_Cost_Year"] * years
    battery_cost = row["Battery_Cost"]

    return (
        row["Buying_Cost"] +
        fuel_cost +
        maintenance_cost +
        insurance_cost +
        tyre_cost +
        battery_cost
    )

filtered_df["Total Cost"] = filtered_df.apply(calculate_tco, axis=1)
filtered_df["Cost_per_km"] = filtered_df["Total Cost"] / (years * annual_km)

# Display Table
st.subheader("📊 Cost Comparison")
st.dataframe(
    filtered_df[["Powertrain", "Total Cost", "Cost_per_km"]]
    .sort_values(by="Total Cost")
)

# Bar Chart
st.subheader("📈 Total Cost by Powertrain")

fig, ax = plt.subplots()
ax.bar(filtered_df["Powertrain"], filtered_df["Total Cost"])
ax.set_xlabel("Powertrain")
ax.set_ylabel("Total Cost (₹)")
ax.set_title("Lifecycle Cost Comparison")

st.pyplot(fig)

# Breakdown for selected powertrain
st.subheader("🔍 Detailed Cost Breakdown")

selected_pt = st.selectbox(
    "Select Powertrain for Breakdown",
    filtered_df["Powertrain"]
)

row = filtered_df[filtered_df["Powertrain"] == selected_pt].iloc[0]

fuel_cost = (years * annual_km / row["Mileage"]) * row["Fuel_Price"]
maintenance_cost = row["Maintenance_Year"] * years
insurance_cost = row["Insurance_Year"] * years
tyre_cost = row["Tyre_Cost_Year"] * years
battery_cost = row["Battery_Cost"]

labels = ["Fuel", "Maintenance", "Insurance", "Tyres", "Battery"]
values = [fuel_cost, maintenance_cost, insurance_cost, tyre_cost, battery_cost]

fig2, ax2 = plt.subplots()
ax2.pie(values, labels=labels, autopct='%1.1f%%')
ax2.set_title(f"{selected_pt} Cost Breakdown")

st.pyplot(fig2)

# Cost per km highlight
st.subheader("💡 Key Insight")

best = filtered_df.loc[filtered_df["Cost_per_km"].idxmin()]

st.success(
    f"Most economical option: {best['Powertrain']} "
    f"(₹ {best['Cost_per_km']:.2f} per km)"
)