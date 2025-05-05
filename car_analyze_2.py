import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.widgets import Button
import matplotlib.gridspec as gridspec

# Adjustable input parameters
jaguar_repair_cost_range = (20_000, 80_000)   # Lower and upper limits for Jaguar annual repair costs
tesla_depreciation_range = (80_000, 220_000)  # Lower and upper limits for Tesla 3-year depreciation
granularity = 6  # Number of intervals

# Constants (fixed assumptions)
jaguar_fixed = 100_000 + 33_000 + 36_000 + 8_000  # Depreciation + Interest + Insurance + Charging
tesla_fixed = 30_000 + 6_000 + 2_150 + 15_000     # Insurance + Charging + Refinancing Fee + Repairs

# Generate ranges based on granularity
jag_repairs = np.linspace(jaguar_repair_cost_range[0], jaguar_repair_cost_range[1], granularity)
tesla_depreciations = np.linspace(tesla_depreciation_range[0], tesla_depreciation_range[1], granularity)

# Calculate matrix
matrix = np.zeros((granularity, granularity))
for i, tesla_dep in enumerate(tesla_depreciations):
    tesla_total = tesla_fixed + tesla_dep
    for j, jag_rep in enumerate(jag_repairs):
        jaguar_total = jaguar_fixed + 3 * jag_rep
        matrix[i, j] = jaguar_total - tesla_total

# Function to display detailed analysis of a specific scenario
def show_detailed_analysis(tesla_depreciation, jaguar_repair):
    # Calculate totals with the selected parameters
    tesla_total = tesla_fixed + tesla_depreciation
    jaguar_total = jaguar_fixed + (3 * jaguar_repair)
    difference = jaguar_total - tesla_total
    
    # Create a new figure for the detailed analysis
    plt.figure(figsize=(16, 10))
    gs = gridspec.GridSpec(2, 2, height_ratios=[2, 1])
    
    # Bar chart comparison
    ax1 = plt.subplot(gs[0, 0])
    labels = ['Tesla Model Y', 'Jaguar I-Pace']
    costs = [tesla_total, jaguar_total]
    colors = ['green', '#ff6666']
    
    bars = ax1.bar(labels, costs, color=colors)
    ax1.set_ylabel('Total 3-Year Cost (kr)')
    ax1.set_title('3-Year Ownership Cost Comparison')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 5000,
                f'{int(height):,} kr',
                ha='center', va='bottom')
        
    winner = "Tesla is cheaper" if difference > 0 else "Jaguar is cheaper"
    diff_text = f"Difference: {abs(int(difference)):,} kr ({winner})"
    ax1.text(0.5, -0.1, diff_text, transform=ax1.transAxes, ha='center', fontsize=12, fontweight='bold')
    
    # Cost breakdown pie charts
    # Tesla breakdown
    tesla_breakdown = {
        'Depreciation': tesla_depreciation,
        'Insurance': 30_000,
        'Charging': 6_000,
        'Refinancing Fee': 2_150,
        'Repairs': 15_000
    }
    
    # Jaguar breakdown
    jaguar_breakdown = {
        'Depreciation': 100_000,
        'Interest': 33_000,
        'Insurance': 36_000,
        'Charging': 8_000,
        'Repairs': 3 * jaguar_repair
    }
    
    # Plot Tesla pie chart
    ax2 = plt.subplot(gs[0, 1])
    tesla_labels = list(tesla_breakdown.keys())
    tesla_values = list(tesla_breakdown.values())
    
    ax2.pie(tesla_values, labels=tesla_labels, autopct='%1.1f%%', startangle=90, 
            colors=plt.cm.Greens(np.linspace(0.2, 0.7, len(tesla_labels))))
    ax2.set_title(f'Tesla Model Y Cost Breakdown\nTotal: {int(tesla_total):,} kr')
    
    # Plot Jaguar pie chart
    ax3 = plt.subplot(gs[1, 1])
    jaguar_labels = list(jaguar_breakdown.keys())
    jaguar_values = list(jaguar_breakdown.values())
    
    ax3.pie(jaguar_values, labels=jaguar_labels, autopct='%1.1f%%', startangle=90,
           colors=plt.cm.Reds(np.linspace(0.2, 0.7, len(jaguar_labels))))
    ax3.set_title(f'Jaguar I-Pace Cost Breakdown\nTotal: {int(jaguar_total):,} kr')
    
    # Add summary table with the analysis parameters
    ax4 = plt.subplot(gs[1, 0])
    ax4.axis('off')
    
    parameter_summary = (
        f"Analysis Parameters:\n\n"
        f"Tesla Model Y:\n"
        f"  - Depreciation: {int(tesla_depreciation):,} kr\n"
        f"  - Fixed costs: {int(tesla_fixed):,} kr\n"
        f"  - Total: {int(tesla_total):,} kr\n\n"
        f"Jaguar I-Pace:\n"
        f"  - Annual repairs: {int(jaguar_repair):,} kr/year\n"
        f"  - Total repairs (3 yrs): {int(3*jaguar_repair):,} kr\n"
        f"  - Fixed costs: {int(jaguar_fixed):,} kr\n"
        f"  - Total: {int(jaguar_total):,} kr\n\n"
        f"{diff_text}"
    )
    
    ax4.text(0.5, 0.5, parameter_summary, ha='center', va='center', fontsize=10,
            bbox={"facecolor":"lightgrey", "alpha":0.5, "pad":5}, 
            transform=ax4.transAxes)
    
    plt.tight_layout()
    plt.suptitle(f'Detailed Analysis - Tesla Depreciation: {int(tesla_depreciation):,} kr, Jaguar Repairs: {int(jaguar_repair):,} kr/yr', 
                fontsize=14, y=1.02)
    plt.subplots_adjust(top=0.9)
    plt.show()

