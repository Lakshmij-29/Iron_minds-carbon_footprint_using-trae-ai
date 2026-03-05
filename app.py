import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="EcoTrack Pro", layout="wide")


st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #e0f7fa, #e8f5e9);
        font-family: 'Segoe UI', sans-serif;
    }

    h1 {
        color: #1b5e20;
        text-align: center;
    }

    h2, h3 {
        color: #2e7d32;
    }

    .stMetric {
        background-color: #ffffffaa;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 2px 2px 10px #cccccc;
    }

    .stButton > button {
        background-color: #43a047;
        color: white;
        border-radius: 8px;
        height: 3em;
        width: 100%;
    }

    .stButton > button:hover {
        background-color: #1b5e20;
        color: white;
    }

    section[data-testid="stSidebar"] {
        background-color: #c8e6c9;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌍 EcoTrack Pro - Smart Carbon Intelligence Dashboard")

@st.cache_data
def load_data():
    return pd.read_csv("dataset.csv")

try:
    data = load_data()
except Exception as e:
    st.error(f"Dataset Load Error: {e}")
    st.stop()

st.sidebar.header("🔍 City Selection")
city1 = st.sidebar.selectbox("Select Primary City", sorted(data["City"].unique()))
city2 = st.sidebar.selectbox("Compare With (Optional)", ["None"] + sorted(data["City"].unique()))


def calculate_emissions(row):
    electricity = row["Avg_Electricity_kWh"] * 0.82
    transport = row["Avg_Transport_Fuel_L"] * 2.31
    cooking = row["Avg_Cooking_LPG_kg"] * 3
    waste = row["Avg_Waste_kg"] * 0.57
    air = row["Avg_Air_Travel_km"] * 0.115
    total = electricity + transport + cooking + waste + air
    
    return {
        "Electricity": electricity,
        "Transport": transport,
        "Cooking LPG": cooking,
        "Waste": waste,
        "Air Travel": air,
        "Total": total
    }

city_data = data[data["City"] == city1].iloc[0]
emissions = calculate_emissions(city_data)


st.subheader(f"📊 Carbon Breakdown for {city1}")

cols = st.columns(5)
for col, (label, value) in zip(cols, list(emissions.items())[:-1]):
    col.metric(label, f"{value:.2f} kg CO₂e")

st.markdown("---")
st.metric("🌡 Total Emission", f"{emissions['Total']:.2f} kg CO₂e")


st.subheader("📈 Emission Contribution")
fig = px.pie(
    names=list(emissions.keys())[:-1],
    values=list(emissions.values())[:-1],
    hole=0.4,
)
fig.update_traces(textinfo='percent+label')
st.plotly_chart(fig, use_container_width=True)


st.subheader("🚦 Emission Level Indicator")

gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=emissions["Total"],
    title={'text': "Carbon Emission Level (kg CO₂e)"},
    gauge={
        'axis': {'range': [0, 600]},
        'bar': {'color': "#2e7d32"},
        'steps': [
            {'range': [0, 300], 'color': "#a5d6a7"},
            {'range': [300, 450], 'color': "#ffe082"},
            {'range': [450, 600], 'color': "#ef9a9a"}
        ],
    }
))
st.plotly_chart(gauge, use_container_width=True)


st.subheader("🌱 Smart Recommendations")

if emissions["Total"] < 300:
    st.success("Excellent sustainability performance! 🌿")
elif emissions["Total"] < 450:
    st.warning("Moderate emissions. Improve transport & electricity usage.")
else:
    st.error("High carbon footprint! Encourage renewables & public transport.")

# ---------------- CITY COMPARISON ---------------- #
if city2 != "None":
    city2_data = data[data["City"] == city2].iloc[0]
    emissions2 = calculate_emissions(city2_data)

    compare_df = pd.DataFrame({
        city1: list(emissions.values())[:-1],
        city2: list(emissions2.values())[:-1]
    }, index=list(emissions.keys())[:-1])

    st.subheader("🏙 City Comparison")
    st.bar_chart(compare_df)


st.subheader("🧮 Personal Carbon Calculator")

col1, col2, col3 = st.columns(3)

with col1:
    elec = st.number_input("Monthly Electricity (kWh)", value=100)
    fuel = st.number_input("Monthly Fuel (Litres)", value=20)

with col2:
    lpg = st.number_input("Monthly LPG (kg)", value=10)
    waste_input = st.number_input("Monthly Waste (kg)", value=15)

with col3:
    air_input = st.number_input("Air Travel (km/year)", value=1000)

if st.button("Calculate My Footprint"):
    total_personal = (elec*0.82 + fuel*2.31 + lpg*3 + waste_input*0.57 + air_input*0.115)
    st.success(f"🌍 Your Estimated Annual Carbon Footprint: {total_personal:.2f} kg CO₂e")

st.subheader("📥 Download City Dataset")

st.download_button(
    "Download Dataset",
    data.to_csv(index=False),
    file_name="carbon_data.csv",
    mime="text/csv"
)
