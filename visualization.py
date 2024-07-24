#Plot for share of Demand Met from sources


# Data to plot
labels = ['Solar', 'BESS', 'Grid', 'Unmet Demand']
sizes = [total_sl, total_bl, total_gl, total_x] # Change these values as per your data
# Colors
colors = ['#009CD8','#8DB824','#EA5813','#9D9D9C']

# Plot
plt.figure(figsize=(8, 6))
plt.pie(sizes, colors=colors,autopct='%1.1f%%', startangle=90,wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'})

# Aspect ratio ensures that pie is drawn as a circle.
plt.axis('equal')


legend_patches = [mpatches.Patch(color=color, label=label) for color, label in zip(colors, labels)]

# Adding the legend at the bottom with colored patches and labels only
plt.legend(handles=legend_patches, loc='lower center', bbox_to_anchor=(0.5, -0.1), ncol=len(labels), frameon=False)



# Title
plt.title('Share of Demand Met from sources')


# Show plot
plt.show()

#Plot for share of usage of solar energy

# Data to plot
labels1 = ['Direct to load', 'Charging the battery', 'Fed to the Grid', 'Power Curtailed']
sizes1 = [total_sl, total_sb, total_sg, total_d]  # Change these values as per your data

# Colors
colors1 = ['#009CD8','#8DB824','#EA5813','#9D9D9C']

# Plot
plt.figure(figsize=(8, 6))
plt.pie(sizes1, colors=colors1,autopct='%1.1f%%', startangle=90,wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'})

# Aspect ratio ensures that pie is drawn as a circle.
plt.axis('equal')


legend_patches = [mpatches.Patch(color=color, label=label) for color, label in zip(colors1, labels1)]

# Adding the legend at the bottom with colored patches and labels only
plt.legend(handles=legend_patches, loc='lower center', bbox_to_anchor=(0.5, -0.1), ncol=len(labels1), frameon=False)



# Title
plt.title('Share of usage of solar energy')


# Show plot
plt.show()

#Plot for the gross electricity drawn from the grid (direct to load, charging the battery), electricity fed to the grid from solar, and the net electricity drawn from the grid

categories= ['Electricity from Grid to load', 'Electricity from Grid to battery','Electricity Fed to Grid from Solar', 'Net Electricity from Grid']
values = [total_gl/(n*1000), total_gb/(n*1000),-total_sg/(n*1000) ,total_ngd/(n*1000)]  # Values can be positive (increase) or negative (decrease)


# Calculate cumulative positions for the bars

cumulative_values = [0] + values[:-1]  # Start with 0 for the first bar
positions = range(len(values))

# Define colors based on the value sign
colors2 = ['#009CD8','#8DB824', '#EA5813', '#9D9D9C']



# Plotting the waterfall chart
plt.figure(figsize=(10, 6))
for i in range(len(values)): 
    if i == 0 or i == (len(values)-1):
        cumulative_values[i] = 0 
    else:
        cumulative_values[i] = cumulative_values[i-1] + values[i-1]

        # Adjust bar color based on value sign
    plt.bar(categories[i], values[i], bottom=cumulative_values[i], color=colors2[i])
    plt.text(categories[i], cumulative_values[i] + values[i] / 2, f"{values[i]:,.1f}", ha='center', va='center', color='black')

    
    
plt.title('Lifetime electricity consumption from grid')
plt.ylabel('Electricity (MWh)')

plt.grid(True, axis='y', linestyle='--', alpha=0.7)

# Format y-axis to disable scientific notation
plt.ticklabel_format(style='plain', axis='y')
plt.xticks(rotation=30, ha='right')

# Show plot
plt.tight_layout()
plt.show()

#Plot for total cost of ownership in terms of LCOE

categories2 = ['Total Grid+DG cost', 'System Component cost', 'Diesel Savings', 'Demand Charges', 'Energy Charges', 'Unmet Demand Cost', 'Solar+BESS+Grid']
values2 = [total_cost_dg_grid/(total_demand), (Capx_cost+total_om_cost)/(total_demand), -total_yearly_dg_costs/(total_demand), (total_fixed_component_cost-fixed_cost_dg_cost)/(total_demand), (total_electricity_cost-total_electricity_variable_bill_dg)/(total_demand), total_unmet_demand_cost/(total_demand), total_c/(total_demand)]

# Calculate cumulative positions for the bars


cumulative_values2 = [0] + values2[:-1]  # Start with 0 for the first bar
positions2 = range(len(values2))


colors4 = []

# Define colors based on the value sign
for i in range(len(values2)):
    
    if i == 0:
        colors4.append('#009CD8')  # First value
    elif i == len(values2) - 1:
        colors4.append('#9D9D9C')  # Last value
    else:
        if values2[i] > 0:
            colors4.append('#8DB824')  # Positive middle values
        if values2[i] < 0:
            colors4.append('#EA5813')  # Negative middle values
        if values2[i] == 0:
            colors4.append('#8DB824')  # Positive middle values
        
            


# Plotting the waterfall chart
plt.figure(figsize=(10, 6))
for i in range(len(values2)): 
    if i == 0 or i == (len(values2)-1):
        cumulative_values2[i] = 0 
    else:
        cumulative_values2[i] = cumulative_values2[i-1] + values2[i-1]

        # Adjust bar color based on value sign
    plt.bar(categories2[i], values2[i], bottom=cumulative_values2[i], color=colors4[i])
    plt.text(categories2[i], cumulative_values2[i] + values2[i] / 2, f"{values2[i]:,.1f}", ha='center', va='center', color='black')

    
    
# Title and labels
plt.title('Total cost of ownership - Solar + BESS + grid vis-a-vis grid + DG set')
plt.ylabel('₹/kWh')
plt.grid(True, axis='y', linestyle='--', alpha=0.7)
# Format y-axis to disable scientific notation
plt.ticklabel_format(style='plain', axis='y')
plt.xticks(rotation=30, ha='right')

# Show plot
plt.tight_layout()
plt.show()
