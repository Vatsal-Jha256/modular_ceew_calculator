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


#Optimization of the battery size
def optimize_solar_grid_bess_costs(n, normal_tariff, option, extended_outage_status, df, solar_generation,
 vos, feed_in_tariff, hourly_load_demand, profile_choice, 
 monthly_energy_consumption, solar_system_size, charge_from_grid, 
 discharge_battery, hos, eff, min_charge, demand_charge, increment_on_peak_tariff,
  decrement_on_non_peak_tariff, initial_solar_module_cost, 
  initial_battery_cost, dg_cost, metering_option, metering_regime, num_years, discount_factor, grid_carbon_factor, 
  dg_carbon_factor, carbon_cost, solar_degradation_rate_yearly, battery_degradation_rate_yearly, demand_escalation_rate_yearly, 
  om_cost_escalation_rate, tariff_escalation_rate_yearly, fit_tariff_escalation_rate_yearly,
   demand_charge_escalation_rate_yearly, dg_escalation_rate_yearly, vos_escalation_rate_yearly, 
num_hours_in_year, charge, battery_replacement_schedule, battery_costs):
    
    option = 2
    overall_max_load = 0
    calculated_values = []
    if option == 2:
        min_bpc = 1
        max_bpc = max(overall_max_load, solar_system_size)
        iterations = 10
        step = (max_bpc - min_bpc) / (iterations - 1)
        min_total_cost = float('inf')
        optimal_bpc = 0
        calculated_values = []

        for i in range(iterations):
            bpc = min_bpc + i * step
            overall_max_load = 0
            yearly_total_demands = []
            yearly_electricity_costs = []
            yearly_electricity_costs_nm = []
            max_values_per_year = []
            yearly_unmet_demand_costs = []
            yearly_om_costs = []
            yearly_emis = []
            yearly_total_sl = []
            yearly_total_bl = []
            yearly_total_gl = []
            yearly_total_sb = []
            yearly_total_gb = []
            yearly_total_sg = []
            yearly_total_d = []
            yearly_total_x = []
            yearly_total_ngd = []
            max_gd1 = 0
            #calculated_values = []

            for year in range(num_years):
                yearly_cost = 0
                yearly_cost_nm = 0
                yearly_unmet_demand_cost = 0
                yearly_demand = 0
                yearly_emi = 0
                yearly_sl = 0
                yearly_bl = 0
                yearly_gl = 0
                yearly_sb = 0
                yearly_gb = 0
                yearly_sg = 0
                yearly_d = 0
                yearly_x = 0
                yearly_ngd = 0

                cycle = year // 10
                current_bpc = bpc * ((1 - battery_degradation_rate_yearly) ** (year % 10))

                peak_tariff = float(normal_tariff) + (float(normal_tariff) * float(increment_on_peak_tariff))
                non_peak_tariff = float(normal_tariff) - (float(normal_tariff) * float(decrement_on_non_peak_tariff))
                current_normal_tariff = float(normal_tariff) * ((1 + float(tariff_escalation_rate_yearly)) ** year)
                current_peak_tariff = peak_tariff * ((1 + float(tariff_escalation_rate_yearly)) ** year)
                current_non_peak_tariff = non_peak_tariff * ((1 + float(tariff_escalation_rate_yearly)) ** year)
                current_feed_in_tariff = float(feed_in_tariff) * ((1 + float(tariff_escalation_rate_yearly)) ** year)
                current_vos = float(vos) * ((1 + float(vos_escalation_rate_yearly)) ** year)
                current_dg_cost = float(dg_cost) * ((1 + float(dg_escalation_rate_yearly)) ** year)

                monthly_ngd_normal = [0] * 13
                monthly_ngd_off_peak = [0] * 13
                monthly_ngd_peak = [0] * 13

                for index in range(num_hours_in_year):
                    current_hour = year * num_hours_in_year + index
                    hour_of_day = index % (24 * n)

                    if year == 0:
                        s = df.at[index, solar_generation] * solar_system_size
                        l = hourly_load_demand[index]
                    else:
                        prev_index = (year - 1) * num_hours_in_year + index
                        s = calculated_values[prev_index]['solar_generation'] * (1 - solar_degradation_rate_yearly)
                        l = calculated_values[prev_index]['load_demand'] * (1 + demand_escalation_rate_yearly)

                    o = extended_outage_status[current_hour]

                    if n == 1:
                        if 16 <= hour_of_day < 22:
                            hourly_tariff = current_peak_tariff
                        elif 22 <= hour_of_day or hour_of_day < 4:
                            hourly_tariff = current_non_peak_tariff
                        else:
                            hourly_tariff = current_normal_tariff

                    if n == 2:
                        if 32 <= hour_of_day < 44:
                            hourly_tariff = current_peak_tariff
                        elif 44 <= hour_of_day or hour_of_day < 8:
                            hourly_tariff = current_non_peak_tariff
                        else:
                            hourly_tariff = current_normal_tariff

                    if n == 4:
                        if 64 <= hour_of_day < 88:
                            hourly_tariff = current_peak_tariff
                        elif 88 <= hour_of_day or hour_of_day < 16:
                            hourly_tariff = current_non_peak_tariff
                        else:
                            hourly_tariff = current_normal_tariff

                    sl = c = sb = d = sg = gb = bg = r = bl = x = gl = gd = gf = ngd = sc = lc = 0

                    sl = min(s, l)

                    if s > l:
                        c = s - l
                        sb = min(c, current_bpc, (1 - charge[current_hour]) * (current_bpc * hos * n))

                        if (s - sl - sb) > 0 and o == 1:
                            d = c - sb
                        else:
                            if (s - sl - sb) > 0 and o == 0:
                                sg = c - sb
                            elif (s - sl - sb) < 0 and o == 0 and charge_from_grid:
                                gb = min(current_bpc, (1 - charge[current_hour]) * (current_bpc * hos * n))

                    if s < l and o == 1:
                        r = l - s
                        available_charge = max(charge[current_hour] - min_charge, 0) * (current_bpc * hos * eff)
                        bl = min(available_charge * n, current_bpc, r)
                        x = max(r - bl, 0)

                    else:
                        if s < l and o == 0 and 16 * n <= hour_of_day < 22 * n and discharge_battery and charge[current_hour] > 0.5:
                            available_charge = max(charge[current_hour] - 0.5, 0) * (current_bpc * hos * eff)
                            bl = min(available_charge * n, current_bpc, l - s)
                            gl = l - s - bl
                        else:
                            if s < l and o == 0:
                                gl = l - s

                    gd = gb + gl
                    gf = sg + bg
                    ngd = gd - gf
                    sc = sl + sb + sg - s
                    lc = sl + bl + gl - l

                    emi = ngd * (grid_carbon_factor / n)
                    yearly_emi += emi

                    yearly_sl += sl
                    yearly_bl += bl
                    yearly_gl += gl
                    yearly_sb += sb
                    yearly_gb += gb
                    yearly_sg += sg
                    yearly_d += d
                    yearly_ngd += ngd
                    yearly_x += x

                    if metering_option == 1:
                        month_key = calculate_month_key(index, n)
                        if n == 1:
                            if 16 <= hour_of_day < 22:
                                monthly_ngd_peak[month_key] += ngd
                            elif 22 <= hour_of_day or hour_of_day < 4:
                                monthly_ngd_off_peak[month_key] += ngd
                            else:
                                monthly_ngd_normal[month_key] += ngd
                        if n == 2:
                            if 32 <= hour_of_day < 44:
                                monthly_ngd_peak[month_key] += ngd
                            elif 44 <= hour_of_day or hour_of_day < 8:
                                monthly_ngd_off_peak[month_key] += ngd
                            else:
                                monthly_ngd_normal[month_key] += ngd

                        if n == 4:
                            if 64 <= hour_of_day < 88:
                                monthly_ngd_peak[month_key] += ngd
                            elif 88 <= hour_of_day or hour_of_day < 16:
                                monthly_ngd_off_peak[month_key] += ngd
                            else:
                                monthly_ngd_normal[month_key] += ngd

                    if metering_option == 2:
                        hourly_electricity_cost = ((gd * hourly_tariff) - (sg * current_feed_in_tariff)) / n
                        yearly_cost += hourly_electricity_cost

                    if o == 0:
                        max_gd1 = max(max_gd1, gd)

                    demand = l / n
                    yearly_demand += demand

                    hourly_unmet_demand_cost = (x * current_vos) / n
                    yearly_unmet_demand_cost += hourly_unmet_demand_cost

                    charge[current_hour + 1] = charge[current_hour] + (((sb + gb) * eff - bl / eff) / (current_bpc * hos * n))

                    calculated_values.append({
                        'year': year,
                        'hour': index,
                        'solar_generation': s,
                        'load_demand': l
                    })

                # Append yearly maximum values and costs
                max_values_per_year.append({
                    'Year': year + 1,        
                    'max_grid_load1': max_gd1
                })
        
        
        
                #print(monthly_ngd_peak)
                unitspk = monthly_ngd_peak
                billing_unitspk, total_banked_unitspk = calculate_billing(unitspk)
                #print("Billing units in year pk:", sum(billing_unitspk))
                #print("Total Banked Units at the end of the period:", total_banked_unitspk)
                yearly_peak_cost=((sum(billing_unitspk)*current_peak_tariff/n)-(total_banked_unitspk*(current_feed_in_tariff/n)))
            
                unitsopk = monthly_ngd_off_peak
                billing_unitsopk, total_banked_unitsopk = calculate_billing(unitsopk)
                #print("Billing units in year: opk", sum(billing_unitsopk))
                #print("Total Banked Units at the end of the period:", total_banked_unitsopk)
                yearly_off_peak_cost=(sum(billing_unitsopk)*(current_non_peak_tariff/n)-(total_banked_unitsopk*(current_feed_in_tariff/n)))
            
                unitsn = monthly_ngd_normal
                billing_unitsn, total_banked_unitsn = calculate_billing(unitsn)
                #print("Billing units in year: n", sum(billing_unitsn))
                #print("Total Banked Units at the end of the period:", total_banked_unitsn)
                yearly_nor_cost=(sum(billing_unitsn)*(current_normal_tariff/n)-(total_banked_unitsn*(current_feed_in_tariff/n)))
            
                yearly_cost_nm=yearly_peak_cost+yearly_off_peak_cost+yearly_nor_cost
                #print(yearly_cost)
        
                yearly_electricity_costs.append(yearly_cost*(1/(1+discount_factor)**year))
                yearly_electricity_costs_nm.append(yearly_cost_nm*(1/(1+discount_factor)**year))
                yearly_unmet_demand_costs.append(yearly_unmet_demand_cost*(1/(1+discount_factor)**year))
                yearly_total_demands.append(yearly_demand*(1/(1+discount_factor)**year))
                yearly_emis.append (yearly_emi)
                yearly_total_sl.append (yearly_sl)
                yearly_total_bl.append (yearly_bl)
                yearly_total_gl.append (yearly_gl)
                yearly_total_sb.append (yearly_sb)
                yearly_total_sg.append (yearly_sg)
                yearly_total_gb.append (yearly_gb)
                yearly_total_d.append (yearly_d)
                yearly_total_x.append (yearly_x)
                yearly_total_ngd.append (yearly_ngd)
                
                # Calculate the total fixed component cost over all years
            total_fixed_component_cost = sum(max_values_per_year[year]['max_grid_load1'] *12* demand_charge*((1+demand_escalation_rate_yearly)/(1+discount_factor)**year)
                    for year in range(num_years))
                
                # Calculate the total electricity cost over all years
            if metering_option==1:
                total_electricity_cost = sum(yearly_electricity_costs_nm)
            if metering_option==2:
                total_electricity_cost = sum(yearly_electricity_costs)
                #total demand
            total_demand=sum(yearly_total_demands)
            
                # Calculate the cost of unmet demand
            total_unmet_demand_cost = sum(yearly_unmet_demand_costs)
        
            #Total Carbon emission
        
            total_emi=sum(yearly_emis)
            total_carbon_savings_cost=total_emi*carbon_cost
        
            total_demand=sum(yearly_total_demands)
            
            
                
                # Calculate the solar module cost 
            solar_module_cost = solar_system_size * initial_solar_module_cost
            total_battery_cost = bpc * hos * battery_costs[0] # Initial battery cost
                
                # Add the replacement costs
            total_battery_cost += sum([bpc * hos * battery_costs[year] for year in battery_replacement_schedule])
                
                # Total Capex cost
            Capx_cost = solar_module_cost + total_battery_cost
            initial_om_cost = 0.01 * (solar_module_cost+ bpc*hos*initial_battery_cost)
            
            
            # O&M cost
            yearly_om_costs=[]
            for year in range(num_years):
                if year == 0:
                    yearly_om_cost = initial_om_cost
                else:
                    yearly_om_cost = initial_om_cost * ((1 + om_cost_escalation_rate) ** year)
                
                yearly_om_costs.append(yearly_om_cost*(1/(1+discount_factor)**year))
                
                    # Accumulate the total O&M cost
            total_om_cost = sum(yearly_om_costs)
        
            #Total cost for BESS system
            
            total_c = total_fixed_component_cost + total_unmet_demand_cost + Capx_cost + total_om_cost + total_electricity_cost+total_carbon_savings_cost
            
            total_sl=sum(yearly_total_sl)
            total_bl=sum(yearly_total_bl)
            total_gl=sum(yearly_total_gl)
            total_sb=sum(yearly_total_sb)
            total_sg=sum(yearly_total_sg)
            total_gb=sum(yearly_total_gb)
            total_d=sum(yearly_total_d)
            total_x=sum(yearly_total_x)
            total_ngd=sum(yearly_total_ngd)
            # Update min_total_cost and optimal_bpc if the current total cost is lower
            if (total_c) < min_total_cost:
                min_total_cost = (total_c)
                optimal_bpc = bpc

    #Cost Calculation of BESS+Solar+Grid System 

    if option==2:
        initial_bpc=optimal_bpc
        yearly_total_demands=[]
        yearly_electricity_costs = []
        yearly_electricity_costs_nm = []
        max_values_per_year = []
        yearly_unmet_demand_costs = []
        yearly_om_costs = []
        max_gd1=0
        yearly_emis=[]
        yearly_total_sl=[]
        yearly_total_bl=[]
        yearly_total_gb=[]
        yearly_total_gl=[]
        yearly_total_sb=[]
        yearly_total_sg=[]
        yearly_total_d=[]
        yearly_total_x=[]
        yearly_total_ngd=[]
        calculated_values=[]
        for year in range(num_years):
            # Calculate the current cycle for battery replacement
            cycle = year // 10
            # Calculate current year's battery power capacity considering the replacement every 10 years
            bpc = initial_bpc * ((1 - battery_degradation_rate_yearly) ** (year % 10))
        
            # initialization of variables
            yearly_cost = 0
            yearly_unmet_demand_cost = 0
            yearly_dg_cost = 0
            yearly_demand=0
            yearly_emi=0
            yearly_sl=0
            yearly_bl=0
            yearly_gl=0
            yearly_sb=0
            yearly_gb=0
            yearly_sg=0
            yearly_d=0
            yearly_x=0
            yearly_ngd=0
            # Adjust tariff rates for the current year
            peak_tariff = float(normal_tariff) + (float(normal_tariff) * float(increment_on_peak_tariff))
            non_peak_tariff = float(normal_tariff) - (float(normal_tariff) * float(decrement_on_non_peak_tariff))
            current_normal_tariff = float(normal_tariff) * ((1 + float(tariff_escalation_rate_yearly)) ** year)
            current_peak_tariff = peak_tariff * ((1 + float(tariff_escalation_rate_yearly)) ** year)
            current_non_peak_tariff = non_peak_tariff * ((1 + float(tariff_escalation_rate_yearly)) ** year)
            current_feed_in_tariff = float(feed_in_tariff) * ((1 + float(fit_tariff_escalation_rate_yearly)) ** year)
            current_vos = float(vos) * ((1 + float(vos_escalation_rate_yearly)) ** year)
            current_dg_cost = float(dg_cost) * ((1 + float(dg_escalation_rate_yearly)) ** year)
        
            monthly_ngd_peak = [0]*13
            monthly_ngd_off_peak = [0]*13
            monthly_ngd_normal = [0]*13
            
            # Iterate over each hour in the year
            for index in range(num_hours_in_year):
                # Calculate the current hour in the overall simulation
                current_hour = year * num_hours_in_year + index
                hour_of_day = index % (24*n)
        
                # Get the current hour's data from the original DataFrame for the first year or from calculated values for subsequent years
            
                if year == 0:
                    s = df.at[index, solar_generation] * solar_system_size    #solar generation
                    l = hourly_load_demand[index]
                else:
                    prev_index = (year - 1) * num_hours_in_year + index
                    s = calculated_values[prev_index]['solar_generation'] * (1 - solar_degradation_rate_yearly) 
                    l = calculated_values[prev_index]['load_demand'] * (1 + demand_escalation_rate_yearly)
        
        
                # Set outage status based on extended outage status list
                o = extended_outage_status[current_hour]
                
                # Add your further calculations and logic here...
                
                # Multiply 'load' and 'outage' for each hour and accumulate it
                l_o = l * o
                # Determine the tariff for the current hour
                if n==1:
                    if 16 <= hour_of_day < 22:  # Peak hours from 5:00 PM to 11:00 PM
                        hourly_tariff = current_peak_tariff
                    elif 22 <= hour_of_day or hour_of_day < 4:  # Non-peak hours from 11:00 PM to 5:00 AM
                        hourly_tariff = current_non_peak_tariff
                    else:  # Normal hours for the remaining time
                        hourly_tariff = current_normal_tariff
        
                if n==2:
                    if 32 <= hour_of_day < 44:  # Peak hours from 5:00 PM to 11:00 PM
                        hourly_tariff = current_peak_tariff
                    elif 44 <= hour_of_day or hour_of_day < 8:  # Non-peak hours from 11:00 PM to 5:00 AM
                        hourly_tariff = current_non_peak_tariff
                    else:  # Normal hours for the remaining time
                        hourly_tariff = current_normal_tariff
                if n==4:
                    if 64 <= hour_of_day < 88:  # Peak hours from 5:00 PM to 11:00 PM
                        hourly_tariff = current_peak_tariff
                    elif 88 <= hour_of_day or hour_of_day < 16:  # Non-peak hours from 11:00 PM to 5:00 AM
                        hourly_tariff = current_non_peak_tariff
                    else:  # Normal hours for the remaining time
                        hourly_tariff = current_normal_tariff
        
        
                # Initialize the variables
                sl= c = sb = d = sg = bg = gb = r = bl = x = gl =gd = gf = ngd = sc = lc = 0
        
                # Solar to load
                sl = min(s, l)
        
                if s > l:
                    c = s - l
                    sb = min(c, bpc, (1 - charge[current_hour]) * (bpc * hos*n))  # solar to battery
        
                    if (s - sl - sb) > 0 and o == 1:
                        d = c - sb  # power curtailment
                    else:
                        if (s - sl - sb) > 0 and o == 0:
                            sg = c - sb  # solar to grid
                        elif (s - sl - sb) < 0 and o == 0 and charge_from_grid:
                            gb = min(bpc, ((1 - charge[current_hour]) * (bpc * hos*n)))  # grid to battery
        
                if s < l and o == 1:
                    r = l - s  # residual load
                    available_charge = max(charge[current_hour] - min_charge, 0) * (bpc * hos * eff)  # prevent discharge below 20%
                    bl = min(available_charge*n, bpc, r)  # battery to the load
                    x = max(r - bl, 0)  # unmet demand
                else:
                    if s < l and o == 0 and hour_of_day in range(16*n, 22*n) and discharge_battery and charge[current_hour] > 0.5:
                        available_charge = max(charge[current_hour] - 0.5, 0) * (bpc * hos * eff)  # prevent discharge below 50%
                        bl = min(available_charge*n, bpc, l - s)  # Battery to the load
                        gl = l - s - bl  # Grid to load
                    else:
                        if s < l and o == 0:
                            gl = l - s  # Grid to load
        
                gd = gb + gl  # Grid draw
                gf = sg + bg  # Grid feed-in
                ngd = gd - gf  # Net grid draw
                sc = sl + sb + sg - s  # Solar check
                lc = sl + bl + gl - l  # Load check
        
                #Calculation of Grid Emission
        
                emi=ngd*(grid_carbon_factor/n)
                yearly_emi+=emi

                yearly_sl+=sl
                yearly_bl+=bl
                yearly_gl+=gl
                yearly_sb+=sb
                yearly_gb+=gb
                yearly_sg+=sg
                yearly_d+=d
                yearly_ngd+=ngd
                yearly_x+=x
                
                if metering_option == 1:
                    # Example usage to populate monthly_ngd_peak based on some data
                    month_key = calculate_month_key(index,n)
                    if n==1:               
                        if 16 <= hour_of_day < 22:
                            monthly_ngd_peak[month_key] += ngd     
                        elif 22 <= hour_of_day or hour_of_day < 4:
                            monthly_ngd_off_peak[month_key] += ngd              
                        else:
                            monthly_ngd_normal[month_key] += ngd
                    if n==2:               
                        if 32 <= hour_of_day < 44:
                            monthly_ngd_peak[month_key] += ngd     
                        elif 44 <= hour_of_day or hour_of_day < 8:
                            monthly_ngd_off_peak[month_key] += ngd              
                        else:
                            monthly_ngd_normal[month_key] += ngd
        
                    if n==4:               
                        if 64 <= hour_of_day < 88:
                            monthly_ngd_peak[month_key] += ngd     
                        elif 88 <= hour_of_day or hour_of_day < 16:
                            monthly_ngd_off_peak[month_key] += ngd              
                        else:
                            monthly_ngd_normal[month_key] += ngd
                
        
                if metering_option == 2:
                    hourly_electricity_cost = ((gd * hourly_tariff) - (sg * current_feed_in_tariff))/n
                    yearly_cost += hourly_electricity_cost
                    
                # Update maximum values of gd for the current year when there is no outage   
                if o == 0:
                    max_gd1 = max(max_gd1, gd)
            
                
                demand=l/n
                yearly_demand+=demand
            
                # Accumulate the unmet demand cost
                hourly_unmet_demand_cost = (x * current_vos)/n
                yearly_unmet_demand_cost += hourly_unmet_demand_cost 
                    
        
                # Ensure charge does not drop below minimum level
                charge[current_hour + 1] = charge[current_hour] + (((sb + gb) * eff - bl / eff) / (bpc * hos*n))
        
                # Append the calculated values to the list
                calculated_values.append({
                    'Year': year + 1,
                    'Hour': index + 1,
                    'solar_generation': s,
                    'load_demand': l,
                    'outage': o,
                    'sl': sl, 'c': c, 'sb': sb, 'd': d, 'sg': sg, 'bg': bg, 'gb': gb,
                    'r': r, 'bl': bl, 'x': x, 'gl': gl, 'gd': gd, 'gf': gf, 'ngd': ngd, 'sc': sc, 'lc': lc,
                    'hourly_tariff': hourly_tariff,
                    'charge': charge[current_hour]
                
                
                })
        
            # Append yearly maximum values and costs
            max_values_per_year.append({
                'Year': year + 1,
                'max_grid_load1': max_gd1
            })
        
            
                #print(monthly_ngd_peak)
            unitspk = monthly_ngd_peak
            billing_unitspk, total_banked_unitspk = calculate_billing(unitspk)
                #print("Billing units in year pk:", sum(billing_unitspk))
                #print("Total Banked Units at the end of the period:", total_banked_unitspk)
            yearly_peak_cost=((sum(billing_unitspk)*current_peak_tariff/n)-(total_banked_unitspk*(current_feed_in_tariff/n)))
            
            unitsopk = monthly_ngd_off_peak
            billing_unitsopk, total_banked_unitsopk = calculate_billing(unitsopk)
                #print("Billing units in year: opk", sum(billing_unitsopk))
                #print("Total Banked Units at the end of the period:", total_banked_unitsopk)
            yearly_off_peak_cost=(sum(billing_unitsopk)*(current_non_peak_tariff/n)-(total_banked_unitsopk*(current_feed_in_tariff/n)))
            
            unitsn = monthly_ngd_normal
            billing_unitsn, total_banked_unitsn = calculate_billing(unitsn)
                #print("Billing units in year: n", sum(billing_unitsn))
                #print("Total Banked Units at the end of the period:", total_banked_unitsn)
            yearly_nor_cost=(sum(billing_unitsn)*(current_normal_tariff/n)-(total_banked_unitsn*(current_feed_in_tariff/n)))
            
            yearly_cost_nm=yearly_peak_cost+yearly_off_peak_cost+yearly_nor_cost
                #print(yearly_cost)
        
            yearly_electricity_costs.append(yearly_cost*(1/(1+discount_factor)**year))
            yearly_electricity_costs_nm.append(yearly_cost_nm*(1/(1+discount_factor)**year))
            yearly_unmet_demand_costs.append(yearly_unmet_demand_cost*(1/(1+discount_factor)**year))
            yearly_total_demands.append(yearly_demand*(1/(1+discount_factor)**year))
            yearly_emis.append (yearly_emi)
            yearly_total_sl.append (yearly_sl)
            yearly_total_bl.append (yearly_bl)
            yearly_total_gl.append (yearly_gl)
            yearly_total_sb.append (yearly_sb)
            yearly_total_sg.append (yearly_sg)
            yearly_total_gb.append (yearly_gb)
            yearly_total_d.append (yearly_d)
            yearly_total_x.append (yearly_x)
            yearly_total_ngd.append (yearly_ngd)
                
                # Calculate the total fixed component cost over all years
        total_fixed_component_cost = sum(max_values_per_year[year]['max_grid_load1'] *12* demand_charge*((1+demand_escalation_rate_yearly)/(1+discount_factor)**year)
                    for year in range(num_years))
                
                # Calculate the total electricity cost over all years
        if metering_option==1:
            total_electricity_cost = sum(yearly_electricity_costs_nm)
        if metering_option==2:
            total_electricity_cost = sum(yearly_electricity_costs)
                #total demand
        total_demand=sum(yearly_total_demands)
            
                # Calculate the cost of unmet demand
        total_unmet_demand_cost = sum(yearly_unmet_demand_costs)
        
            #Total Carbon emission
        
        total_emi=sum(yearly_emis)
        total_carbon_savings_cost=total_emi*carbon_cost
        
        total_demand=sum(yearly_total_demands)
        
            
                
        # Calculate the solar module cost 
        solar_module_cost = solar_system_size * initial_solar_module_cost
        total_battery_cost = initial_bpc* hos * battery_costs[0] # Initial battery cost
        
                
        # Add the replacement costs
        total_battery_cost += sum([initial_bpc * hos * battery_costs[year] for year in battery_replacement_schedule])
                
        # Total Capex cost
        Capx_cost = solar_module_cost + total_battery_cost
        
        initial_om_cost = 0.01 * (solar_module_cost+ initial_bpc*hos*initial_battery_cost)
            
            
        # O&M cost
        yearly_om_costs=[]
        for year in range(num_years):
            if year == 0:
                yearly_om_cost = initial_om_cost
            else:
                yearly_om_cost = initial_om_cost * ((1 + om_cost_escalation_rate) ** year)
                
            yearly_om_costs.append(yearly_om_cost*(1/(1+discount_factor)**year))
                
                    # Accumulate the total O&M cost
        total_om_cost = sum(yearly_om_costs)
        
            #Total cost for BESS system
            
        total_c = total_fixed_component_cost + total_unmet_demand_cost + Capx_cost + total_om_cost + total_electricity_cost+total_carbon_savings_cost
        total_battery_size=optimal_bpc*hos
        total_sl=sum(yearly_total_sl)
        total_bl=sum(yearly_total_bl)
        total_gl=sum(yearly_total_gl)
        total_sb=sum(yearly_total_sb)
        total_sg=sum(yearly_total_sg)
        total_gb=sum(yearly_total_gb)
        total_d=sum(yearly_total_d)
        total_x=sum(yearly_total_x)
        total_ngd=sum(yearly_total_ngd)
        st.metric(label="Optimized total cost for solar+Grid+BESS system", value=format_indian_currency(total_c))
        st.metric(label="Optimized LCOE for solar+Grid+BESS system", value=f"{total_c / total_demand:.2f} INR/kWh")

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

        return {
            'fixed_component_cost':total_fixed_component_cost,
            'variable_component_cost':total_electricity_cost,
            'unmet_demand_cost':total_unmet_demand_cost,
            'capx_cost':Capx_cost,
            'total_om_cost':total_om_cost,
            'total_cost':total_c,
            'lcoe':total_c/total_demand,
            'total_sl':total_sl,
            'total_bl':total_bl,
            'total_gl':total_gl,
            'total_sb':total_sb,
            'total_sg':total_sg,
            'total_d':total_d,
            'total_x':total_x,
            'total_gb':total_gb,
            'total_ngd':total_ngd,
            'total_demand':total_demand,
            'cashflow_table':cashflow_table,
            'total_coc':total_coc,
            'total_emi':total_emi,
            'optimal_bpc':optimal_bpc,
            'total_battery_size':total_battery_size
        }

