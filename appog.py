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

# Instructions for Excel Upload
st.write("""
### Instructions:
1. The Excel sheet must have column names in the first row.
2. The sheet to be analyzed must contain a column named "Weight (KG)".
3. The weights will be used to categorize deliveries into Type A (0-2 kg), Type B (2-10 kg), and Type C (10-200 kg).
""")

# Function to extract delivery data from the selected sheet
def extract_deliveries_from_excel(file, sheet_name):
    df = pd.read_excel(file, sheet_name=sheet_name)
    if 'Weight (KG)' not in df.columns:
        st.error("The selected sheet does not contain the required 'Weight (KG)' column.")
        return None, None, None
    
    weight = df['Weight (KG)']
    D_a = sum((weight > 0) & (weight <= 2))
    D_b = sum((weight > 2) & (weight <= 10))
    D_c = sum((weight > 10) & (weight <= 200))
    
    return D_a, D_b, D_c

# Extract deliveries from uploaded Excel file
if uploaded_file:
    excel = pd.ExcelFile(uploaded_file)
    sheet_name = st.selectbox("Select Sheet", excel.sheet_names)
    if st.button("Extract Deliveries from Excel"):
        D_a, D_b, D_c = extract_deliveries_from_excel(uploaded_file, sheet_name)
        if D_a is not None:
            st.success(f"Extracted Deliveries - Type A: {D_a}, Type B: {D_b}, Type C: {D_c}")

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

# Functions to run optimizations
def optimize_scenario_1(D_a, D_b, D_c, cost_v1, cost_v2, cost_v3, v1_capacity, v2_capacity, v3_capacity):
    lp_problem = pulp.LpProblem("Delivery_Cost_Minimization", pulp.LpMinimize)
    V1 = pulp.LpVariable('V1', lowBound=0, cat='Integer')
    V2 = pulp.LpVariable('V2', lowBound=0, cat='Integer')
    V3 = pulp.LpVariable('V3', lowBound=0, cat='Integer')

    A1 = pulp.LpVariable('A1', lowBound=0, cat='Continuous')
    B1 = pulp.LpVariable('B1', lowBound=0, cat='Continuous')
    C1 = pulp.LpVariable('C1', lowBound=0, cat='Continuous')
    A2 = pulp.LpVariable('A2', lowBound=0, cat='Continuous')
    B2 = pulp.LpVariable('B2', lowBound=0, cat='Continuous')
    A3 = pulp.LpVariable('A3', lowBound=0, cat='Continuous')

    lp_problem += cost_v1 * V1 + cost_v2 * V2 + cost_v3 * V3, "Total Cost"
    lp_problem += A1 + A2 + A3 == D_a, "Total_Deliveries_A_Constraint"
    lp_problem += B1 + B2 == D_b, "Total_Deliveries_B_Constraint"
    lp_problem += C1 == D_c, "Total_Deliveries_C_Constraint"
    lp_problem += v1_capacity * V1 >= C1 + B1 + A1, "V1_Capacity_Constraint"
    lp_problem += v2_capacity * V2 >= B2 + A2, "V2_Capacity_Constraint"
    lp_problem += v3_capacity * V3 >= A3, "V3_Capacity_Constraint"
    lp_problem += C1 == D_c, "Assign_C_To_V1"
    lp_problem += B1 <= v1_capacity * V1 - C1, "Assign_B_To_V1"
    lp_problem += B2 == D_b - B1, "Assign_Remaining_B_To_V2"
    lp_problem += A1 <= v1_capacity * V1 - C1 - B1, "Assign_A_To_V1"
    lp_problem += A2 <= v2_capacity * V2 - B2, "Assign_A_To_V2"
    lp_problem += A3 == D_a - A1 - A2, "Assign_Remaining_A_To_V3"
    lp_problem.solve()

    return {
        "Status": pulp.LpStatus[lp_problem.status],
        "V1": pulp.value(V1),
        "V2": pulp.value(V2),
        "V3": pulp.value(V3),
        "Total Cost": pulp.value(lp_problem.objective),
        "Deliveries assigned to V1": pulp.value(C1 + B1 + A1),
        "Deliveries assigned to V2": pulp.value(B2 + A2),
        "Deliveries assigned to V3": pulp.value(A3)
    }

