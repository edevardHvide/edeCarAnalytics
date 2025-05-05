import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import pandas as pd

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

# Cost range sliders
jag_min, jag_max = st.sidebar.slider(
    "Jaguar Annual Repair Cost Range (kr)",
    min_value=10_000,
    max_value=100_000,
    value=(20_000, 80_000),
    step=5_000,
    format="%d kr"
)

tesla_min, tesla_max = st.sidebar.slider(
    "Tesla 3-Year Depreciation Range (kr)",
    min_value=50_000,
    max_value=300_000,
    value=(80_000, 220_000),
    step=10_000,
    format="%d kr"
)

# Adjustable fixed costs
st.sidebar.header("Fixed Costs")
with st.sidebar.expander("Jaguar Fixed Costs", expanded=False):
    jag_depreciation = st.number_input("Depreciation (kr)", value=100_000, step=5000, format="%d")
    jag_interest = st.number_input("Interest (kr)", value=33_000, step=1000, format="%d")
    jag_insurance = st.number_input("Insurance for 3 years (kr)", value=36_000, step=1000, format="%d")
    jag_charging = st.number_input("Charging (kr)", value=8_000, step=1000, format="%d")

with st.sidebar.expander("Tesla Fixed Costs", expanded=False):
    tesla_insurance = st.number_input("Insurance for 3 years (kr)", value=30_000, step=1000, format="%d")
    tesla_charging = st.number_input("Charging (kr)", value=6_000, step=1000, format="%d")
    tesla_refinancing = st.number_input("Refinancing Fee (kr)", value=2_150, step=100, format="%d")
    tesla_repairs = st.number_input("Repairs for 3 years (kr)", value=15_000, step=1000, format="%d")

# Calculate fixed costs
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

# Create two columns for the main layout
col1, col2 = st.columns([2, 3])

# Create the heatmap in the first column
with col1:
    st.subheader("Cost Difference Matrix")
    st.write("Positive values (red): Tesla is cheaper | Negative values (green): Jaguar is cheaper")
    
    # Helper function to format numbers with 'k' for thousands
    def format_k(val):
        val = int(val)
        if val >= 1000:
            return f"{val/1000:.0f}k kr"
        return f"{val} kr"
    
    # Create DataFrame for heatmap
    df_heatmap = pd.DataFrame(
        matrix,
        index=[format_k(val) for val in tesla_depreciations],
        columns=[format_k(val) + "/yr" for val in jag_repairs]
    )
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Format function for annotations in the heatmap
    def fmt(x):
        x = int(x)
        if x >= 1000 or x <= -1000:
            return f"{x/1000:.0f}k"
        return f"{x}"
    
    sns.heatmap(
        matrix, annot=True, fmt=fmt, cmap='RdYlGn_r', center=0,
        xticklabels=[f"{int(j/1000)}k" for j in jag_repairs],
        yticklabels=[f"{int(t/1000)}k" for t in tesla_depreciations],
        cbar_kws={'label': 'Difference (Jaguar - Tesla, kr)'},
        linewidths=0.5, linecolor='gray', ax=ax
    )
    
    ax.set_xlabel("Jaguar Annual Repair Costs (kr/year)")
    ax.set_ylabel("Tesla Depreciation over 3 years (kr)")
    ax.set_title("Scenario Matrix: Jaguar vs Tesla Cost Difference")
    
    # Show the plot
    st.pyplot(fig)
    
    # Create a selection mechanism
    st.subheader("Select a scenario to analyze")
    
    # Using select boxes for Tesla and Jaguar selection
    selected_tesla_index = st.selectbox(
        "Tesla Depreciation",
        options=range(granularity),
        format_func=lambda i: format_k(tesla_depreciations[i])
    )
    
    selected_jaguar_index = st.selectbox(
        "Jaguar Annual Repairs",
        options=range(granularity),
        format_func=lambda i: format_k(jag_repairs[i]) + "/yr"
    )
    
    # Get the selected values
    selected_tesla_dep = tesla_depreciations[selected_tesla_index]
    selected_jaguar_rep = jag_repairs[selected_jaguar_index]

# Display the detailed analysis in the second column
with col2:
    st.subheader("Detailed Cost Analysis")
    
    # Calculate totals with the selected parameters
    tesla_total = tesla_fixed + selected_tesla_dep
    jaguar_total = jaguar_fixed + (3 * selected_jaguar_rep)
    difference = jaguar_total - tesla_total
    
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
    
    # Show cost breakdowns in tables
    st.subheader("Cost Breakdown")
    
    # Create two columns for Tesla and Jaguar breakdowns
    cost_col1, cost_col2 = st.columns(2)
    
    # Helper function to format amounts with 'k' for thousands
    def format_amount(val):
        val = round(val, -1)  # Round to nearest 10
        if val >= 1000:
            return f"{val/1000:.0f}k"
        return f"{val}"
    
    with cost_col1:
        st.write("**Tesla Model Y Costs**")
        
        tesla_breakdown = {
            'Cost Category': ['Depreciation', 'Insurance', 'Charging', 'Refinancing Fee', 'Repairs', 'Total'],
            'Amount (kr)': [
                format_amount(selected_tesla_dep), 
                format_amount(tesla_insurance), 
                format_amount(tesla_charging), 
                format_amount(tesla_refinancing), 
                format_amount(tesla_repairs),
                format_amount(tesla_total)
            ],
            'Percentage': [
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
            'Cost Category': ['Depreciation', 'Interest', 'Insurance', 'Charging', 'Repairs (3 yrs)', 'Total'],
            'Amount (kr)': [
                format_amount(jag_depreciation), 
                format_amount(jag_interest), 
                format_amount(jag_insurance), 
                format_amount(jag_charging), 
                format_amount(jaguar_repairs_3yr),
                format_amount(jaguar_total)
            ],
            'Percentage': [
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
            'Category': ['Depreciation', 'Insurance', 'Charging', 'Refinancing Fee', 'Repairs'],
            'Cost': [selected_tesla_dep, tesla_insurance, tesla_charging, tesla_refinancing, tesla_repairs]
        }
        
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(
            tesla_pie_data['Cost'],
            labels=tesla_pie_data['Category'],
            autopct='%1.1f%%',
            startangle=90,
            colors=plt.cm.Greens(np.linspace(0.2, 0.7, len(tesla_pie_data['Category'])))
        )
        total_display = f"{round(tesla_total/1000, 0):.0f}k kr"
        ax.set_title(f'Tesla Cost Distribution\nTotal: {total_display}')
        
        st.pyplot(fig)
    
    with pie_col2:
        st.write("**Jaguar I-Pace**")
        
        # Create pie chart data
        jaguar_pie_data = {
            'Category': ['Depreciation', 'Interest', 'Insurance', 'Charging', 'Repairs (3 yrs)'],
            'Cost': [jag_depreciation, jag_interest, jag_insurance, jag_charging, jaguar_repairs_3yr]
        }
        
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(
            jaguar_pie_data['Cost'],
            labels=jaguar_pie_data['Category'],
            autopct='%1.1f%%',
            startangle=90,
            colors=plt.cm.Reds(np.linspace(0.2, 0.7, len(jaguar_pie_data['Category'])))
        )
        total_display = f"{round(jaguar_total/1000, 0):.0f}k kr"
        ax.set_title(f'Jaguar Cost Distribution\nTotal: {total_display}')
        
        st.pyplot(fig)

# Footer
st.markdown("---")
st.caption("Car Cost Comparison Tool - Made with Streamlit") 