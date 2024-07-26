from helper import *
import calendar
import pandas as pd
import numpy as np
import numpy_financial as npf
# import matplotlib.pyplot as plt
# import matplotlib.patches as mpatches
import streamlit as st
# import plotly.express as px
import plotly.graph_objects as go

def calculate_grid_dg_costs(n,normal_tariff,  extended_outage_status, df, solar_generation,
 vos, feed_in_tariff, hourly_load_demand, profile_choice, 
 monthly_energy_consumption, solar_system_size, charge_from_grid, 
 discharge_battery, hos, eff, min_charge, demand_charge, increment_on_peak_tariff,
  decrement_on_non_peak_tariff,  initial_solar_module_cost, 
  initial_battery_cost, dg_cost, metering_option, metering_regime, num_years, discount_factor, grid_carbon_factor, 
  dg_carbon_factor, carbon_cost, solar_degradation_rate_yearly, battery_degradation_rate_yearly, demand_escalation_rate_yearly, 
  om_cost_escalation_rate, tariff_escalation_rate_yearly, fit_tariff_escalation_rate_yearly,
   demand_charge_escalation_rate_yearly, dg_escalation_rate_yearly, vos_escalation_rate_yearly, 
num_hours_in_year, charge, battery_replacement_schedule, battery_costs):
    
    calculated_values = []
    max_values_per_year = []
    yearly_dg_costs = []
    yearly_dg_grid_emis = []
    yearly_dg_dg_emis = []
    yearly_electricity_variable_bills_dg = []
    max_gd_dg1 = 0
    yearly_total_demands = []
    overall_max_load = 0

    for year in range(num_years):
        yearly_dg_cost = 0
        yearly_electricity_variable_bill_dg_year = 0
        max_load = 0
        yearly_dg_grid_emi = 0
        yearly_demand = 0
        yearly_dg_dg_emi = 0

        # Adjust tariff rates for the current year
        peak_tariff = float(normal_tariff) + (float(normal_tariff) * float(increment_on_peak_tariff))
        non_peak_tariff = float(normal_tariff) - (float(normal_tariff) * float(decrement_on_non_peak_tariff))
        current_normal_tariff = float(normal_tariff) * ((1 + float(tariff_escalation_rate_yearly)) ** year)
        current_peak_tariff = peak_tariff * ((1 + float(tariff_escalation_rate_yearly)) ** year)
        current_non_peak_tariff = non_peak_tariff * ((1 + float(tariff_escalation_rate_yearly)) ** year)
        current_feed_in_tariff = float(feed_in_tariff) * ((1 + float(fit_tariff_escalation_rate_yearly)) ** year)
        current_vos = float(vos) * ((1 + float(vos_escalation_rate_yearly)) ** year)
        current_dg_cost = float(dg_cost) * ((1 + float(dg_escalation_rate_yearly)) ** year)
        
        # Iterate over each hour in the year
        for index in range(num_hours_in_year):
            current_hour = year * num_hours_in_year + index
            hour_of_day = index % (24 * n)

            if year == 0:
                l = hourly_load_demand[index]
            else:
                prev_index = (year - 1) * num_hours_in_year + index
                l = calculated_values[prev_index]['load_demand'] * (1 + demand_escalation_rate_yearly)

            o = extended_outage_status[current_hour]
            demand = l / n
            yearly_demand += demand

            l_o = l * o

            if n == 1:
                if 16 <= hour_of_day < 22:
                    hourly_tariff = current_peak_tariff
                elif 22 <= hour_of_day or hour_of_day < 4:
                    hourly_tariff = current_non_peak_tariff
                else:
                    hourly_tariff = current_normal_tariff

            elif n == 2:
                if 32 <= hour_of_day < 44:
                    hourly_tariff = current_peak_tariff
                elif 44 <= hour_of_day or hour_of_day < 8:
                    hourly_tariff = current_non_peak_tariff
                else:
                    hourly_tariff = current_normal_tariff

            elif n == 4:
                if 64 <= hour_of_day < 88:
                    hourly_tariff = current_peak_tariff
                elif 88 <= hour_of_day or hour_of_day < 16:
                    hourly_tariff = current_non_peak_tariff
                else:
                    hourly_tariff = current_normal_tariff

            gd_dg = gd_die = 0

            max_load = max(max_load, l)

            if o == 0:
                gd_dg = l
            if o == 1:
                gd_die = l

            dg_grid_emi = gd_dg * (grid_carbon_factor / n)
            dg_dg_emi = gd_die * (dg_carbon_factor / n)

            yearly_dg_grid_emi += dg_grid_emi
            yearly_dg_dg_emi += dg_dg_emi

            if o == 0:
                max_gd_dg1 = max(max_gd_dg1, gd_dg)

            hourly_electricity_variable_bill_dg = ((l - l_o) * hourly_tariff) / n
            yearly_electricity_variable_bill_dg_year += hourly_electricity_variable_bill_dg

            hourly_dg_cost = ((l_o) * current_dg_cost) / n
            yearly_dg_cost += hourly_dg_cost

            calculated_values.append({
                'Year': year + 1,
                'Hour': index + 1,
                'load_demand': l,
                'outage': o,
                'gd_dg': gd_dg,
                'gd_die': gd_die,
                'dg_grid_emi': dg_grid_emi,
                'dg_dg_emi': dg_dg_emi,
                'hourly_tariff': hourly_tariff,
            })

        overall_max_load = max(overall_max_load, max_load)

        max_values_per_year.append({
            'Year': year + 1,
            'max_grid_load_dg1': max_gd_dg1,
            'max_demand_load': max_load
        })

        yearly_electricity_variable_bills_dg.append(yearly_electricity_variable_bill_dg_year * (1 / (1 + discount_factor) ** year))
        yearly_dg_costs.append(yearly_dg_cost * (1 / (1 + discount_factor) ** year))
        yearly_dg_grid_emis.append(yearly_dg_grid_emi)
        yearly_dg_dg_emis.append(yearly_dg_dg_emi)
        yearly_total_demands.append(yearly_demand * (1 / (1 + discount_factor) ** year))

    fixed_cost_dg_cost = sum(max_values_per_year[year]['max_grid_load_dg1'] * 12 * demand_charge * ((1 + demand_escalation_rate_yearly) / (1 + discount_factor) ** year)
                             for year in range(num_years))

    total_electricity_variable_bill_dg = sum(yearly_electricity_variable_bills_dg)
    total_yearly_dg_costs = sum(yearly_dg_costs)
    total_demand = sum(yearly_total_demands)

    total_dg_grid_emi = sum(yearly_dg_grid_emis)
    total_dg_dg_emi = sum(yearly_dg_dg_emis)
    total_dg_emi = total_dg_grid_emi + total_dg_dg_emi
    total_dg_emi_cost = total_dg_emi * carbon_cost

    total_cost_dg_grid = fixed_cost_dg_cost + total_electricity_variable_bill_dg + total_yearly_dg_costs + total_dg_emi_cost

    grid_dg_lcoe = total_cost_dg_grid / total_demand

    st.metric(label="Total cost for Grid+DG system", value=format_indian_currency(total_cost_dg_grid))
    st.metric(label="LCOE for Grid+DG system", value=f"{grid_dg_lcoe:.2f} INR/kWh")

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


    return {
        'fixed_cost_dg_cost': fixed_cost_dg_cost,
        'total_electricity_variable_bill_dg': total_electricity_variable_bill_dg,
        'total_yearly_dg_costs': total_yearly_dg_costs,
        'total_cost_dg_grid': total_cost_dg_grid,
        'grid_dg_lcoe': grid_dg_lcoe,
        'cashflow_table':cashflow_table,
        'total_costs':total_costs,
        'total_dg_emi':total_dg_emi,
        'total_dg_emi_cost':total_dg_emi_cost
    }
