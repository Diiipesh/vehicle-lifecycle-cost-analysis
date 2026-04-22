import streamlit as st
import pandas as pd

st.set_page_config(page_title="Vehicle Lifecycle Cost Analysis", layout="wide")
st.title("🚗 Vehicle Lifecycle Cost Analysis")

# -------- Load Data Safely --------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/vehicles.csv")
        if df.empty:
            st.error("vehicles.csv is empty")
            return None
        return df
    except FileNotFoundError:
        st.error("File not found: data/vehicles.csv")
        return None
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return None

df = load_data()
if df is None:
    st.stop()

required_cols = [
    "Body_Type","Powertrain","Buying_Cost","Mileage","Fuel_Price",
    "Maintenance_Year","Insurance_Year","Tyre_Cost_Year","Battery_Cost"
]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"Missing columns in CSV: {missing}")
    st.stop()

# -------- Sidebar Inputs --------
st.sidebar.header("Inputs")
years = st.sidebar.slider("Ownership (years)", 5, 20, 20)
annual_km = st.sidebar.slider("Annual km", 5000, 30000, 12000)
body_type = st.sidebar.selectbox("Body Type", sorted(df["Body_Type"].unique()))

# -------- Filter --------
fdf = df[df["Body_Type"] == body_type].copy()
if fdf.empty:
    st.warning("No rows for selected body type")
    st.stop()

# -------- TCO Calculation --------
def tco(row):
    total_km = years * annual_km
    fuel = (total_km / row["Mileage"]) * row["Fuel_Price"]
    maint = row["Maintenance_Year"] * years
    ins = row["Insurance_Year"] * years
    tyre = row["Tyre_Cost_Year"] * years
    batt = row["Battery_Cost"]
    return row["Buying_Cost"] + fuel + maint + ins + tyre + batt

fdf["Total_Cost"] = fdf.apply(tco, axis=1)
fdf["Cost_per_km"] = fdf["Total_Cost"] / (years * annual_km)

# -------- Display --------
st.subheader("📊 Comparison")
st.dataframe(
    fdf[["Powertrain","Total_Cost","Cost_per_km"]]
    .sort_values("Total_Cost")
)

# -------- Simple Bar Chart (no matplotlib needed) --------
st.subheader("📈 Total Cost by Powertrain")
chart_df = fdf.set_index("Powertrain")[["Total_Cost"]]
st.bar_chart(chart_df)

# -------- Breakdown (selected powertrain) --------
st.subheader("🔍 Cost Breakdown")
pt = st.selectbox("Select Powertrain", fdf["Powertrain"])
row = fdf[fdf["Powertrain"] == pt].iloc[0]

total_km = years * annual_km
breakdown = pd.Series({
    "Fuel": (total_km / row["Mileage"]) * row["Fuel_Price"],
    "Maintenance": row["Maintenance_Year"] * years,
    "Insurance": row["Insurance_Year"] * years,
    "Tyres": row["Tyre_Cost_Year"] * years,
    "Battery": row["Battery_Cost"]
})

st.write("Breakdown (₹):")
st.dataframe(breakdown.rename("Cost").to_frame())

st.subheader("📊 Breakdown Chart")
st.bar_chart(breakdown)

# -------- Insight --------
best = fdf.loc[fdf["Cost_per_km"].idxmin()]
st.success(f"Most economical: {best['Powertrain']} (₹ {best['Cost_per_km']:.2f}/km)")