def optimize_scenario_2(D_a, D_b, D_c, cost_v1, cost_v2, v1_capacity, v2_capacity):
    lp_problem = pulp.LpProblem("Delivery_Cost_Minimization", pulp.LpMinimize)

    V1 = pulp.LpVariable('V1', lowBound=0, cat='Integer')
    V2 = pulp.LpVariable('V2', lowBound=0, cat='Integer')

    A1 = pulp.LpVariable('A1', lowBound=0, cat='Continuous')
    B1 = pulp.LpVariable('B1', lowBound=0, cat='Continuous')
    C1 = pulp.LpVariable('C1', lowBound=0, cat='Continuous')
    A2 = pulp.LpVariable('A2', lowBound=0, cat='Continuous')
    B2 = pulp.LpVariable('B2', lowBound=0, cat='Continuous')

    lp_problem += cost_v1 * V1 + cost_v2 * V2, "Total Cost"

    lp_problem += A1 + A2 == D_a, "Total_Deliveries_A_Constraint"
    lp_problem += B1 + B2 == D_b, "Total_Deliveries_B_Constraint"
    lp_problem += C1 == D_c, "Total_Deliveries_C_Constraint"

    lp_problem += v1_capacity * V1 >= C1 + B1 + A1, "V1_Capacity_Constraint"
    lp_problem += v2_capacity * V2 >= B2 + A2, "V2_Capacity_Constraint"

    lp_problem += C1 == D_c, "Assign_C_To_V1"
    lp_problem += B1 <= v1_capacity * V1 - C1, "Assign_B_To_V1"
    lp_problem += B2 == D_b - B1, "Assign_Remaining_B_To_V2"
    lp_problem += A1 <= v1_capacity * V1 - C1 - B1, "Assign_A_To_V1"
    lp_problem += A2 == D_a - A1, "Assign_Remaining_A_To_V2"

    lp_problem.solve()

    return {
        "Status": pulp.LpStatus[lp_problem.status],
        "V1": pulp.value(V1),
        "V2": pulp.value(V2),
        "Total Cost": pulp.value(lp_problem.objective),
        "Deliveries assigned to V1": pulp.value(C1 + B1 + A1),
        "Deliveries assigned to V2": pulp.value(B2 + A2)
    }

def optimize_scenario_3(D_a, D_b, D_c, cost_v1, cost_v3, v1_capacity, v3_capacity):
    lp_problem = pulp.LpProblem("Delivery_Cost_Minimization", pulp.LpMinimize)

    V1 = pulp.LpVariable('V1', lowBound=0, cat='Integer')
    V3 = pulp.LpVariable('V3', lowBound=0, cat='Integer')

    A1 = pulp.LpVariable('A1', lowBound=0, cat='Continuous')
    B1 = pulp.LpVariable('B1', lowBound=0, cat='Continuous')
    C1 = pulp.LpVariable('C1', lowBound=0, cat='Continuous')
    A3 = pulp.LpVariable('A3', lowBound=0, cat='Continuous')

    lp_problem += cost_v1 * V1 + cost_v3 * V3, "Total Cost"

    lp_problem += A1 + A3 == D_a, "Total_Deliveries_A_Constraint"
    lp_problem += B1 == D_b, "Total_Deliveries_B_Constraint"
    lp_problem += C1 == D_c, "Total_Deliveries_C_Constraint"

    lp_problem += v1_capacity * V1 >= C1 + B1 + A1, "V1_Capacity_Constraint"
    lp_problem += v3_capacity * V3 >= A3, "V3_Capacity_Constraint"

    lp_problem += C1 == D_c, "Assign_C_To_V1"
    lp_problem += B1 <= v1_capacity * V1 - C1, "Assign_B_To_V1"
    lp_problem += A1 <= v1_capacity * V1 - C1 - B1, "Assign_A_To_V1"
    lp_problem += A3 == D_a - A1, "Assign_Remaining_A_To_V3"

    lp_problem.solve()

    return {
        "Status": pulp.LpStatus[lp_problem.status],
        "V1": pulp.value(V1),
        "V3": pulp.value(V3),
        "Total Cost": pulp.value(lp_problem.objective),
        "Deliveries assigned to V1": pulp.value(C1 + B1 + A1),
        "Deliveries assigned to V3": pulp.value(A3)
    }

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
