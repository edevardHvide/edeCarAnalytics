import numpy as np
import streamlit as st
import pandas as pd
import altair as alt

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
st.markdown(
    """
    This tool helps you analyze the 3-year cost difference between a Tesla Model Y 
    and a Jaguar I-Pace under various depreciation and repair cost scenarios. 
    The heatmap shows cost differences across scenarios.
    """
)

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
st.write("Positive values (red): Tesla is cheaper | Negative values (blue): Jaguar is cheaper")

# Format function for k-format display
def format_k_value(val):
    val = int(val)
    if abs(val) >= 1000:
        return f"{val/1000:.0f}k"
    return f"{val}"

# Create data for heatmap
heatmap_data = []
for i, tesla_dep in enumerate(tesla_depreciations):
    for j, jag_rep in enumerate(jag_repairs):
        heatmap_data.append({
            'Tesla Depreciation': int(tesla_dep),
            'Jaguar Repairs': int(jag_rep),
            'Difference': matrix[i, j],
            'Winner': 'Tesla cheaper' if matrix[i, j] > 0 else 'Jaguar cheaper',
            'Formatted Difference': format_k_value(matrix[i, j])
        })

df_heatmap = pd.DataFrame(heatmap_data)

# Create Altair heatmap
heatmap = alt.Chart(df_heatmap).mark_rect().encode(
    x=alt.X(
        'Jaguar Repairs:O', 
        title='Jaguar Annual Repair Costs (kr/year)', 
        axis=alt.Axis(labelAngle=0, format='~s', labelOverlap=True)
    ),
    y=alt.Y(
        'Tesla Depreciation:O', 
        title='Tesla Depreciation over 3 years (kr)', 
        sort='descending',
        axis=alt.Axis(format='~s')
    ),
    color=alt.Color(
        'Difference:Q', 
        scale=alt.Scale(
            scheme='redblue', 
            domain=[
                df_heatmap['Difference'].min(),
                df_heatmap['Difference'].max()
            ],
            zero=True
        ),
        legend=alt.Legend(title='Difference (Jaguar - Tesla, kr)')
    ),
    tooltip=[
        alt.Tooltip(
            'Tesla Depreciation:Q',
            title='Tesla Depreciation',
            format='~s'
        ),
        alt.Tooltip(
            'Jaguar Repairs:Q',
            title='Jaguar Repairs/yr',
            format='~s'
        ),
        alt.Tooltip(
            'Formatted Difference:N', 
            title='Difference'
        ),
        alt.Tooltip(
            'Winner:N',
            title='Result'
        )
    ]
).properties(
    width='container',
    height=400,
    title='Scenario Matrix: Jaguar vs Tesla Cost Difference'
)

# Add text overlay
text = alt.Chart(df_heatmap).mark_text(baseline='middle').encode(
    x='Jaguar Repairs:O',
    y='Tesla Depreciation:O',
    text='Formatted Difference:N',
    color=alt.condition(
        alt.datum.Difference > 0,
        alt.value('white'),
        alt.value('black')
    )
)

# Combine and display
st.altair_chart(heatmap + text, use_container_width=True)

# --- Scenario Selection (Full Width) ---
st.subheader("Select a scenario to analyze")

