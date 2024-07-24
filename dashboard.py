from helper import *
from solar_grid_dg import calculate_solar_grid_dg_costs
from solar_grid import calculate_solar_grid_costs
from grid_dg import calculate_grid_dg_costs
from solar_grid_bess_analyse import calculate_solar_grid_bess_costs
from solar_grid_bess_optimize import optimize_solar_grid_bess_costs



#Cashflow Table for Grid+Solar+BESS system


# Initialize numpy arrays for yearly costs
total_fixed_component_costc = np.zeros(num_years)
total_electricity_costc = np.zeros(num_years)
total_unmet_demand_costc = np.zeros(num_years)
total_electricity_costc_nm= np.zeros(num_years)
total_om_costc = np.zeros(num_years)
total_coc = np.zeros(num_years)
total_capexc = np.zeros(num_years)

# Assign CAPEX cost for the first year
total_capexc[0] = Capx_cost

# Calculate the yearly costs
for year in range(num_years):
    total_fixed_component_costc[year] = max_values_per_year[year]['max_grid_load1'] * 12 * demand_charge * ((1 + demand_escalation_rate_yearly) / (1 + discount_factor) ** year)
    if metering_option==1:
        total_electricity_costc[year]=yearly_electricity_costs_nm[year]
    if metering_option==2:
        total_electricity_costc[year] = yearly_electricity_costs[year] 
    total_unmet_demand_costc[year] = yearly_unmet_demand_costs[year]
    total_om_costc[year] = yearly_om_costs[year]
    total_coc[year] = total_fixed_component_costc[year] + total_electricity_costc[year] + total_om_costc[year] + total_unmet_demand_costc[year] + total_capexc[year]

# Print the total costs for verification
#print("Fixed Cost DG Cost per year: ", total_fixed_component_costc)
#print("Variable Electricity Bill DG per year: ", total_electricity_costc)
#print("DG Costs per year: ", total_unmet_demand_costc)
#print("Total O&M Costs per year: ", total_om_costc)
#print("CAPEX Cost per year: ", total_capexc)
#print("Total Costs per year: ", total_coc)

cashflow_table = np.array([total_fixed_component_costc, total_electricity_costc,total_unmet_demand_costc, total_om_costc, total_capexc, total_coc]).T

# Print the cashflow table
#print("\nCashflow Table Array:")
#print("Year | Fixed Cost | Variable Electricity Bill|  | Unmet Demand Costs | O&M Costs | CAPEX | Total Costs")
#for year in range(num_years):
   # print(f"{year + 1}    | {total_fixed_component_costc[year]:.2f}        | {total_electricity_costc[year]:.2f}                 | {total_unmet_demand_costc[year]:.2f}     | {total_om_costc[year]:.2f}   | {total_capexc[year]:.2f}   | {total_coc[year]:.2f} ")

#Cashflow Table for Grid+DG system

fixed_cost_dg_costs = np.zeros(num_years)
variable_electricity_bills_dg = np.zeros(num_years)
dg_costs = np.zeros(num_years)
total_costs = np.zeros(num_years)

# Calculate the yearly costs
for year in range(num_years):
    fixed_cost_dg_costs[year] = max_values_per_year[year]['max_grid_load_dg1'] * 12 * demand_charge * ((1 + demand_escalation_rate_yearly) / (1 + discount_factor) ** year)
    variable_electricity_bills_dg[year] = yearly_electricity_variable_bills_dg[year]
    dg_costs[year] = yearly_dg_costs[year]
    total_costs[year] = fixed_cost_dg_costs[year] + variable_electricity_bills_dg[year] + dg_costs[year]
    
total_cost_all_components = np.sum(total_costs)

# Print the total costs for verification
#print("Fixed Cost DG Cost per year: ", fixed_cost_dg_costs)
#print("Variable Electricity Bill DG per year: ", variable_electricity_bills_dg)
#print("DG Costs per year: ", dg_costs)
#print("Total Costs per year: ", total_costs)

cashflow_table = np.array([fixed_cost_dg_costs, variable_electricity_bills_dg, dg_costs, total_costs]).T

# Print the cashflow table
#print("\nCashflow Table Array:")
#print("Year | Fixed Cost DG | Variable Electricity Bill DG | DG Costs | Total Costs")
#for year in range(num_years):
#    print(f"{year + 1}    | {fixed_cost_dg_costs[year]:.2f}        | {variable_electricity_bills_dg[year]:.2f}                 | {dg_costs[year]:.2f}     | {total_costs[year]:.2f}")
#Cashflow of Solar+BESS+Grid-Grid+DG System
cost_difference = total_coc - total_costs
# Calculate cumulative cost difference
cumulative_cost_difference = [sum(cost_difference[:i+1]) for i in range(num_years)]

# Print the resulting cashflow table
#print("Year |  Total Costs (Solar+BESS) | Total Costs (Grid+DG) | Cost Difference | Cumulative Cost Difference")
#for year in range(num_years):
   # print(f"{year + 1}    |  {total_coc[year]:.2f}                 | {total_costs[year]:.2f}             | {cost_difference[year]:.2f}             | {cumulative_cost_difference[year]:.2f}")
# Find the payback period
payback_period = next((i+1 for i, diff in enumerate(cumulative_cost_difference) if diff <= 0), None)

# Calculation of IRR

# Calculate IRR
anti_discount_factor = [1]*num_years


for i in range(num_years):
    anti_discount_factor[i] = (1+discount_factor)**i


cash_flows = ((cost_difference)*(anti_discount_factor))

irr = npf.irr(cash_flows)

# Print IRR
#print(f"Internal Rate of Return (IRR): {irr:.2%}")

#Dashboard Data

net_savings=total_cost_dg_grid-total_c+Capx_cost

print(f"Payback Period: {payback_period} years")

print(f"Internal Rate of Return (IRR): {irr:.2%}")

print(f"Lifetime savings:{format_indian_currency(net_savings)}")

print(f"System Capx cost:{format_indian_currency(Capx_cost)}")

print(f"System NPV:{format_indian_currency(net_savings-Capx_cost)}")

print(f"Lifetime avoided emissions: {(total_dg_emi - total_emi)/1000:.0f} tCO2")

if option==2:
    print(f"Optimized battery size for the solar+Grid+BESS system: {optimal_bpc:.0f}kW/{total_battery_size:.0f} kWh")

print(f"The total demand over the 25 years period is: {sum(yearly_total_demands_nd):.0f} kWh")