# Create the original heatmap with clickable cells
fig, ax = plt.subplots(figsize=(12, 9))

# Plot heatmap
hm = sns.heatmap(
    matrix, annot=True, fmt=".0f", cmap='RdYlGn_r', center=0,
    xticklabels=[f"{int(j):,}" for j in jag_repairs],
    yticklabels=[f"{int(t):,}" for t in tesla_depreciations],
    cbar_kws={'label': 'Difference (Jaguar - Tesla, kr)'},
    linewidths=0.5, linecolor='gray', ax=ax
)

ax.set_xlabel("Jaguar Annual Repair Costs (kr/year)")
ax.set_ylabel("Tesla Depreciation over 3 years (kr)")
ax.set_title("Scenario Matrix: Jaguar vs Tesla Total Cost Difference 3 Year Perspective\n(Click on a cell for detailed analysis)")

# Add annotations to clarify meaning
for i in range(granularity):
    for j in range(granularity):
        diff = matrix[i, j]
        text = "Jaguar cheaper" if diff < 0 else "Tesla cheaper"
        color = "green" if diff < 0 else "red"
        ax.text(j + 0.5, i + 0.7, text, ha='center', va='center', color=color, fontsize=9, fontweight='bold')

# Fixed assumptions summary
assumptions = (
    f"Jaguar Fixed Costs:\n"
    f"  - Depreciation: 100,000 kr\n"
    f"  - Interest: 33,000 kr\n"
    f"  - Insurance (3 yrs): 36,000 kr\n"
    f"  - Charging: 8,000 kr\n\n"
    f"Tesla Fixed Costs:\n"
    f"  - Insurance (3 yrs): 30,000 kr\n"
    f"  - Charging: 6,000 kr\n"
    f"  - Refinancing Fee: 2,150 kr\n"
    f"  - Repairs (3 yrs): 15,000 kr"
)

plt.figtext(0.5, -0.15, assumptions, ha="center", fontsize=10, bbox={"facecolor":"lightgrey", "alpha":0.5, "pad":5})
plt.tight_layout(rect=[0, 0.05, 1, 1])

# Define the click event handler
def on_click(event):
    if event.inaxes == ax:
        # Get the coordinates of the clicked cell
        y, x = int(event.ydata), int(event.xdata)
        if 0 <= y < granularity and 0 <= x < granularity:
            # Get parameters for the clicked cell
            tesla_dep = tesla_depreciations[y]
            jag_rep = jag_repairs[x]
            
            # Show the detailed analysis
            show_detailed_analysis(tesla_dep, jag_rep)

# Connect the click event handler
fig.canvas.mpl_connect('button_press_event', on_click)

# Display a message to guide the user
print("INTERACTIVE ANALYSIS: Click on any cell in the heatmap to see a detailed cost breakdown for that scenario.")

plt.show()
