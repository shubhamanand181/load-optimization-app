import streamlit as st
import pandas as pd
import pulp

# Define the load optimization function
def load_optimization(D_a, D_b, D_c, W_a, W_b, W_c):
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
    V1 = pulp.LpVariable('V1', lowBound=0, cat='Integer')
    V2 = pulp.LpVariable('V2', lowBound=0, cat='Integer')
    V3 = pulp.LpVariable('V3', lowBound=0, cat='Integer')

    # Objective function
    lp_problem += cost_v1 * V1 + cost_v2 * V2 + cost_v3 * V3, "Total Cost"

    # Constraints
    lp_problem += v1_deliveries_per_day * V1 >= D_c, "V1_Delivery_Constraint"
    lp_problem += v2_deliveries_per_day * V2 >= D_b, "V2_Delivery_Constraint"
    lp_problem += v3_deliveries_per_day * V3 >= D_a, "V3_Delivery_Constraint"

    lp_problem += new_weight_capacity_v1 * V1 >= W_c, "V1_Weight_Constraint"
    lp_problem += new_weight_capacity_v2 * V2 >= W_b, "V2_Weight_Constraint"
    lp_problem += new_weight_capacity_v3 * V3 >= W_a, "V3_Weight_Constraint"

    # Maximum Distance Constraint (assumed example)
    max_distance_per_day = 200  # km (this would depend on actual distance limits per vehicle)
    lp_problem += max_distance_per_day * V1 + max_distance_per_day * V2 + max_distance_per_day * V3 <= 200 * 10, "Max_Distance_Constraint"

    # Driver Constraints
    total_drivers = 10
    lp_problem += V1 + V2 + V3 <= total_drivers, "Driver_Constraint"

    # Solve the problem
    lp_problem.solve()

    # Results
    status = pulp.LpStatus[lp_problem.status]
    V1_value = pulp.value(V1)
    V2_value = pulp.value(V2)
    V3_value = pulp.value(V3)
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

            # Display the input data
            st.subheader("Input Data")
            st.write(df)

            # Display classification results
            st.subheader("Classification Results")
            st.write(f"Type A Deliveries (0-2 kg): {D_a}, Total Weight: {W_a} kg")
            st.write(f"Type B Deliveries (2-10 kg): {D_b}, Total Weight: {W_b} kg")
            st.write(f"Type C Deliveries (>10 kg): {D_c}, Total Weight: {W_c} kg")

    except Exception as e:
        st.error(f"An error occurred: {e}")

# Manual entry option for number of deliveries
st.sidebar.header("Manual Entry")
D_a_manual = st.sidebar.number_input("Number of Type A Deliveries (0-2 kg)", min_value=0, value=0)
D_b_manual = st.sidebar.number_input("Number of Type B Deliveries (2-10 kg)", min_value=0, value=0)
D_c_manual = st.sidebar.number_input("Number of Type C Deliveries (>10 kg)", min_value=0, value=0)

# Run the load optimization model with manual input if provided
if st.sidebar.button("Optimize with Manual Input"):
    W_a_manual = D_a_manual * 1.5  # Average weight for Type A (example)
    W_b_manual = D_b_manual * 6    # Average weight for Type B (example)
    W_c_manual = D_c_manual * 15   # Average weight for Type C (example)
    
    status, V1_value, V2_value, V3_value, total_cost = load_optimization(D_a_manual, D_b_manual, D_c_manual, W_a_manual, W_b_manual, W_c_manual)
    
    # Display the results
    st.subheader("Optimization Results with Manual Input")
    st.write(f"Status: {status}")
    st.write(f"V1: {V1_value}")
    st.write(f"V2: {V2_value}")
    st.write(f"V3: {V3_value}")
    st.write(f"Total Cost: {total_cost}")
