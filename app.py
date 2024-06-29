import streamlit as st
import pandas as pd
import pulp

# Title
st.title("Delivery Cost Optimization")

# Manual Entry of Deliveries
st.write("### Manual Entry of Deliveries")
D_a = st.number_input("Number of Type A deliveries (0-2 kg)", min_value=0, value=80)
D_b = st.number_input("Number of Type B deliveries (2-10 kg)", min_value=0, value=100)
D_c = st.number_input("Number of Type C deliveries (10-200 kg)", min_value=0, value=10)

# File uploader for Excel file
st.subheader("Upload Excel File")
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file:
    excel = pd.ExcelFile(uploaded_file)
    sheet_name = st.selectbox("Select Sheet", excel.sheet_names)
    if st.button("Extract Deliveries from Excel"):
        D_a, D_b, D_c = extract_deliveries_from_excel(uploaded_file, sheet_name)
        if D_a is not None:
            st.success(f"Extracted Deliveries - Type A: {D_a}, Type B: {D_b}, Type C: {D_c}")

# Instructions for Excel Upload
st.write("""
### Instructions:
1. The Excel sheet must have column names in the first row.
2. The sheet to be analyzed must contain a column named "Weight (KG)".
3. The weights will be used to categorize deliveries into Type A (0-2 kg), Type B (2-10 kg), and Type C (10-200 kg).
""")

# Display vehicle descriptions
vehicle_descriptions = {
    "V1": "A versatile vehicle capable of handling all types of deliveries with a higher cost and larger capacity (a four wheeler mini-truck).",
    "V2": "A mid-range vehicle that can handle types A and B deliveries with moderate cost and capacity (a three wheeler EV).",
    "V3": "A cost-effective vehicle that handles only type A deliveries with the smallest capacity (a two wheeler EV)."
}

st.subheader("Vehicle Information")
st.text("V1: " + vehicle_descriptions["V1"])
st.text("V2: " + vehicle_descriptions["V2"])
st.text("V3: " + vehicle_descriptions["V3"])

# User input for vehicle capacities
st.subheader("Vehicle Capacities (deliveries per day)")
v1_capacity = st.number_input("Capacity of V1", min_value=1, value=64)
v2_capacity = st.number_input("Capacity of V2", min_value=1, value=66)
v3_capacity = st.number_input("Capacity of V3", min_value=1, value=72)

# User input for vehicle costs
st.subheader("Vehicle Costs (USD per day)")
cost_v1 = st.number_input("Cost of V1", min_value=0.0, value=62.8156)
cost_v2 = st.number_input("Cost of V2", min_value=0.0, value=33.0)
cost_v3 = st.number_input("Cost of V3", min_value=0.0, value=29.0536)

# User selection for scenario
scenario = st.selectbox("Select Scenario", ["Scenario 1: V1, V2, V3", "Scenario 2: V1, V2", "Scenario 3: V1, V3"])

if st.button("Optimize"):
    if scenario == "Scenario 1: V1, V2, V3":
        result = optimize_scenario_1(D_a, D_b, D_c, cost_v1, cost_v2, cost_v3, v1_capacity, v2_capacity, v3_capacity)
    elif scenario == "Scenario 2: V1, V2":
        result = optimize_scenario_2(D_a, D_b, D_c, cost_v1, cost_v2, v1_capacity, v2_capacity)
    elif scenario == "Scenario 3: V1, V3":
        result = optimize_scenario_3(D_a, D_b, D_c, cost_v1, cost_v3, v1_capacity, v3_capacity)
    
    st.write("Optimization Results:")
    st.write(f"Status: {result['Status']}")
    st.write(f"V1: {result['V1']}")
    if "V2" in result:
        st.write(f"V2: {result['V2']}")
    if "V3" in result:
        st.write(f"V3: {result['V3']}")
    st.write(f"Total Cost: {result['Total Cost']}")
    st.write(f"Deliveries assigned to V1: {result['Deliveries assigned to V1']}")
    if "Deliveries assigned to V2" in result:
        st.write(f"Deliveries assigned to V2: {result['Deliveries assigned to V2']}")
    if "Deliveries assigned to V3" in result:
        st.write(f"Deliveries assigned to V3: {result['Deliveries assigned to V3']}")
