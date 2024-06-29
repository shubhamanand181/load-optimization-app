import streamlit as st
import pulp

# Function to run optimization for scenario 1 (V1, V2, V3)
def optimize_scenario_1(D_a, D_b, D_c):
    v1_deliveries_per_day = 64
    v2_deliveries_per_day = 66
    v3_deliveries_per_day = 72

    cost_v1 = 62.8156
    cost_v2 = 33
    cost_v3 = 29.0536

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

    lp_problem += 64 * V1 >= C1 + B1 + A1, "V1_Capacity_Constraint"
    lp_problem += 66 * V2 >= B2 + A2, "V2_Capacity_Constraint"
    lp_problem += 72 * V3 >= A3, "V3_Capacity_Constraint"

    lp_problem += C1 == D_c, "Assign_C_To_V1"
    lp_problem += B1 <= 64 * V1 - C1, "Assign_B_To_V1"
    lp_problem += B2 == D_b - B1, "Assign_Remaining_B_To_V2"
    lp_problem += A1 <= 64 * V1 - C1 - B1, "Assign_A_To_V1"
    lp_problem += A2 <= 66 * V2 - B2, "Assign_A_To_V2"
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

# Function to run optimization for scenario 2 (V1, V2)
def optimize_scenario_2(D_a, D_b, D_c):
    v1_deliveries_per_day = 64
    v2_deliveries_per_day = 66

    cost_v1 = 62.8156
    cost_v2 = 33

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

    lp_problem += 64 * V1 >= C1 + B1 + A1, "V1_Capacity_Constraint"
    lp_problem += 66 * V2 >= B2 + A2, "V2_Capacity_Constraint"

    lp_problem += C1 == D_c, "Assign_C_To_V1"
    lp_problem += B1 <= 64 * V1 - C1, "Assign_B_To_V1"
    lp_problem += B2 == D_b - B1, "Assign_Remaining_B_To_V2"
    lp_problem += A1 <= 64 * V1 - C1 - B1, "Assign_A_To_V1"
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

# Function to run optimization for scenario 3 (V1, V3)
def optimize_scenario_3(D_a, D_b, D_c):
    v1_deliveries_per_day = 64
    v3_deliveries_per_day = 72

    cost_v1 = 62.8156
    cost_v3 = 29.0536

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

    lp_problem += 64 * V1 >= C1 + B1 + A1, "V1_Capacity_Constraint"
    lp_problem += 72 * V3 >= A3, "V3_Capacity_Constraint"

    lp_problem += C1 == D_c, "Assign_C_To_V1"
    lp_problem += B1 <= 64 * V1 - C1, "Assign_B_To_V1"
    lp_problem += A1 <= 64 * V1 - C1 - B1, "Assign_A_To_V1"
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

# Streamlit app
st.title("Delivery Cost Optimization")

# User input for number of deliveries
D_a = st.number_input("Number of Type A deliveries (0-2 kg)", min_value=0, value=80)
D_b = st.number_input("Number of Type B deliveries (2-10 kg)", min_value=0, value=100)
D_c = st.number_input("Number of Type C deliveries (>10 kg)", min_value=0, value=10)

# User selection for scenario
scenario = st.selectbox("Select Scenario", ["Scenario 1: V1, V2, V3", "Scenario 2: V1, V2", "Scenario 3: V1, V3"])

if st.button("Optimize"):
    if scenario == "Scenario 1: V1, V2, V3":
        result = optimize_scenario_1(D_a, D_b, D_c)
    elif scenario == "Scenario 2: V1, V2":
        result = optimize_scenario_2(D_a, D_b, D_c)
    elif scenario == "Scenario 3: V1, V3":
        result = optimize_scenario_3(D_a, D_b, D_c)
    
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
