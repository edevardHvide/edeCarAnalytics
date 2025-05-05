import matplotlib.pyplot as plt

# --- Tesla Model Y Variables ---
tesla = {
    'name': 'Tesla Model Y',
    'depreciation': 100_000,
    'down_payment_interest': 30_943,
    'insurance': 10_000 * 3,
    'charging': 6_000,
    'repairs': 15_000,
}

tesla['total_cost'] = (
    tesla['depreciation']
    + tesla['down_payment_interest']
    + tesla['insurance']
    + tesla['charging']
    + tesla['repairs']
)

# --- Jaguar I-Pace Variables (Shared) ---
jaguar_base = {
    'name': 'Jaguar I-Pace',
    'depreciation': 80_000,
    'interest': 33_000,
    'insurance': 12_000 * 3,
    'charging': 8_000,
}

# Define Jaguar repair scenarios
repair_scenarios = {
    'Repairs 20k/yr': 20_000 * 3,
    'Repairs 40k/yr': 40_000 * 3,
    'Repairs 60k/yr': 60_000 * 3,
}

# Calculate total cost for each Jaguar scenario
jaguar_costs = {}
for label, repairs in repair_scenarios.items():
    total = (
        jaguar_base['depreciation']
        + jaguar_base['interest']
        + jaguar_base['insurance']
        + jaguar_base['charging']
        + repairs
    )
    jaguar_costs[label] = total

# Add Tesla to the cost comparison
labels = list(jaguar_costs.keys()) + [tesla['name']]
costs = list(jaguar_costs.values()) + [tesla['total_cost']]

# --- Plotting ---
plt.figure(figsize=(10, 6))
bars = plt.bar(labels, costs)

# Highlight Tesla bar in a different color
bars[-1].set_color('green')

plt.ylabel("Total 3-Year Cost (kr)")
plt.title("3-Year Ownership Cost: Jaguar I-Pace vs Tesla Model Y")
plt.xticks(rotation=15)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Add value labels
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 2000, f"{int(yval):,} kr", ha='center', va='bottom')

plt.tight_layout()
plt.show()
