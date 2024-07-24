from helper import calculate_billing, calculate_month_key

def calculate_solar_grid_costs(df, hourly_load_demand, extended_outage_status,  solar_system_size, dg_cost=30,num_years=25, n=1,
                                initial_solar_module_cost=50000, normal_tariff=5, demand_charge=300,
                               increment_on_peak_tariff=0.2, decrement_on_non_peak_tariff=0.2, feed_in_tariff=0,
                               vos=50, grid_carbon_factor=0.716, carbon_cost=0, solar_degradation_rate_yearly=0.01,
                               battery_degradation_rate_yearly=0.03, demand_escalation_rate_yearly=0.02,
                               om_cost_escalation_rate=0.03, tariff_escalation_rate_yearly=0.01,
                               fit_tariff_escalation_rate_yearly=0.00, demand_charge_escalation_rate_yearly=0.01,
                               dg_escalation_rate_yearly=0.04, vos_escalation_rate_yearly=0.04, discount_factor=0.08,
                               num_hours_in_year=8760, metering_option=1):

    calculated_values=[]
    max_values_per_year = []
    yearly_electricity_costs_sg = []
    yearly_electricity_costs_sg_nm = []
    yearly_unmet_demand_costs_sg = []
    yearly_sg_grid_emis = []
    overall_max_load = 0

    for year in range(num_years):
        yearly_unmet_demand_cost_sg = 0
        yearly_cost_sg = 0
        yearly_cost_sg_nm = 0
        max_load = 0
        yearly_sg_grid_emi = 0
        max_gd_sg1 = 0

        peak_tariff = float(normal_tariff) + (float(normal_tariff) * float(increment_on_peak_tariff))
        non_peak_tariff = float(normal_tariff) - (float(normal_tariff) * float(decrement_on_non_peak_tariff))
        current_normal_tariff = float(normal_tariff) * ((1 + float(tariff_escalation_rate_yearly)) ** year)
        current_peak_tariff = peak_tariff * ((1 + float(tariff_escalation_rate_yearly)) ** year)
        current_non_peak_tariff = non_peak_tariff * ((1 + float(tariff_escalation_rate_yearly)) ** year)
        current_feed_in_tariff = float(feed_in_tariff) * ((1 + float(tariff_escalation_rate_yearly)) ** year)
        current_vos = float(vos) * ((1 + float(vos_escalation_rate_yearly)) ** year)
        current_dg_cost = float(dg_cost) * ((1 + float(dg_escalation_rate_yearly)) ** year)

        monthly_ngd_peak = [0] * 13
        monthly_ngd_off_peak = [0] * 13
        monthly_ngd_normal = [0] * 13

        for index in range(num_hours_in_year):
            current_hour = year * num_hours_in_year + index
            hour_of_day = index % (24 * n)

            if year == 0:
                s = df.at[index, 'solar_generation'] * solar_system_size
                l = hourly_load_demand[index]
            else:
                prev_index = (year - 1) * num_hours_in_year + index
                s = calculated_values[prev_index]['solar_generation'] * (1 - solar_degradation_rate_yearly)
                l = calculated_values[prev_index]['load_demand'] * (1 + demand_escalation_rate_yearly)

            o = extended_outage_status[current_hour]

            l_o = l * o

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

            sl_sg = x_sg = sg_sg = gl_sg = gd_sg = gf_sg = ngd_sg = sc_sg = lc_sg = 0

            max_load = max(max_load, l)

            sl_sg = min(s, l)

            if o == 1:
                x_sg = l
            if s > l and o == 0:
                sg_sg = (s - l)
            if s < l and o == 0:
                gl_sg = (l - s)

            gd_sg = gl_sg
            gf_sg = sg_sg
            ngd_sg = gd_sg - gf_sg
            sc_sg = sl_sg + sg_sg - s
            lc_sg = sl_sg + gl_sg - l

            sg_emi = (ngd_sg * grid_carbon_factor) / n
            yearly_sg_grid_emi += sg_emi

            if metering_option == 1:
                month_key = calculate_month_key(index)
                if n == 1:
                    if 16 <= hour_of_day < 22:
                        monthly_ngd_peak[month_key] += ngd_sg
                    elif 22 <= hour_of_day or hour_of_day < 4:
                        monthly_ngd_off_peak[month_key] += ngd_sg
                    else:
                        monthly_ngd_normal[month_key] += ngd_sg
                if n == 2:
                    if 32 <= hour_of_day < 44:
                        monthly_ngd_peak[month_key] += ngd_sg
                    elif 44 <= hour_of_day or hour_of_day < 8:
                        monthly_ngd_off_peak[month_key] += ngd_sg
                    else:
                        monthly_ngd_normal[month_key] += ngd_sg
                if n == 4:
                    if 64 <= hour_of_day < 88:
                        monthly_ngd_peak[month_key] += ngd_sg
                    elif 88 <= hour_of_day or hour_of_day < 16:
                        monthly_ngd_off_peak[month_key] += ngd_sg
                    else:
                        monthly_ngd_normal[month_key] += ngd_sg

            if metering_option == 2:
                hourly_electricity_cost_sg = ((gd_sg * hourly_tariff) - (sg_sg * current_feed_in_tariff)) / n
                yearly_cost_sg += hourly_electricity_cost_sg

            if o == 0:
                max_gd_sg1 = max(max_gd_sg1, gd_sg)

            hourly_unmet_demand_cost_sg = (x_sg * current_vos) / n
            yearly_unmet_demand_cost_sg += hourly_unmet_demand_cost_sg

            calculated_values.append({
                'Year': year + 1,
                'Hour': index + 1,
                'solar_generation': s,
                'load_demand': l,
                'outage': o,
                'hourly_tariff': hourly_tariff,
                'gd_sg': gd_sg,
                'gf_sg': gf_sg,
                'ngd_sg': ngd_sg,
                'sl_sg': sl_sg
            })

        overall_max_load = max(overall_max_load, max_load)

        unitspk = monthly_ngd_peak
        billing_unitspk, total_banked_unitspk = calculate_billing(unitspk)
        yearly_sg_peak_cost = ((sum(billing_unitspk) * current_peak_tariff / n) - (total_banked_unitspk * (current_feed_in_tariff / n)))

        unitsopk = monthly_ngd_off_peak
        billing_unitsopk, total_banked_unitsopk = calculate_billing(unitsopk)
        yearly_sg_off_peak_cost = (sum(billing_unitsopk) * (current_non_peak_tariff / n) - (total_banked_unitsopk * (current_feed_in_tariff / n)))

        unitsn = monthly_ngd_normal
        billing_unitsn, total_banked_unitsn = calculate_billing(unitsn)
        yearly_sg_nor_cost = (sum(billing_unitsn) * (current_normal_tariff / n) - (total_banked_unitsn * (current_feed_in_tariff / n)))

        yearly_cost_sg_nm = yearly_sg_peak_cost + yearly_sg_off_peak_cost + yearly_sg_nor_cost

        max_values_per_year.append({
            'Year': year + 1,
            'max_grid_load_sg1': max_gd_sg1,
            'max_demand_load': max_load
        })

        yearly_electricity_costs_sg.append(yearly_cost_sg * (1 / (1 + discount_factor) ** year))
        yearly_electricity_costs_sg_nm.append(yearly_cost_sg_nm * (1 / (1 + discount_factor) ** year))
        yearly_unmet_demand_costs_sg.append(yearly_unmet_demand_cost_sg * (1 / (1 + discount_factor) ** year))
        yearly_sg_grid_emis.append(yearly_sg_grid_emi)

    fixed_cost_dg_cost = sum(max_values_per_year[year]['max_grid_load_sg1'] * 12 * demand_charge * ((1 + demand_escalation_rate_yearly) / (1 + discount_factor) ** year) for year in range(num_years))

    if metering_option == 1:
        total_electricity_cost_sg = sum(yearly_electricity_costs_sg_nm)
    if metering_option == 2:
        total_electricity_cost_sg = sum(yearly_electricity_costs_sg)

    total_unmet_demand_cost_sg = sum(yearly_unmet_demand_costs_sg)
    total_sg_emi = sum(yearly_sg_grid_emis)
    total_sg_emi_cost = total_sg_emi * carbon_cost
    total_demand = sum([sum(y['load_demand'] for y in calculated_values if y['Year'] == year + 1) for year in range(num_years)])

    solar_module_cost = solar_system_size * initial_solar_module_cost
    initial_om_cost_sg = 0.01 * solar_module_cost
    yearly_om_costs_sg = []
    for year in range(num_years):
        if year == 0:
            yearly_om_cost_sg = initial_om_cost_sg
        else:
            yearly_om_cost_sg = initial_om_cost_sg * ((1 + om_cost_escalation_rate) ** year)
        yearly_om_costs_sg.append(yearly_om_cost_sg * (1 / (1 + discount_factor) ** year))

    total_om_cost_sg = sum(yearly_om_costs_sg)
    total_cost_solar_grid = fixed_cost_dg_cost + total_electricity_cost_sg + total_unmet_demand_cost_sg + solar_module_cost + total_om_cost_sg + total_sg_emi_cost
    grid_sg_lcoe = total_cost_solar_grid / total_demand

    return {
        'fixed_cost_dg_cost': fixed_cost_dg_cost,
        'total_electricity_cost_sg': total_electricity_cost_sg,
        'total_unmet_demand_cost_sg': total_unmet_demand_cost_sg,
        'solar_module_cost': solar_module_cost,
        'total_om_cost_sg': total_om_cost_sg,
        'total_cost_solar_grid': total_cost_solar_grid,
        'grid_sg_lcoe': grid_sg_lcoe
    }