# Using number inputs for free value selection
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
    
    # Create comparison bar chart with Altair
    st.subheader("Total 3-Year Cost Comparison")
    
    # Create a DataFrame for the bar chart
    df_costs = pd.DataFrame({
        'Vehicle': ['Tesla Model Y', 'Jaguar I-Pace'],
        'Total Cost': [tesla_total, jaguar_total],
        'Formatted Cost': [
            f"{int(tesla_total/1000)}k kr", 
            f"{int(jaguar_total/1000)}k kr"
        ]
    })
    
    # Create Altair bar chart
    bar_chart = alt.Chart(df_costs).mark_bar().encode(
        x=alt.X('Vehicle:N', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Total Cost:Q', title='Total 3-Year Cost (kr)', scale=alt.Scale(zero=True)),
        color=alt.Color('Vehicle:N', scale=alt.Scale(domain=['Tesla Model Y', 'Jaguar I-Pace'], 
                                                   range=['green', '#ff6666'])),
        tooltip=[
            alt.Tooltip('Vehicle:N', title='Vehicle'),
            alt.Tooltip('Formatted Cost:N', title='Total Cost')
        ]
    ).properties(
        width='container',
        height=300
    )
    
    # Add text labels
    text = bar_chart.mark_text(
        align='center',
        baseline='bottom',
        dy=-10,
        fontSize=14
    ).encode(
        text='Formatted Cost:N'
    )
    
    # Display chart
    st.altair_chart(bar_chart + text, use_container_width=True)

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
    
    # Pie charts using Altair
    st.subheader("Cost Distribution")
    pie_col1, pie_col2 = st.columns(2)
    
    with pie_col1:
        st.write("**Tesla Model Y**")
        
        # Create pie chart data
        tesla_display_total = selected_tesla_dep + tesla_insurance + tesla_charging + tesla_refinancing + tesla_repairs
        
        tesla_pie_df = pd.DataFrame({
            'Category': ['Depreciation', 'Insurance', 'Charging', 'Refinancing Fee', 'Repairs'],
            'Cost': [selected_tesla_dep, tesla_insurance, tesla_charging, tesla_refinancing, tesla_repairs],
            'Percentage': [
                selected_tesla_dep/tesla_display_total*100,
                tesla_insurance/tesla_display_total*100,
                tesla_charging/tesla_display_total*100,
                tesla_refinancing/tesla_display_total*100,
                tesla_repairs/tesla_display_total*100
            ]
        })
        
        tesla_pie = alt.Chart(tesla_pie_df).mark_arc().encode(
            theta=alt.Theta(field="Percentage", type="quantitative"),
            color=alt.Color(field="Category", type="nominal", scale=alt.Scale(scheme='greens')),
            tooltip=[
                alt.Tooltip("Category:N", title="Category"),
                alt.Tooltip("Cost:Q", title="Cost", format="~s"),
                alt.Tooltip("Percentage:Q", title="Percentage", format=".1f")
            ]
        ).properties(
            title=f"Tesla Ownership Cost Distribution\nTotal: {format_amount(tesla_display_total)} kr",
            width='container',
            height=250
        )
        
        st.altair_chart(tesla_pie, use_container_width=True)
    
    with pie_col2:
        st.write("**Jaguar I-Pace**")
        
        # Create pie chart data
        jaguar_display_total = jag_depreciation + jag_interest + jag_insurance + jag_charging + jaguar_repairs_3yr
        
        jaguar_pie_df = pd.DataFrame({
            'Category': ['Depreciation', 'Interest', 'Insurance', 'Charging', 'Repairs (3 yrs)'],
            'Cost': [jag_depreciation, jag_interest, jag_insurance, jag_charging, jaguar_repairs_3yr],
            'Percentage': [
                jag_depreciation/jaguar_display_total*100,
                jag_interest/jaguar_display_total*100,
                jag_insurance/jaguar_display_total*100,
                jag_charging/jaguar_display_total*100,
                jaguar_repairs_3yr/jaguar_display_total*100
            ]
        })
        
        jaguar_pie = alt.Chart(jaguar_pie_df).mark_arc().encode(
            theta=alt.Theta(field="Percentage", type="quantitative"),
            color=alt.Color(field="Category", type="nominal", scale=alt.Scale(scheme='reds')),
            tooltip=[
                alt.Tooltip("Category:N", title="Category"),
                alt.Tooltip("Cost:Q", title="Cost", format="~s"),
                alt.Tooltip("Percentage:Q", title="Percentage", format=".1f")
            ]
        ).properties(
            title=f"Jaguar Ownership Cost Distribution\nTotal: {format_amount(jaguar_display_total)} kr",
            width='container',
            height=250
        )
        
        st.altair_chart(jaguar_pie, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Car Cost Comparison Tool - Made with Streamlit and Altair") 