from helper import *
from visualization import graphs
import calendar
import pandas as pd
import numpy as np
import numpy_financial as npf
# import matplotlib.pyplot as plt
# import matplotlib.patches as mpatches
import streamlit as st
# import plotly.express as px
import plotly.graph_objects as go


#Cashflow Table for Grid+Solar+BESS system

def dashboard_main(results_solar_grid,results_grid_dg,
 results_solar_grid_dg, results_solar_grid_bess,
    n, option, extended_outage_status, df, solar_generation,
 vos, feed_in_tariff, hourly_load_demand, profile_choice, 
 monthly_energy_consumption, solar_system_size, charge_from_grid, 
 discharge_battery, hos, eff, min_charge, demand_charge, increment_on_peak_tariff,
  decrement_on_non_peak_tariff, initial_solar_module_cost, 
  initial_battery_cost, dg_cost, metering_option, metering_regime, num_years, discount_factor, grid_carbon_factor, 
  dg_carbon_factor, carbon_cost, solar_degradation_rate_yearly, battery_degradation_rate_yearly, demand_escalation_rate_yearly, 
  om_cost_escalation_rate, tariff_escalation_rate_yearly, fit_tariff_escalation_rate_yearly,
   demand_charge_escalation_rate_yearly, dg_escalation_rate_yearly, vos_escalation_rate_yearly, 
num_hours_in_year, charge, battery_replacement_schedule, battery_costs):
    
    
    total_coc=results_solar_grid_bess['total_coc']
    total_costs=results_grid_dg['total_costs']
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
    Capx_cost=results_solar_grid_bess['capx_cost']
    
    total_sl=results_solar_grid_bess['total_sl']
    total_bl=results_solar_grid_bess['total_bl']
    total_gl=results_solar_grid_bess['total_gl']
    total_x=results_solar_grid_bess['total_x']
    total_sb=results_solar_grid_bess['total_sb']
    total_sg=results_solar_grid_bess['total_sg']
    total_d=results_solar_grid_bess['total_d']
    total_gb=results_solar_grid_bess['total_gb']
    total_ngd=results_solar_grid_bess['total_ngd']
    total_cost_dg_grid=results_grid_dg['total_cost_dg_grid']
    total_demand=results_solar_grid_bess['total_demand']
    total_om_cost=results_solar_grid_bess['total_om_cost']
    total_yearly_dg_costs=results_grid_dg['total_yearly_dg_costs']
    total_fixed_component_cost=results_solar_grid_bess['fixed_component_cost']
    fixed_cost_dg_cost=results_grid_dg['fixed_cost_dg_cost']
    total_electricity_cost=results_solar_grid_bess['variable_component_cost']
    total_electricity_variable_bill_dg=results_grid_dg['total_electricity_variable_bill_dg']
    total_unmet_demand_cost=results_solar_grid_bess['unmet_demand_cost']
    total_c=results_solar_grid_bess['total_cost']
    # Print IRR
    #print(f"Internal Rate of Return (IRR): {irr:.2%}")

    #Dashboard Data

     # Display the System CAPX Cost
    #st.write(f"System Capx cost: {format_indian_currency(Capx_cost)}")

    # Display the System NPV
    #st.write(f"System NPV: {format_indian_currency(net_savings - Capx_cost-total_om_cost)}")
    total_cost_dg_grid=results_grid_dg['total_cost_dg_grid']
    total_c=results_solar_grid_bess['total_cost']
    total_dg_emi=results_grid_dg['total_dg_emi']
    total_emi=results_solar_grid_bess['total_emi']

    net_savings=total_cost_dg_grid-total_c+Capx_cost+total_om_cost

    st.metric(label="Payback Period", value=f"{payback_period} years")

    st.metric(label="Internal Rate of Return (IRR)", value=f"{irr:.2%}")

    st.metric(label="Lifetime savings", value=format_indian_currency(net_savings))

    st.metric(label="Lifetime avoided emissions", value=f"{(total_dg_emi - total_emi) / 1000:.0f} tCO2")

    if option == 2:
        optimal_bpc=results_solar_grid_bess['optimal_bpc']
        total_battery_size=results_solar_grid_bess['total_battery_size']
        st.metric(label="Optimized battery size for the solar+Grid+BESS system", value=f"{optimal_bpc:.0f}kW/{total_battery_size:.0f} kWh")
 

    graphs(n, total_sl, total_bl, total_gl, total_x, total_sb,
     total_sg, total_d, total_gb, total_ngd, total_cost_dg_grid, 
     total_demand, Capx_cost, total_om_cost, total_yearly_dg_costs, 
     total_fixed_component_cost, fixed_cost_dg_cost, total_electricity_cost, 
     total_electricity_variable_bill_dg, total_unmet_demand_cost, total_c )
