import streamlit as st
import calendar
import pandas as pd
import numpy as np
import numpy_financial as npf
import plotly.graph_objects as go

def graphs(n, total_sl, total_bl, total_gl, total_x, total_sb,
     total_sg, total_d, total_gb, total_ngd, total_cost_dg_grid, 
     total_demand, Capx_cost, total_om_cost, total_yearly_dg_costs, 
     total_fixed_component_cost, fixed_cost_dg_cost, total_electricity_cost, 
     total_electricity_variable_bill_dg, total_unmet_demand_cost, total_c):
    # Data to plot
    labels = ['Solar', 'BESS', 'Grid', 'Unmet Demand']
    sizes = [total_sl, total_bl, total_gl, total_x]
    colors = ['#009CD8', '#8DB824', '#EA5813', '#9D9D9C']

    # Pie Chart for Share of Demand Met from Sources
    fig1 = go.Figure(data=[go.Pie(labels=labels, values=sizes, hole=.3)])
    fig1.update_traces(marker=dict(colors=colors, line=dict(color='white', width=3)))
    fig1.update_layout(title_text='Share of Demand Met from sources')

    # Data to plot for share of usage of solar energy
    labels1 = ['Direct to load', 'Charging the battery', 'Fed to the Grid', 'Power Curtailed']
    sizes1 = [total_sl, total_sb, total_sg, total_d]
    colors1 = ['#009CD8', '#8DB824', '#EA5813', '#9D9D9C']

    # Pie Chart for Share of Usage of Solar Energy
    fig2 = go.Figure(data=[go.Pie(labels=labels1, values=sizes1, hole=.3)])
    fig2.update_traces(marker=dict(colors=colors1, line=dict(color='white', width=3)))
    fig2.update_layout(title_text='Share of Usage of Solar Energy')

    # Data for the gross electricity drawn from the grid
    categories = ['Electricity from Grid to load', 'Electricity from Grid to battery', 'Electricity Fed to Grid from Solar', 'Net Electricity from Grid']
    values = [total_gl / (n * 1000), total_gb / (n * 1000), -total_sg / (n * 1000), total_ngd / (n * 1000)]
    colors2 = ['#009CD8', '#8DB824', '#EA5813', '#9D9D9C']

    # Waterfall Chart for Lifetime Electricity Consumption from Grid
    fig3 = go.Figure()
    cumulative_values = [0] + [sum(values[:i + 1]) for i in range(len(values) - 1)]
    for i, (category, value, cumulative) in enumerate(zip(categories, values, cumulative_values)):
        base_value = 0 if i == 0 or i == len(values) - 1 else cumulative
        fig3.add_trace(go.Bar(
            x=[category],
            y=[value],
            base=[base_value],
            marker_color=colors2[i],
            name=category
        ))

    fig3.update_layout(title_text='Lifetime Electricity Consumption from Grid', yaxis_title='Electricity (MWh)', barmode='stack')

    # Data for total cost of ownership
    categories1 = ['Total Grid+DG cost', 'System Component cost', 'Diesel Savings', 'Demand Charges', 'Energy Charges', 'Unmet Demand Cost', 'Solar+BESS+Grid']
    values1 = [total_cost_dg_grid / 1000000, (Capx_cost + total_om_cost) / 1000000, -total_yearly_dg_costs / 1000000, (total_fixed_component_cost - fixed_cost_dg_cost) / 1000000, (total_electricity_cost - total_electricity_variable_bill_dg) / 1000000, total_unmet_demand_cost / 1000000, total_c / 1000000]

    # Waterfall Chart for Total Cost of Ownership
    fig4 = go.Figure()
    cumulative_values1 = [0] + [sum(values1[:i + 1]) for i in range(len(values1) - 1)]
    colors3 = ['#009CD8'] + ['#8DB824' if v > 0 else '#EA5813' for v in values1[1:-1]] + ['#9D9D9C']

    for i, (category, value, cumulative) in enumerate(zip(categories1, values1, cumulative_values1)):
        base_value = 0 if i == 0 or i == len(values1) - 1 else cumulative
        fig4.add_trace(go.Bar(
            x=[category],
            y=[value],
            base=[base_value],
            marker_color=colors3[i],
            name=category
        ))

    fig4.update_layout(title_text='Total Cost of Ownership - Solar + BESS + Grid vs Grid + DG Set', yaxis_title='₹ Lakh', barmode='stack')

    # Data for total cost of ownership in terms of LCOE
    categories2 = ['Total Grid+DG cost', 'System Component cost', 'Diesel Savings', 'Demand Charges', 'Energy Charges', 'Unmet Demand Cost', 'Solar+BESS+Grid']
    values2 = [total_cost_dg_grid / total_demand, (Capx_cost + total_om_cost) / total_demand, -total_yearly_dg_costs / total_demand, (total_fixed_component_cost - fixed_cost_dg_cost) / total_demand, (total_electricity_cost - total_electricity_variable_bill_dg) / total_demand, total_unmet_demand_cost / total_demand, total_c / total_demand]

    # Waterfall Chart for Total Cost of Ownership in terms of LCOE
    fig5 = go.Figure()
    cumulative_values2 = [0] + [sum(values2[:i + 1]) for i in range(len(values2) - 1)]
    colors4 = ['#009CD8'] + ['#8DB824' if v > 0 else '#EA5813' for v in values2[1:-1]] + ['#9D9D9C']

    for i, (category, value, cumulative) in enumerate(zip(categories2, values2, cumulative_values2)):
        base_value = 0 if i == 0 or i == len(values2) - 1 else cumulative
        fig5.add_trace(go.Bar(
            x=[category],
            y=[value],
            base=[base_value],
            marker_color=colors4[i],
            name=category
        ))

    fig5.update_layout(title_text='Total Cost of Ownership - Solar + BESS + Grid vs Grid + DG Set (LCOE)', yaxis_title='₹/kWh', barmode='stack')

    # Displaying in Streamlit
    st.title('Energy System Analysis')

    # First row: Pie charts
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

    # Second row: Waterfall charts for electricity consumption and total cost of ownership
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(fig3, use_container_width=True)
    with col4:
        st.plotly_chart(fig4, use_container_width=True)

    # Third row: Waterfall chart for total cost of ownership in terms of LCOE
    st.plotly_chart(fig5, use_container_width=True)
