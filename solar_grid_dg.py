from helper import calculate_billing, calculate_month_key

def calculate_solar_grid_dg_costs(df, hourly_load_demand, extended_outage_status,  solar_system_size, n, dg_cost=30, 
                               num_years=25, initial_solar_module_cost=50000, normal_tariff=5, demand_charge=300,
                               increment_on_peak_tariff=0.2, decrement_on_non_peak_tariff=0.2, feed_in_tariff=0,
                               vos=50, grid_carbon_factor=0.716, carbon_cost=0, solar_degradation_rate_yearly=0.01,
                               battery_degradation_rate_yearly=0.03, demand_escalation_rate_yearly=0.02,
                               om_cost_escalation_rate=0.03, tariff_escalation_rate_yearly=0.01,
                               fit_tariff_escalation_rate_yearly=0.00, demand_charge_escalation_rate_yearly=0.01,
                               dg_escalation_rate_yearly=0.04, vos_escalation_rate_yearly=0.04, discount_factor=0.08,
                               num_hours_in_year=8760, metering_option=1):

    #Calculation of power flow for solar+Grid+DG scenario
    max_values_per_year = []
    calculated_values=[]
    max_values_per_year = []
    yearly_electricity_costs_sdg = []
    yearly_electricity_costs_sdg_nm = []
    yearly_dg_costs_sdg = []
    yearly_total_demands = []
    yearly_total_demands_nd = []
    yearly_sdg_grid_emis = []
    yearly_sdg_dg_emis = []
    overall_max_load = 0
    max_gd_sdg1 = 0

    for year in range(num_years):
        
    # initialization of variables 
        
        yearly_demand=0
        yearly_dg_cost_sdg=0
        yearly_cost_sdg=0  
        yearly_cos_sdg_nm=0
        max_load=0
        yearly_sdg_grid_emi=0
        yearly_sdg_dg_emi=0
        # Adjust tariff rates for the current year
        
        peak_tariff = float(normal_tariff) + (float(normal_tariff) * float(increment_on_peak_tariff))
        non_peak_tariff = float(normal_tariff) - (float(normal_tariff) * float(decrement_on_non_peak_tariff))
        current_normal_tariff = float(normal_tariff) * ((1 + float(tariff_escalation_rate_yearly)) ** year)
        current_peak_tariff = peak_tariff * ((1 + float(tariff_escalation_rate_yearly)) ** year)
        current_non_peak_tariff = non_peak_tariff * ((1 + float(tariff_escalation_rate_yearly)) ** year)
        current_feed_in_tariff = float(feed_in_tariff) * ((1 + float(tariff_escalation_rate_yearly)) ** year)
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
            demand=l/n
            yearly_demand+=demand
            
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

            sl_sdg=d_sdg=dg_unmet=gl_sdg=sg_sdg=gd_sdg=gf_sdg=ngd_sdg=sc_sdg=lc_sdg=0
            
            #Calculation of maximum load 

            max_load=max(max_load,l)
            
            sl_sdg=min(s,l)
            #sl_sdglist += sl_sdg
            #dg_unmet = 0
            if s>l and o==1:
                d_sdg=(s-l)
            if s>l and o==0:
                sg_sdg=(s-l)
            if s<l and o==1:
                dg_unmet= (l-s)                                #umnet load suppiled by DG
            if s<l and o==0:
                gl_sdg= (l-s)

            gd_sdg = gl_sdg  # Grid drawn
            gf_sdg = sg_sdg  # Grid feed-in
            ngd_sdg = gd_sdg - gf_sdg  # Net grid draw
            sc_sdg = sl_sdg + sg_sdg - s  # Solar check
            lc_sdg = sl_sdg + gl_sdg - l  # Load check

            sdg_grid_emi=ngd_sdg*(grid_carbon_factor)/n
            sdg_dg_emi=dg_unmet*(dg_carbon_factor)/n

            yearly_sdg_grid_emi+=sdg_grid_emi
            yearly_sdg_dg_emi+=sdg_dg_emi
            
            if metering_option == 1:
                # Example usage to populate monthly_ngd_peak based on some data
                month_key = calculate_month_key(index)
                if n==1:
                    if 16 <= hour_of_day < 22:
                        monthly_ngd_peak[month_key] += ngd_sdg
                        
                    elif 22 <= hour_of_day or hour_of_day < 4:
                        monthly_ngd_off_peak[month_key] += ngd_sdg              
                    else:
                        monthly_ngd_normal[month_key] += ngd_sdg 
                if n==2:
                    if 32 <= hour_of_day < 44:  # Peak hours from 5:00 PM to 11:00 PM
                        monthly_ngd_peak[month_key] += ngd_sdg
                    elif 44 <= hour_of_day or hour_of_day < 8:  # Non-peak hours from 11:00 PM to 5:00 AM
                        monthly_ngd_off_peak[month_key] += ngd_sdg           
                    else:  # Normal hours for the remaining time
                        monthly_ngd_normal[month_key] += ngd_sdg 
                if n==4:
                    if 64 <= hour_of_day < 88:  # Peak hours from 5:00 PM to 11:00 PM
                        monthly_ngd_peak[month_key] += ngd_sdg
                    elif 88 <= hour_of_day or hour_of_day < 16:  # Non-peak hours from 11:00 PM to 5:00 AM
                        monthly_ngd_off_peak[month_key] += ngd_sdg
                    else:  # Normal hours for the remaining time
                        monthly_ngd_normal[month_key] += ngd_sdg
            

            if metering_option == 2:
                hourly_electricity_cost_sdg= ((gd_sdg * hourly_tariff) - (sg_sdg *current_feed_in_tariff))/n
                yearly_cost_sdg += hourly_electricity_cost_sdg
            
            # Update maximum values of gd for the current year when there is no outage   
            if o == 0:           
                max_gd_sdg1=max(max_gd_sdg1,gd_sdg)

        
            # Accumulate yearly generator cost solar+Grid+DG

            hourly_dg_cost_sdg = (dg_unmet * (current_dg_cost))/n
            yearly_dg_cost_sdg += hourly_dg_cost_sdg
            
        

            # Append the calculated values to the list
            calculated_values.append({
                'Year': year + 1,
                'Hour': index + 1,
                'solar_generation': s,
                'load_demand': l,
                'outage': o,
                'hourly_tariff': hourly_tariff,
                'sg_sdg':sg_sdg, 'dg_numet':dg_unmet,
            
            
            })
            
        overall_max_load = max(overall_max_load, max_load)


        #print(monthly_ngd_peak)
        unitspk = monthly_ngd_peak
        billing_unitspk, total_banked_unitspk = calculate_billing(unitspk)
        #print("Billing units in year pk:", sum(billing_unitspk))
        #print("Total Banked Units at the end of the period:", total_banked_unitspk)
        yearly_sdg_peak_cost=(sum(billing_unitspk)*(current_peak_tariff)/n-total_banked_unitspk*(current_feed_in_tariff)/n)

        unitsopk = monthly_ngd_off_peak
        billing_unitsopk, total_banked_unitsopk = calculate_billing(unitsopk)
        #print("Billing units in year: opk", sum(billing_unitsopk))
        #print("Total Banked Units at the end of the period:", total_banked_unitsopk)
        yearly_sdg_off_peak_cost=(sum(billing_unitsopk)*(current_non_peak_tariff)/n-total_banked_unitsopk*(current_feed_in_tariff)/n)

        unitsn = monthly_ngd_normal
        billing_unitsn, total_banked_unitsn = calculate_billing(unitsn)
        #print("Billing units in year: n", sum(billing_unitsn))
        #print("Total Banked Units at the end of the period:", total_banked_unitsn)
        yearly_sdg_nor_cost=(sum(billing_unitsn)*(current_normal_tariff)/n-total_banked_unitsn*(current_feed_in_tariff)/n)

        yearly_cost_sdg_nm=yearly_sdg_peak_cost+yearly_sdg_off_peak_cost+yearly_sdg_nor_cost
        #print(yearly_cost_sdg)
        
        # Append yearly maximum values and costs
        max_values_per_year.append({
            'Year': year + 1,
            'max_grid_load_sdg1':max_gd_sdg1,
            'max_demand_load':max_load
        })    
        
        yearly_electricity_costs_sdg.append(yearly_cost_sdg*(1/(1+discount_factor)**year)) 
        yearly_electricity_costs_sdg_nm.append(yearly_cost_sdg_nm*(1/(1+discount_factor)**year))   
        yearly_dg_costs_sdg.append(yearly_dg_cost_sdg*(1/(1+discount_factor)**year))
        yearly_total_demands.append(yearly_demand*(1/(1+discount_factor)**year))
        yearly_total_demands_nd.append(yearly_demand) 
        yearly_sdg_grid_emis.append (yearly_sdg_grid_emi)
        yearly_sdg_dg_emis.append (yearly_sdg_dg_emi)

    #print(f'The maximum load value over 25 years is: {overall_max_load}')

    #Cost Calculation of solar+Grid+DG


    # Calculate the fixed component cost for solar+Grid+DG
    fixed_cost_sdg_cost=sum( max_values_per_year[year]['max_grid_load_sdg1'] *12* demand_charge*((1+demand_escalation_rate_yearly)/(1+discount_factor)**year)
        for year in range(num_years))

    # Calculate the variable component cost for solar+Grid+DG
    if metering_option==1:
        total_electricity_cost_sdg=sum(yearly_electricity_costs_sdg_nm)
    if metering_option==2:
        total_electricity_cost_sdg=sum(yearly_electricity_costs_sdg)

    # Calculate the diesel cost for solar+Grid+DG
    total_yearly_dg_costs_sdg = sum(yearly_dg_costs_sdg)

    #solar module cost
    solar_module_cost = solar_system_size * initial_solar_module_cost



    total_demand=sum(yearly_total_demands)
    #Calculate the carbon emission cost Grid+DG system

    total_sdg_grid_emi=sum(yearly_sdg_grid_emis)
    total_sdg_dg_emi=sum(yearly_sdg_dg_emis)
    total_sdg_emi=(total_sdg_grid_emi+total_sdg_dg_emi)
    total_sdg_emi_cost=(total_sdg_emi)*carbon_cost


    #O&M cost
    initial_om_cost_sg=0.01*solar_module_cost
    yearly_om_costs_sg=[]
    for year in range(num_years):
        if year == 0:
            yearly_om_cost_sg= initial_om_cost_sg
        else:
            yearly_om_cost_sg = initial_om_cost_sg * ((1 + om_cost_escalation_rate) ** year)

        yearly_om_costs_sg.append(yearly_om_cost_sg*(1/(1+discount_factor)**year))

    # Accumulate the total O&M cost
    total_om_cost_sg =sum(yearly_om_costs_sg)


    # Calculate the total cost with solar+Grid+DG
    total_cost_solar_grid_dg=fixed_cost_sdg_cost+total_electricity_cost_sdg+total_yearly_dg_costs_sdg+solar_module_cost+total_om_cost_sg+total_sdg_emi_cost


    #Calculate the LCOE of solar+Grid+DG system
    grid_sol_sdg_lcoe=(total_cost_solar_grid_dg)/(total_demand)


    return {
    'total_fixed_component_cost': fixed_cost_sdg_cost,
    'total_variable_component_cost': total_electricity_cost_sdg,
    'total_unmet_demand_cost': total_yearly_dg_costs_sdg,
    'total_capx_cost': solar_module_cost,
    'total_om_cost': total_om_cost_sg,
    'total_cost': total_cost_solar_grid_dg,
    'lcoe': grid_sol_sdg_lcoe
    }
