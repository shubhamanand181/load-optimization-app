import streamlit as st
import pandas as pd
import pulp

# Define the load optimization function
def load_optimization(D_a, D_b, D_c, W_a, W_b, W_c, use_v1=True, use_v2=True, use_v3=True):
    # New weight capacities
    new_weight_capacity_v1 = 1000  # kg per day for v1
    new_weight_capacity_v2 = 500   # kg per day for v2
    new_weight_capacity_v3 = 60    # kg per day for v3

    # New delivery capacities based on time constraints
    v1_deliveries_per_day = 64
    v2_deliveries_per_day = 66
    v3_deliveries_per_day = 72

    # New costs with incentive
    cost_v1 = 62.8156
    cost_v2 = 33
    cost_v3 = 29.0536

    # Create a linear programming problem
    lp_problem = pulp.LpProblem("Delivery_Cost_Minimization", pulp.LpMinimize)

    # Define decision variables
    V1 = pulp.LpVariable('V1', lowBound=0, cat='Integer') if use_v1 else 0
    V2 = pulp.LpVariable('V2', lowBound=0, cat='Integer') if use_v2 else 0
    V3 = pulp.LpVariable('V3', lowBound=0, cat='Integer') if use_v3 else 0

    # Objective function
    lp_problem += cost_v1 * V1 + cost_v2 * V2 + cost_v3 * V3, "Total Cost"

    # Delivery constraints
    if use_v1:
        lp_problem += v1_deliveries_per_day * V1 >= D_c, "V1_Delivery_Constraint"
        lp_problem += new_weight_capacity_v1 * V1 >= W_c, "V1_Weight_Constraint"
    if use_v2:
        lp_problem += v2_deliveries_per_day * V2 >= D_b, "V2_Delivery_Constraint"
        lp_problem += new_weight_capacity_v2 * V2 >= W_b, "V2_Weight_Constraint"
    if use_v3:
        lp_problem += v3_deliveries_per_day * V3 >= D_a, "V3_Delivery_Constraint"
        lp_problem += new_weight_capacity_v3 * V3 >= W_a, "V3_Weight_Constraint"

    # Simplified underutilization constraints
    if use_v1:
        U1 = pulp.LpVariable('U1', lowBound=0, upBound=1, cat='Binary')
        lp_problem += V1 <= 1000 * (1 - U1), "V1_Underutilization_Constraint"
    if use_v2:
        U2 = pulp.LpVariable('U2', lowBound=0, upBound=1, cat='Binary')
        lp_problem += V2 <= 1000 * (1 - U2), "V2_Underutilization_Constraint"
    if use_v3:
        U3 = pulp.LpVariable('U3', lowBound=0, upBound=1, cat='Binary')
        lp_problem += V3 <= 1000 * (1 - U3), "V3_Underutilization_Constraint"

    if use_v1 and use_v2 and use_v3:
        lp_problem += U1 + U2 + U3 <= 1, "Single_Underutilized_Vehicle_Constraint"
    elif use_v1 and use_v2:
        lp_problem += U1 + U2 <= 1, "Single_Underutilized_Vehicle_Constraint"
    elif use_v1 and use_v3:
        lp_problem += U1 + U3 <= 1, "Single_Underutilized_Vehicle_Constraint"

    # Solve the problem
    lp_problem.solve()

    # Results
    status = pulp.LpStatus[lp_problem.status]
    V1_value = pulp.value(V1) if use_v1 else 0
    V2_value = pulp.value(V2) if use_v2 else 0
    V3_value = pulp.value(V3) if use_v3 else 0
    total_cost = pulp.value(lp_problem.objective)

    return status, V1_value, V2_value, V3_value, total_cost

# Streamlit app
st.title("Load Optimization Model")

# Descriptive message for delivery types
st.markdown("""
### Delivery Type Descriptions:
- **Type A Deliveries**: 0-2 kg
- **Type B Deliveries**: 2-10 kg
- **Type C Deliveries**: More than 10 kg
""")

# File uploader for Excel file
uploaded_file = st.file_uploader("Upload your input data (Excel)", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Read the uploaded Excel file and get the sheet names
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_names = excel_file.sheet_names
        
        # Let the user select a sheet
        sheet_name = st.selectbox("Select the sheet to use", sheet_names)
        
        # Read the selected sheet
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
        st.write("Columns in the selected sheet:", df.columns.tolist())  # Debug output

        if 'Weight (KG)' not in df.columns:
            st.error("The selected sheet does not contain a 'Weight (KG)' column. Please select a valid sheet.")
        else:
            # Extract and classify weights
            weights = df['Weight (KG)']
            D_a = len(weights[(weights > 0) & (weights <= 2)])
            D_b = len(weights[(weights > 2) & (weights <= 10)])
            D_c = len(weights[weights > 10])

            W_a = weights[(weights > 0) & (weights <= 2)].sum()
            W_b = weights[(weights > 2) & (weights <= 10)].sum()
            W_c = weights[weights > 10].sum()

            st.write(f"Debug Weights: A: {W_a}, B: {W_b}, C: {W_c}")

            # Display the input data
            st.subheader("Input Data")
            st.write(df)

            # Display classification results
            st.subheader("Classification Results")
            st.write(f"Type A Deliveries (0-2 kg): {D_a}, Total Weight: {W_a} kg")
            st.write(f"Type B Deliveries (2-10 kg): {D_b}, Total Weight: {W_b} kg")
            st.write(f"Type C Deliveries (>10 kg): {D_c}, Total Weight: {W_c} kg")

            # Run optimization for all three cases
            st.subheader("Optimization Results")

            # Case 1: All vehicles
            status, V1_value, V2_value, V3_value, total_cost = load_optimization(D_a, D_b, D_c, W_a, W_b, W_c, use_v1=True, use_v2=True, use_v3=True)
            st.write(f"**All Vehicles (V1, V2, V3)** - Status: {status}, V1: {V1_value}, V2: {V2_value}, V3: {V3_value}, Total Cost: {total_cost}")

            # Case 2: Only V1 and V2
            status, V1_value, V2_value, V3_value, total_cost = load_optimization(D_a, D_b, D_c, W_a, W_b, W_c, use_v1=True, use_v2=True, use_v3=False)
            st.write(f"**Only V1 and V2 (V3=0)** - Status: {status}, V1: {V1_value}, V2: {V2_value}, V3: {V3_value}, Total Cost: {total_cost}")

            # Case 3: Only V1 and V3
            status, V1_value, V2_value, V3_value, total_cost = load_optimization(D_a, D_b, D_c, W_a, W_b, W_c, use_v1=True, use_v2=False, use_v3=True)
            st.write(f"**Only V1 and V3 (V2=0)** - Status: {status}, V1: {V1_value}, V2: {V2_value}, V3: {V3_value}, Total Cost: {total_cost}")

    except Exception as e:
        st.error(f"An error occurred: {e}")

# Descriptive message for vehicle types
st.markdown("""
### Vehicle Type Descriptions:
- **V1**: Capacity 1000 kg, 64 deliveries per day, Cost $62.82
- **V2**: Capacity 500 kg, 66 deliveries per day, Cost $33.00
- **V3**: Capacity 60 kg, 72 deliveries per day, Cost $29.05
""")
