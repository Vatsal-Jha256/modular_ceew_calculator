def grid_dg_calc( num_hours_in_year, hourly_load_demand, extended_outage_status, normal_tariff, increment_on_peak_tariff= 0.2, decrement_on_non_peak_tariff=0.2, tariff_escalation_rate_yearly= 0.01, feed_in_tariff= 0.0,  dg_cost=30, num_years=25,vos_escalation_rate_yearly= 0.04, dg_escalation_rate_yearly = 0.04, 
            demand_escalation_rate_yearly= 0.01,vos=50, dg_cost=30,discount_factor=0.08, demand_charge=300, 
                 grid_carbon_factor=0.716, dg_carbon_factor=0.76, carbon_cost=0):
    
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
        current_feed_in_tariff = float(feed_in_tariff) * ((1 + float(tariff_escalation_rate_yearly)) ** year)
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

    return {
        'fixed_cost_dg_cost': fixed_cost_dg_cost,
        'total_electricity_variable_bill_dg': total_electricity_variable_bill_dg,
        'total_yearly_dg_costs': total_yearly_dg_costs,
        'total_cost_dg_grid': total_cost_dg_grid,
        'grid_dg_lcoe': grid_dg_lcoe
    }
