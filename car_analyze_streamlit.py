import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import pandas as pd

# --- Utility Functions ---
# Helper function to format numbers with 'k' for thousands
def format_k_display(val):
    val = int(val)
    if val >= 1000:
        return f"{val/1000:.0f}k kr"
    return f"{val} kr"

# Set page configuration
st.set_page_config(
    page_title="Car Cost Comparison Tool",
    page_icon="🚗",
    layout="wide"
)

# App title and description
st.title("Tesla Model Y vs Jaguar I-Pace Cost Comparison")
st.markdown("""
This tool helps you analyze the 3-year cost difference between a Tesla Model Y and a Jaguar I-Pace
under various depreciation and repair cost scenarios. The heatmap shows cost differences across scenarios.
Click on any cell in the heatmap to see a detailed breakdown.
""")

# Sidebar for adjustable parameters
st.sidebar.header("Adjust Parameters")

# Granularity slider
granularity = st.sidebar.slider(
    "Grid size (granularity)",
    min_value=3,
    max_value=9,
    value=6,
    step=1,
    help="Higher values create a more detailed grid with more scenarios"
)

# Helper function for 'k' formatting
def format_k_value(val):
    if val >= 10000:
        return f"{int(val/1000)}k kr"
    return f"{int(val)} kr"

# Cost range sliders
jag_min, jag_max = st.sidebar.slider(
    "Jaguar Annual Repair Cost Range (kr)",
    min_value=10_000,
    max_value=100_000,
    value=(20_000, 80_000),
    step=5_000,
    format=None,
    help="Range of annual repair costs to consider"
)

tesla_min, tesla_max = st.sidebar.slider(
    "Tesla 3-Year Depreciation Range (kr)",
    min_value=50_000,
    max_value=300_000,
    value=(80_000, 220_000),
    step=10_000,
    format=None,
    help="Range of 3-year depreciation to consider"
)

# Adjustable fixed costs
st.sidebar.header("Fixed Costs")

# Function to create number input with k-formatted display
def k_number_input(label, default_value, step, key=None):
    value = st.number_input(label, value=default_value, step=step, format=None, key=key)
    return value

with st.sidebar.expander("Jaguar Fixed Costs", expanded=False):
    jag_purchase = k_number_input("Purchase Price", 700_000, 50000, key="jag_purchase")
    jag_depreciation = k_number_input("Depreciation", 70_000, 5000, key="jag_dep")
    jag_interest = k_number_input("Interest", 33_000, 1000, key="jag_int")
    jag_insurance = k_number_input("Insurance for 3 years", 120_000, 1000, key="jag_ins")
    jag_charging = k_number_input("Charging", 8_000, 1000, key="jag_chg")

with st.sidebar.expander("Tesla Fixed Costs", expanded=False):
    tesla_purchase = k_number_input("Purchase Price", 700_000, 50000, key="tesla_purchase")
    tesla_insurance = k_number_input("Insurance for 3 years", 60_000, 1000, key="tesla_ins")
    tesla_charging = k_number_input("Charging", 6_000, 1000, key="tesla_chg")
    tesla_refinancing = k_number_input("Refinancing Fee", 2_150, 100, key="tesla_ref")
    tesla_repairs = k_number_input("Repairs for 3 years", 15_000, 1000, key="tesla_rep")

# Calculate fixed costs (without the purchase price for the cost comparison)
jaguar_fixed = jag_depreciation + jag_interest + jag_insurance + jag_charging
tesla_fixed = tesla_insurance + tesla_charging + tesla_refinancing + tesla_repairs

# Generate ranges based on granularity
jag_repairs = np.linspace(jag_min, jag_max, granularity)
tesla_depreciations = np.linspace(tesla_min, tesla_max, granularity)

# Calculate matrix and round to nearest 10
matrix = np.zeros((granularity, granularity))
for i, tesla_dep in enumerate(tesla_depreciations):
    tesla_total = tesla_fixed + tesla_dep
    for j, jag_rep in enumerate(jag_repairs):
        jaguar_total = jaguar_fixed + 3 * jag_rep
        matrix[i, j] = round(jaguar_total - tesla_total, -1)  # Round to nearest 10

# --- Matrix Visualization (Full Width) ---
st.subheader("Cost Difference Matrix")
st.write("Positive values (red): Tesla is cheaper | Negative values (green): Jaguar is cheaper")

# Format function for annotations in the heatmap - convert to string first
def fmt_func(val):
    val = int(val)
    if abs(val) >= 1000:
        return f"{val/1000:.0f}k"
    return f"{val}"

# Create DataFrame for heatmap (for display purposes only)
df_heatmap = pd.DataFrame(
    matrix,
    index=[format_k_display(val) for val in tesla_depreciations],
    columns=[format_k_display(val).replace(" kr", "") + "/yr" for val in jag_repairs]
)

