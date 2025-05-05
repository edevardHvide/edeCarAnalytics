import numpy as np
import streamlit as st
import pandas as pd
import altair as alt

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

# Calculate matrix
matrix = np.zeros((granularity, granularity))
for i, tesla_dep in enumerate(tesla_depreciations):
    tesla_total = tesla_fixed + tesla_dep
    for j, jag_rep in enumerate(jag_repairs):
        jaguar_total = jaguar_fixed + 3 * jag_rep
        matrix[i, j] = jaguar_total - tesla_total

# Cost Difference Matrix section (full width)
st.subheader("Cost Difference Matrix")
st.write("Positive values (red): Tesla is cheaper | Negative values (blue): Jaguar is cheaper")

# Create data for heatmap
heatmap_data = []
for i, tesla_dep in enumerate(tesla_depreciations):
    for j, jag_rep in enumerate(jag_repairs):
        heatmap_data.append({
            'Tesla Depreciation': int(tesla_dep),
            'Jaguar Repairs': int(jag_rep),
            'Difference': matrix[i, j],
            'Winner': 'Tesla cheaper' if matrix[i, j] > 0 else 'Jaguar cheaper'
        })

df_heatmap = pd.DataFrame(heatmap_data)

# Create Altair heatmap
heatmap = alt.Chart(df_heatmap).mark_rect().encode(
    x=alt.X(
        'Jaguar Repairs:O', 
        title='Jaguar Annual Repair Costs (kr/year)', 
        axis=alt.Axis(labelAngle=0, format=',', labelOverlap=True)
    ),
    y=alt.Y(
        'Tesla Depreciation:O', 
        title='Tesla Depreciation over 3 years (kr)', 
        sort='descending',
        axis=alt.Axis(format=',')
    ),
    color=alt.Color(
        'Difference:Q', 
        scale=alt.Scale(
            scheme='redblue', 
            domain=[
                df_heatmap['Difference'].min(),
                df_heatmap['Difference'].max()
            ]
        ),
        legend=alt.Legend(title='Difference (Jaguar - Tesla, kr)')
    ),
    tooltip=[
        alt.Tooltip(
            'Tesla Depreciation:Q',
            title='Tesla Depreciation',
            format=','
        ),
        alt.Tooltip(
            'Jaguar Repairs:Q',
            title='Jaguar Repairs/yr',
            format=','
        ),
        alt.Tooltip(
            'Difference:Q', 
            title='Difference',
            format=','
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
    text=alt.Text('Difference:Q', format=','),
    color=alt.condition(
        alt.datum.Difference > 0,
        alt.value('white'),
        alt.value('black')
    )
)

# Combine and display
st.altair_chart(heatmap + text, use_container_width=True)

# Scenario selection section
st.subheader("Select a scenario to analyze")

# Use columns for the selection controls
col1, col2 = st.columns(2)

with col1:
    # Using select boxes for Tesla selection
    selected_tesla_index = st.selectbox(
        "Tesla Depreciation",
        options=range(granularity),
        format_func=lambda i: f"{int(tesla_depreciations[i]):,} kr"
    )

with col2:
    # Using select boxes for Jaguar selection
    selected_jaguar_index = st.selectbox(
        "Jaguar Annual Repairs",
        options=range(granularity),
        format_func=lambda i: f"{int(jag_repairs[i]):,} kr/yr"
    )

# Get the selected values
selected_tesla_dep = tesla_depreciations[selected_tesla_index]
selected_jaguar_rep = jag_repairs[selected_jaguar_index]

# Detailed analysis section
st.subheader("Detailed Cost Analysis")

# Calculate totals with the selected parameters
tesla_total = tesla_fixed + selected_tesla_dep
jaguar_total = jaguar_fixed + (3 * selected_jaguar_rep)
difference = jaguar_total - tesla_total

# Display the winner
winner = "Tesla Model Y is cheaper" if difference > 0 else "Jaguar I-Pace is cheaper"
diff_amount = abs(int(difference))

col1, col2 = st.columns([1, 2])

with col1:
    st.metric(
        "Cost Difference", 
        f"{diff_amount:,} kr", 
        delta=winner,
        delta_color="normal"
    )

# Create comparison bar chart with Altair
st.subheader("Total 3-Year Cost Comparison")

# Create a DataFrame for the bar chart
df_costs = pd.DataFrame({
    'Vehicle': ['Tesla Model Y', 'Jaguar I-Pace'],
    'Total Cost': [tesla_total, jaguar_total]
})

# Create Altair bar chart
bar_chart = alt.Chart(df_costs).mark_bar().encode(
    x=alt.X('Vehicle:N', axis=alt.Axis(labelAngle=0)),
    y=alt.Y('Total Cost:Q', title='Total 3-Year Cost (kr)', scale=alt.Scale(zero=True)),
    color=alt.Color('Vehicle:N', scale=alt.Scale(domain=['Tesla Model Y', 'Jaguar I-Pace'], 
                                               range=['green', '#ff6666'])),
    tooltip=[
        alt.Tooltip('Vehicle:N', title='Vehicle'),
        alt.Tooltip('Total Cost:Q', title='Total Cost', format=',')
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
    text=alt.Text('Total Cost:Q', format=',d')
)

# Display chart
st.altair_chart(bar_chart + text, use_container_width=True)

# Show cost breakdowns in tables
st.subheader("Cost Breakdown")

# Create two columns for Tesla and Jaguar breakdowns
cost_col1, cost_col2 = st.columns(2)

with cost_col1:
    st.write("**Tesla Model Y Costs**")
    
    jaguar_repairs_3yr = 3 * selected_jaguar_rep
    
    tesla_breakdown = {
        'Cost Category': ['Depreciation', 'Insurance', 'Charging', 'Refinancing Fee', 'Repairs', 'Total'],
        'Amount (kr)': [
            f"{int(selected_tesla_dep):,}", 
            f"{tesla_insurance:,}", 
            f"{tesla_charging:,}", 
            f"{tesla_refinancing:,}", 
            f"{tesla_repairs:,}",
            f"{int(tesla_total):,}"
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
    
    # Create pie chart data for Tesla
    tesla_pie_data = pd.DataFrame({
        'Category': ['Depreciation', 'Insurance', 'Charging', 'Refinancing Fee', 'Repairs'],
        'Cost': [selected_tesla_dep, tesla_insurance, tesla_charging, tesla_refinancing, tesla_repairs]
    })
    
    # Create donut chart for Tesla
    tesla_pie = alt.Chart(tesla_pie_data).mark_arc().encode(
        theta=alt.Theta(field="Cost", type="quantitative"),
        color=alt.Color(field="Category", type="nominal", scale=alt.Scale(scheme='greens')),
        tooltip=[
            alt.Tooltip("Category:N", title="Category"),
            alt.Tooltip("Cost:Q", title="Cost", format=",.0f"),
            alt.Tooltip("Cost:Q", title="Percentage", format=".1%")
        ]
    ).properties(
        title='Tesla Cost Distribution',
        width=250,
        height=250
    )
    
    st.altair_chart(tesla_pie, use_container_width=True)

with cost_col2:
    st.write("**Jaguar I-Pace Costs**")
    
    jaguar_repairs_3yr = 3 * selected_jaguar_rep
    
    jaguar_breakdown = {
        'Cost Category': ['Depreciation', 'Interest', 'Insurance', 'Charging', 'Repairs (3 yrs)', 'Total'],
        'Amount (kr)': [
            f"{jag_depreciation:,}", 
            f"{jag_interest:,}", 
            f"{jag_insurance:,}", 
            f"{jag_charging:,}", 
            f"{int(jaguar_repairs_3yr):,}",
            f"{int(jaguar_total):,}"
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
    
    # Create pie chart data for Jaguar
    jaguar_pie_data = pd.DataFrame({
        'Category': ['Depreciation', 'Interest', 'Insurance', 'Charging', 'Repairs (3 yrs)'],
        'Cost': [jag_depreciation, jag_interest, jag_insurance, jag_charging, jaguar_repairs_3yr]
    })
    
    # Create donut chart for Jaguar
    jaguar_pie = alt.Chart(jaguar_pie_data).mark_arc().encode(
        theta=alt.Theta(field="Cost", type="quantitative"),
        color=alt.Color(field="Category", type="nominal", scale=alt.Scale(scheme='reds')),
        tooltip=[
            alt.Tooltip("Category:N", title="Category"),
            alt.Tooltip("Cost:Q", title="Cost", format=",.0f"),
            alt.Tooltip("Cost:Q", title="Percentage", format=".1%")
        ]
    ).properties(
        title='Jaguar Cost Distribution',
        width=250,
        height=250
    )
    
    st.altair_chart(jaguar_pie, use_container_width=True)

# Add assumptions summary
with st.expander("Fixed Assumptions Summary", expanded=False):
    assumptions = f"""
    ### Jaguar Fixed Costs:
    - Depreciation: {jag_depreciation:,} kr
    - Interest: {jag_interest:,} kr
    - Insurance (3 yrs): {jag_insurance:,} kr
    - Charging: {jag_charging:,} kr
    - **Total Fixed (excluding repairs): {jaguar_fixed:,} kr**
    
    ### Tesla Fixed Costs:
    - Insurance (3 yrs): {tesla_insurance:,} kr
    - Charging: {tesla_charging:,} kr
    - Refinancing Fee: {tesla_refinancing:,} kr
    - Repairs (3 yrs): {tesla_repairs:,} kr
    - **Total Fixed (excluding depreciation): {tesla_fixed:,} kr**
    """
    st.markdown(assumptions)

# Footer
st.markdown("---")
st.caption("Car Cost Comparison Tool - Made with Streamlit & Altair") 