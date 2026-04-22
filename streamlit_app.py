import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import this

# Title
st.title("🚗 Vehicle Lifecycle Cost Analysis")

# Load Data
df = pd.read_csv("data/vehicles.csv")

# Sidebar Inputs
st.sidebar.header("User Inputs")

years = st.sidebar.slider("Ownership Period (years)", 5, 20, 20)
annual_km = st.sidebar.slider("Annual Distance (km)", 5000, 30000, 12000)

body_type = st.sidebar.selectbox(
    "Select Body Type",
    df["Body_Type"].unique()
)

# Filter data
filtered_df = df[df["Body_Type"] == body_type]

# TCO Calculation Function
def calculate_tco(row):
    total_km = years * annual_km

    fuel_cost = (total_km / row["Mileage"]) * row["Fuel_Price"]
    maintenance_cost = row["Maintenance_Year"] * years
    insurance_cost = row["Insurance_Year"] * years
    tyre_cost = row["Tyre_Cost_Year"] * years
    battery_cost = row["Battery_Cost"]

    total_cost = (
        row["Buying_Cost"] +
        fuel_cost +
        maintenance_cost +
        insurance_cost +
        tyre_cost +
        battery_cost
    )

    return total_cost

# Apply calculation
filtered_df["Total Cost"] = filtered_df.apply(calculate_tco, axis=1)
filtered_df["Cost_per_km"] = filtered_df["Total Cost"] / (years * annual_km)

# Display Table
st.subheader("📊 Total Cost Comparison")
st.dataframe(filtered_df[["Powertrain", "Total Cost", "Cost_per_km"]])

# Bar Chart
st.subheader("📈 Total Cost by Powertrain")

fig, ax = plt.subplots()
ax.bar(filtered_df["Powertrain"], filtered_df["Total Cost"])
ax.set_xlabel("Powertrain")
ax.set_ylabel("Total Cost (₹)")
ax.set_title("Lifecycle Cost Comparison")

st.pyplot(fig)

# Cost Breakdown (for first row as example)
st.subheader("🔍 Cost Breakdown Example")

row = filtered_df.iloc[0]

labels = ["Fuel", "Maintenance", "Insurance", "Tyres", "Battery"]
values = [
    (years * annual_km / row["Mileage"]) * row["Fuel_Price"],
    row["Maintenance_Year"] * years,
    row["Insurance_Year"] * years,
    row["Tyre_Cost_Year"] * years,
    row["Battery_Cost"]
]

fig2, ax2 = plt.subplots()
ax2.pie(values, labels=labels, autopct='%1.1f%%')
ax2.set_title(f"Cost Breakdown - {row['Powertrain']}")

st.pyplot(fig2)