# Create annotation array
annotations = np.zeros_like(matrix).astype(str)
for i in range(matrix.shape[0]):
    for j in range(matrix.shape[1]):
        annotations[i, j] = fmt_func(matrix[i, j])

# Create heatmap
fig, ax = plt.subplots(figsize=(12, 8))

sns.heatmap(
    df_heatmap, annot=annotations, fmt="", cmap='RdYlGn_r', center=0,
    xticklabels=[f"{int(j/1000)}k" for j in jag_repairs],
    yticklabels=[f"{int(t/1000)}k" for t in tesla_depreciations],
    cbar_kws={'label': 'Difference (Jaguar - Tesla, kr)'},
    linewidths=0.5, linecolor='gray', ax=ax
)

ax.set_xlabel("Jaguar Annual Repair Costs (kr/year)")
ax.set_ylabel("Tesla Depreciation over 3 years (kr)")
ax.set_title("Scenario Matrix: Jaguar vs Tesla Cost Difference")

# Show the plot (full width)
st.pyplot(fig)

# --- Scenario Selection (Full Width) ---
st.subheader("Select a scenario to analyze")

# Using number inputs for free value selection with k formatting
col_a, col_b = st.columns(2)

with col_a:
    selected_tesla_dep = st.number_input(
        "Tesla Depreciation",
        min_value=int(tesla_min),
        max_value=int(tesla_max),
        value=int(tesla_depreciations[len(tesla_depreciations)//2]),
        step=10000,
        format=None
    )

with col_b:
    selected_jaguar_rep = st.number_input(
        "Jaguar Annual Repairs",
        min_value=int(jag_min),
        max_value=int(jag_max),
        value=int(jag_repairs[len(jag_repairs)//2]),
        step=5000,
        format=None
    )

# --- Detailed Analysis ---
# Calculate totals with the selected parameters
tesla_total = tesla_fixed + selected_tesla_dep
jaguar_total = jaguar_fixed + (3 * selected_jaguar_rep)
difference = jaguar_total - tesla_total

# Helper function to format amounts with 'k' for thousands
def format_amount(val):
    val = round(val, -1)  # Round to nearest 10
    if val >= 1000:
        return f"{val/1000:.0f}k"
    return f"{val}"

# Create two columns for the main detailed analysis
col1, col2 = st.columns([1, 1])

# Left column for cost difference and bar chart
with col1:
    st.subheader("Cost Comparison")
    
    # Display the winner
    winner = "Tesla Model Y is cheaper" if difference > 0 else "Jaguar I-Pace is cheaper"
    diff_amount = abs(int(round(difference, -1)))  # Round to nearest 10
    
    # Format the difference with 'k' for thousands
    diff_display = f"{diff_amount/1000:.0f}k kr" if diff_amount >= 1000 else f"{diff_amount} kr"
    
    st.metric(
        "Cost Difference", 
        diff_display, 
        delta=winner,
        delta_color="normal"
    )
    
    # Create comparison bar chart
    st.subheader("Total 3-Year Cost Comparison")
    
    # Create a DataFrame for the bar chart
    df_costs = pd.DataFrame({
        'Vehicle': ['Tesla Model Y', 'Jaguar I-Pace'],
        'Total Cost (kr)': [tesla_total, jaguar_total]
    })
    
    # Plot bar chart
    bar_colors = ['green', '#ff6666']
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(
        df_costs['Vehicle'],
        df_costs['Total Cost (kr)'],
        color=bar_colors
    )
    
    # Add value labels with 'k' formatting
    for bar in bars:
        height = round(bar.get_height(), -1)  # Round to nearest 10
        height_display = f"{height/1000:.0f}k kr"
        ax.text(
            bar.get_x() + bar.get_width()/2.,
            height + 5000,
            height_display,
            ha='center',
            va='bottom'
        )
    
    ax.set_ylabel('Total 3-Year Cost (kr)')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    st.pyplot(fig)

# Right column for cost breakdown tables
with col2:
    # Show cost breakdowns in tables
    st.subheader("Cost Breakdown")
    
    # Create two columns for Tesla and Jaguar breakdowns
    cost_col1, cost_col2 = st.columns(2)
    
    with cost_col1:
        st.write("**Tesla Model Y Costs**")
        
        tesla_breakdown = {
            'Cost Category': ['Purchase Price', 'Depreciation', 'Insurance', 'Charging', 'Refinancing Fee', 'Repairs', 'Total'],
            'Amount (kr)': [
                format_amount(tesla_purchase),
                format_amount(selected_tesla_dep), 
                format_amount(tesla_insurance), 
                format_amount(tesla_charging), 
                format_amount(tesla_refinancing), 
                format_amount(tesla_repairs),
                format_amount(tesla_total)
            ],
            'Percentage': [
                "N/A",
                f"{selected_tesla_dep/tesla_total*100:.1f}%",
                f"{tesla_insurance/tesla_total*100:.1f}%", 
                f"{tesla_charging/tesla_total*100:.1f}%", 
                f"{tesla_refinancing/tesla_total*100:.1f}%", 
                f"{tesla_repairs/tesla_total*100:.1f}%",
                "100%"
            ]
        }
        
        st.table(pd.DataFrame(tesla_breakdown))
    
    with cost_col2:
        st.write("**Jaguar I-Pace Costs**")
        
        jaguar_repairs_3yr = 3 * selected_jaguar_rep
        
        jaguar_breakdown = {
            'Cost Category': ['Purchase Price', 'Depreciation', 'Interest', 'Insurance', 'Charging', 'Repairs (3 yrs)', 'Total'],
            'Amount (kr)': [
                format_amount(jag_purchase),
                format_amount(jag_depreciation), 
                format_amount(jag_interest), 
                format_amount(jag_insurance), 
                format_amount(jag_charging), 
                format_amount(jaguar_repairs_3yr),
                format_amount(jaguar_total)
            ],
            'Percentage': [
                "N/A",
                f"{jag_depreciation/jaguar_total*100:.1f}%",
                f"{jag_interest/jaguar_total*100:.1f}%", 
                f"{jag_insurance/jaguar_total*100:.1f}%", 
                f"{jag_charging/jaguar_total*100:.1f}%", 
                f"{jaguar_repairs_3yr/jaguar_total*100:.1f}%",
                "100%"
            ]
        }
        
        st.table(pd.DataFrame(jaguar_breakdown))
    
    # Pie charts
    st.subheader("Cost Distribution")
    pie_col1, pie_col2 = st.columns(2)
    
    with pie_col1:
        st.write("**Tesla Model Y**")
        
        # Create pie chart data
        tesla_pie_data = {
            'Category': ['Purchase Price', 'Depreciation', 'Insurance', 'Charging', 'Refinancing Fee', 'Repairs'],
            'Cost': [tesla_purchase, selected_tesla_dep, tesla_insurance, tesla_charging, tesla_refinancing, tesla_repairs]
        }
        
        # Calculate total for display (excluding Purchase Price)
        tesla_display_total = selected_tesla_dep + tesla_insurance + tesla_charging + tesla_refinancing + tesla_repairs
        
        fig, ax = plt.subplots(figsize=(8, 8))
        # Only show costs related to ownership, not the purchase price
        ax.pie(
            tesla_pie_data['Cost'][1:],  # Skip Purchase Price
            labels=tesla_pie_data['Category'][1:],  # Skip Purchase Price
            autopct='%1.1f%%',
            startangle=90,
            colors=plt.cm.Greens(np.linspace(0.2, 0.7, len(tesla_pie_data['Category'])-1))
        )
        total_display = f"{round(tesla_display_total/1000, 0):.0f}k kr"
        ax.set_title(f'Tesla Ownership Cost Distribution\nTotal: {total_display}')
        
        st.pyplot(fig)
    
    with pie_col2:
        st.write("**Jaguar I-Pace**")
        
        # Create pie chart data
        jaguar_repairs_3yr = 3 * selected_jaguar_rep
        jaguar_pie_data = {
            'Category': ['Purchase Price', 'Depreciation', 'Interest', 'Insurance', 'Charging', 'Repairs (3 yrs)'],
            'Cost': [jag_purchase, jag_depreciation, jag_interest, jag_insurance, jag_charging, jaguar_repairs_3yr]
        }
        
        # Calculate total for display (excluding Purchase Price)
        jaguar_display_total = jag_depreciation + jag_interest + jag_insurance + jag_charging + jaguar_repairs_3yr
        
        fig, ax = plt.subplots(figsize=(8, 8))
        # Only show costs related to ownership, not the purchase price
        ax.pie(
            jaguar_pie_data['Cost'][1:],  # Skip Purchase Price
            labels=jaguar_pie_data['Category'][1:],  # Skip Purchase Price
            autopct='%1.1f%%',
            startangle=90,
            colors=plt.cm.Reds(np.linspace(0.2, 0.7, len(jaguar_pie_data['Category'])-1))
        )
        total_display = f"{round(jaguar_display_total/1000, 0):.0f}k kr"
        ax.set_title(f'Jaguar Ownership Cost Distribution\nTotal: {total_display}')
        
        st.pyplot(fig)

# Footer
st.markdown("---")
st.caption("Car Cost Comparison Tool - Made with Streamlit") 