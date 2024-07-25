from helper import *
from tariff_rates import tariff_rates
import streamlit as st
from solar_grid_dg import calculate_solar_grid_dg_costs
from solar_grid import calculate_solar_grid_costs
from grid_dg import calculate_grid_dg_costs
from solar_grid_bess_analyze import calculate_solar_grid_bess_costs
from solar_grid_bess_optimize import optimize_solar_grid_bess_costs
from dashboard import dashboard_main
import calendar
import pandas as pd
import numpy as np
import numpy_financial as npf
# import matplotlib.pyplot as plt
# import matplotlib.patches as mpatches
import streamlit as st
# import plotly.express as px
import plotly.graph_objects as go



# List of months for iteration
months = ['January', 'February', 'March', 'April', 'May', 'June', 
          'July', 'August', 'September', 'October', 'November', 'December']

# Display the options
st.write("Select an option for data pattern:")
options = ["Hourly time block", "30 min time block", "15 min time block"]

# Create a selectbox for the options
time_block_option = st.selectbox("Choose a time block option:", options)

# Determine the value of 'n' based on the selection
if time_block_option == "Hourly time block":
    n = 1

elif time_block_option == "30 min time block":
    n = 2

elif time_block_option == "15 min time block":
    n = 4

req_length=8760*n


# Define a function to parse state and city from the predefined dictionary
def get_state_city_options(tariff_rates):
    state_city_dict = {}
    for key in tariff_rates.keys():
        state, city = key.split(" - ")
        if state not in state_city_dict:
            state_city_dict[state] = []
        state_city_dict[state].append(city)
    return state_city_dict

# Function to get tariff rates
def get_tariff_rate(state, city, consumer_category):
    key = f"{state} - {city}"
    return tariff_rates.get(key, {}).get(consumer_category)

# Parse the state and city options from the tariff rates dictionary
state_city_dict = get_state_city_options(tariff_rates)

# Select state
selected_state = st.selectbox("Select your state", list(state_city_dict.keys()))

# Select city if the state has multiple cities
cities = state_city_dict[selected_state]
if len(cities) > 1:
    selected_city = st.selectbox("Select your city", cities)
else:
    selected_city = cities[0]

# Combine state and city
state = f"{selected_state} - {selected_city}"

# Select consumer category
consumer_category = st.selectbox("Select your consumer category", ['residential', 'industrial', 'commercial'])

# Select tariff option (predefined or custom)
tariff_option = st.radio("Select an option for electricity tariff", ("Predefined", "Custom"))

if tariff_option=="Predefined":
    # Check if the state and consumer category are valid
    if state in tariff_rates and consumer_category in tariff_rates[state]:
        # Retrieve the corresponding tariff rate based on user input
        normal_tariff = tariff_rates[state][consumer_category]
    else:
        st.error("Invalid state or consumer category.")
        exit()

else:
    normal_tariff = st.number_input("Enter electricity tariff rate: ", min_value=0.0, step=1.0)

outage_schedule = get_outage_schedule(n)
yearly_outage_status = generate_outage_status(outage_schedule, months, n)

# Repeat the yearly outage status for 25 years
extended_outage_status = yearly_outage_status * 25
#Read the input file

file_path = './datasets/input1.xlsx'

if n == 1:
    solar_data_sheet = 'Hourly'
elif n == 2:
    solar_data_sheet = 'Half-Hourly'
elif n == 4:
    solar_data_sheet = 'Quaterly'
else:
    raise ValueError("Invalid value for n. Expected 1, 2, or 4.")


# Attempt to read the Excel file
try:
    df = pd.read_excel(file_path, sheet_name=solar_data_sheet)
    #st.write('file read successfully')
    #st.write(df)

except FileNotFoundError:
    st.write(f"File not found: {file_path}")
except ValueError as e:
    st.write(f"ValueError: {e}")
except Exception as e:
    st.write(f"An error occurred: {e}")

st.title("Select an option for solar generation:")
option = st.selectbox(
    "Choose an option:",
    ["Predefined solar generation", "Custom solar generation"]
)
if option == "Predefined solar generation":
    # Select the solar-generation coloumn based on the input state
    
    if state == 'Andhra Pradesh - Visakhapatnam':
        solar_generation = 'Andhra Pradesh - Visakhapatnam'
    elif state == 'Assam - Guwahati':
        solar_generation = 'Assam - Guwahati'
    elif state == 'Bihar - Patna':
        solar_generation = 'Bihar - Patna'
    elif state == 'Chandigarh - Chandigarh':
        solar_generation = 'Chandigarh - Chandigarh'
    elif state == 'Chhattisgarh - Bilaspur':
        solar_generation = 'Chhattisgarh - Bilaspur'
    elif state == 'Chhattisgarh - Raipur':
        solar_generation = 'Chhattisgarh - Raipur'
    elif state == 'Delhi - Delhi':
        solar_generation = 'Delhi - Delhi'
    elif state == 'Goa - Goa':
        solar_generation = 'Goa - Goa'
    elif state == 'Gujarat - Ahmedabad':
        solar_generation = 'Gujarat - Ahmedabad'
    elif state == 'Gujarat - Rajkot':
        solar_generation = 'Gujarat - Rajkot'
    elif state == 'Haryana - Faridabad':
        solar_generation = 'Haryana - Faridabad'
    elif state == 'Himachal Pradesh - Shimla':
        solar_generation = 'Himachal Pradesh - Shimla'
    elif state == 'Jammu and Kashmir - Srinagar':
        solar_generation = 'Jammu and Kashmir - Srinagar'
    elif state == 'Jharkhand - Ranchi':
        solar_generation = 'Jharkhand - Ranchi'
    elif state == 'Karnataka - Bengaluru':
        solar_generation = 'Karnataka - Bengaluru'
    elif state == 'Karnataka - Mangalore':
        solar_generation = 'Karnataka - Mangalore'
    elif state == 'Kerala - Kochi':
        solar_generation = 'Kerala - Kochi'
    elif state == 'Kerala - Thrissur':
        solar_generation = 'Kerala - Thrissur'
    elif state == 'Madhya Pradesh - Bhopal':
        solar_generation = 'Madhya Pradesh - Bhopal'
    elif state == 'Madhya Pradesh - Indore':
        solar_generation = 'Madhya Pradesh - Indore'
    elif state == 'Madhya Pradesh - Jabalpur':
        solar_generation = 'Madhya Pradesh - Jabalpur'
    elif state == 'Maharashtra - Aurangabad':
        solar_generation = 'Maharashtra - Aurangabad'
    elif state == 'Maharashtra - Mumbai':
        solar_generation = 'Maharashtra - Mumbai'
    elif state == 'Maharashtra - Navi Mumbai':
        solar_generation = 'Maharashtra - Navi Mumbai'
    elif state == 'Maharashtra - Pune':
        solar_generation = 'Maharashtra - Pune'
    elif state == 'Odisha - Bhubaneswar':
        solar_generation = 'Odisha - Bhubaneswar'
    elif state == 'Odisha - Cuttack':
        solar_generation = 'Odisha - Cuttack'
    elif state == 'Punjab - Amritsar':
        solar_generation = 'Punjab - Amritsar'
    elif state == 'Rajasthan - Bikaner':
        solar_generation = 'Rajasthan - Bikaner'
    elif state == 'Rajasthan - Jaipur':
        solar_generation = 'Rajasthan - Jaipur'
    elif state == 'Rajasthan - Jodhpur':
        solar_generation = 'Rajasthan - Jodhpur'
    elif state == 'Tamil Nadu - Chennai':
        solar_generation = 'Tamil Nadu - Chennai'
    elif state == 'Tamil Nadu - Coimbatore':
        solar_generation = 'Tamil Nadu - Coimbatore'
    elif state == 'Tamil Nadu - Madurai':
        solar_generation = 'Tamil Nadu - Madurai'
    elif state == 'Telangana - Hyderabad':
        solar_generation = 'Telangana - Hyderabad'
    elif state == 'Uttar Pradesh - Agra':
        solar_generation = 'Uttar Pradesh - Agra'
    elif state == 'Uttar Pradesh - Aligarh':
        solar_generation = 'Uttar Pradesh - Aligarh'
    elif state == 'Uttar Pradesh - Ghaziabad':
        solar_generation = 'Uttar Pradesh - Ghaziabad'
    elif state == 'Uttar Pradesh - Kanpur':
        solar_generation = 'Uttar Pradesh - Kanpur'
    elif state == 'Uttar Pradesh - Lucknow':
        solar_generation = 'Uttar Pradesh - Lucknow'
    elif state == 'Uttar Pradesh - Meerut':
        solar_generation = 'Uttar Pradesh - Meerut'
    elif state == 'Uttar Pradesh - Moradabad':
        solar_generation = 'Uttar Pradesh - Moradabad'
    elif state == 'Uttar Pradesh - Varanasi':
        solar_generation = 'Uttar Pradesh - Varanasi'
    elif state == 'Uttarakhand - Dehradun':
        solar_generation = 'Uttarakhand - Dehradun'
    elif state == 'West Bengal - Asansol':
        solar_generation = 'West Bengal - Asansol'
    elif state == 'West Bengal - Kolkata':
        solar_generation = 'West Bengal - Kolkata'
    
    # Add more conditions for other states if needed
else:  # Custom demand pattern
    # Path to the sample CSV file for download
    sample_file_path = "./datasets/samplesolar.csv"
    solar_generation='customsolar'
    # Provide a downloadable sample CSV file from the specified path
    try:
        with open(sample_file_path, "rb") as file:
            st.download_button(
                label="Download Sample CSV",
                data=file,
                file_name="samplesolar.csv",
                mime='text/csv'
            )
    except FileNotFoundError:
        st.error(f"The sample file '{sample_file_path}' was not found. Please ensure it is placed in the correct directory.")

    # File uploader for custom solar generation pattern
    custom_file = st.file_uploader("Choose a CSV file", type="csv", key="loadpatterncsv")

    if custom_file:
        try:
            # Read the uploaded file into a DataFrame without header, skipping the first row
            cust_df = pd.read_csv(custom_file, header=None, skiprows=1)
            custom_df = cust_df.values


            if len(custom_df) == req_length:

                df['customsolar'] = custom_df[:, 0]  # Assuming single column data

                st.write("Custom solar generation pattern uploaded successfully.")
            else:
                st.error(f"The uploaded CSV file does not have the required rows. It has {len(custom_df)} rows but {req_length} rows are required.")
        except pd.errors.EmptyDataError:
            st.error("The uploaded file is empty. Please upload a valid CSV file.")
        except pd.errors.ParserError:
            st.error("The uploaded file is not a valid CSV. Please check the file format and content.")
        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")




vos = st.number_input("Enter the value of Lost Load:", min_value=0.0, placeholder="50")

with st.expander('Optional: Enter Feed-in Tariff'):
    use_custom_feedin = st.checkbox("Use Optional Feed-In Tariff? (yes/no)", key='optionaltariff')
    feed_in_tariff_input=st.number_input("Enter feed-in tariff rate: ", min_value=0.0, step=1.0)



# Demand Pattern Calculation

# Define column names for the load profiles

load_profile_columns = ['Constant load - 7 days a week', 'Constant load - 6 days a week', 'Constant load - 5 days a week', 'Constant load - 6 AM to 10 PM ',
 'Constant load - 6 AM to 10 PM - 6 days a week', 'Constant load - 6 AM to 10 PM - 5 days a week', 'Constant load - 9 AM to 5 PM', 'Constant load - 9 AM to 5 PM - 6 days a week', 'Constant load - 9 AM to 5 PM - 5 days a week',
 'Constant load - 6 AM to 6 PM']

st.title("Select an option:")
option = st.selectbox(
    "Choose an option:",
    ["Predefined load profiles", "Custom demand pattern"]
)

hourly_load_demand = []

def calculate_monthly_energy_consumption(monthly_consumption):
    return [monthly_consumption] * 12

if option == "Predefined load profiles":
    # Create a dictionary to map profile to index
    profile_dict = {profile: i for i, profile in enumerate(load_profile_columns, start=1)}
    # Display dropdown with profile names
    st.subheader('Select a Load Profile:')
    profile_name = st.selectbox('Choose a load profile:', load_profile_columns)

    # Get the selected profile index using the profile name
    profile_choice = profile_dict[profile_name]
    profile_choice=profile_choice-1
    # User input for monthly energy consumption
    default_consumption = st.number_input('Enter Monthly Energy Consumption (in kWh):', min_value=0.0, step=1.0)
    use_optional_energy=False


    # Hidden expander for optional detailed input
    with st.expander('Optional: Enter Detailed Monthly Energy Consumption'):
        use_optional_energy = st.checkbox("Use Optional Inputs? (yes/no)", key='optionalenergy')
        detailed_consumption = []
        for month in calendar.month_name[1:]:  # Start from January
            detailed_consumption.append(st.number_input(f'Enter {month} energy consumption (in kWh):', min_value=0.0, step=1.0))

    # Use default or detailed inputs based on user choice
    if use_optional_energy:
        monthly_energy_consumption = detailed_consumption
    else:
        monthly_energy_consumption = calculate_monthly_energy_consumption(default_consumption)
    # Initialize an empty list to store hourly load demand for the entire year
    hourly_load_demand = []
    
    # Calculate hourly load demand for each month based on selected solar input and energy consumption
    for month_index, month in enumerate(months):
        days_in_month = calendar.monthrange(2023, month_index + 1)[1]
        hours_in_month = days_in_month * 24*n
        total_load_input = df[load_profile_columns[profile_choice]].values[:hours_in_month]
        total_load_input = total_load_input / total_load_input.sum()  # Normalize the solar input
        hourly_load_for_month = total_load_input * monthly_energy_consumption[month_index]*n
        hourly_load_demand.extend(hourly_load_for_month)    
    
else:  # Predefined load profiles
    custom_load_column = 'customload'
    st.write("Upload your custom demand pattern CSV file:")
    
    # Define the path to the sample CSV file
    sample_file_path = "./datasets/sampleload.csv"

    # Provide a downloadable sample CSV file from the specified path
    try:
        with open(sample_file_path, "rb") as file:
            st.download_button(
                label="Download Sample CSV",
                data=file,
                file_name="sampleload.csv",
                mime='text/csv'
            )
    except FileNotFoundError:
        st.error(f"The sample file '{sample_file_path}' was not found. Please ensure it is placed in the correct directory.")

    # File uploader for custom demand pattern
    custom_file = st.file_uploader("Choose a CSV file", type="csv")

    if custom_file:
        try:
            # Read the uploaded file into a DataFrame without header, skipping the first row
            cust_df = pd.read_csv(custom_file, header=None, skiprows=1)
            custom_df = cust_df.values

            # Check if the uploaded DataFrame has the required number of rows
            if len(custom_df) == req_length:

                df['customload'] = custom_df[:, 0]  # Assuming single column data

                # Extract the custom load column for further processing if needed
                hourly_load_demand = df['customload'].values
            else:
                st.error(f"The uploaded CSV file does not have the required rows. It has {len(custom_df)} rows but {req_length} rows are required.")
        except pd.errors.EmptyDataError:
            st.error("The uploaded file is empty. Please upload a valid CSV file.")
        except pd.errors.ParserError:
            st.error("The uploaded file is not a valid CSV. Please check the file format and content.")
        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")

# User inputs
#b=0 # control optimization and analyze option
# Selecting option 1 or 2
stringoption = st.selectbox("Select an option:", ["Do you want to analyze and compare your system cost with existing battery size", "Do you want to optimize the battery size"])

# Handling user input based on selected option
if stringoption == "Do you want to analyze and compare your system cost with existing battery size":
    bpc_wo = st.number_input("Enter the size of the battery in kW:", min_value=0.0)
    option=1
else:
    option=2
# User input for solar system size
solar_system_size = st.number_input("Enter the size of the solar system in kW:", min_value=0.0)

charge_from_grid=False
discharge_battery=False
# Expander for optional inputs
with st.expander('Optional Inputs'):
    charge_from_grid = st.checkbox("Allow charging the battery from the grid? (yes/no)", key='charge_from_grid')
    discharge_battery = st.checkbox("Discharge battery when solar generation < load demand and no outage during peak hours? (yes/no)", key='discharge_battery')


hos = 4  # hours of storage
eff = 0.95  # efficiency value, assuming an example value
min_charge = 0.2  # minimum charge level to prevent discharge below 20%
demand_charge = 300 #INR/kWh/Month 
increment_on_peak_tariff= 0.2 # 20%
decrement_on_non_peak_tariff=0.2 # 20%
if use_custom_feedin:
    feed_in_tariff=feed_in_tariff_input
else:
    feed_in_tariff = 0   #INR/kWh

if 0 <= solar_system_size < 1:
    initial_solar_module_cost = 46293*1.12  # INR per kW the bench mark cost is with out GST, 12% GST added with that
    
if 1 <= solar_system_size < 2:
    initial_solar_module_cost = 43140*1.12

if 2 <= solar_system_size < 3:
    initial_solar_module_cost = 42020*1.12

if 3 <= solar_system_size < 10:
    initial_solar_module_cost = 40991*1.12

if 10 <= solar_system_size <= 100:
    initial_solar_module_cost = 38236*1.12

if  solar_system_size > 100:
    initial_solar_module_cost = 35886*1.12

initial_battery_cost = 25000  # INR per kWh
dg_cost = 30  # Diesel Generator cost INR/kWh

#Select metering regime
# User input for selecting the metering regime
st.markdown("## Select the metering regime:")
string_metering_option = st.selectbox("Net Metering", ["Net Metering", "Net Billing"])

if string_metering_option == "Net Metering":
    #st.write("You selected Net Metering.")
    metering_option=1
else:
    #st.write("You selected Net Billing.")
    metering_option=2

if metering_option == 1:
    metering_regime = 'net metering'
else:
    metering_regime = 'net billing'


st.markdown("## Enter financial specifications:")
num_years = st.number_input("Enter Period Of Financial Analysis(in years): ", placeholder="25", min_value=1, step=1)
discount_factor = st.number_input("Enter Discount Factor: (in percentage)", min_value=0.0, step=1.0)
discount_factor=discount_factor/100
# Yearly degradation and escalation rates
grid_carbon_factor=0.716
dg_carbon_factor=0.76
carbon_cost=0
solar_degradation_rate_yearly = 0.01  # 0.5% per year
battery_degradation_rate_yearly = 0.03  # 1% per year
demand_escalation_rate_yearly = 0.02  # 2% per year
om_cost_escalation_rate = 0.03  # 3% per year
tariff_escalation_rate_yearly = 0.01  # 2% per year
fit_tariff_escalation_rate_yearly = 0.00  # 0% per year
demand_charge_escalation_rate_yearly = 0.01  # 2% per year
dg_escalation_rate_yearly = 0.04  # 2% per year
vos_escalation_rate_yearly = 0.04  # 2% per year

#storage & Initialization of used arrays

num_hours_in_year=n*8760 # Number of hours in a year
# Initialize the charge list
charge = [1] * (num_hours_in_year * num_years + 1)



#print(hourly_load_demand[0])
#print(sum(hourly_load_demand))
#print(len(hourly_load_demand))

# Battery replacement schedule and cost
battery_replacement_schedule = [10, 20]  # Battery is replaced at year 10 and year 20
battery_costs = {0: initial_battery_cost, 10: initial_battery_cost / 2, 20: initial_battery_cost / 4}  # Cost halves every 10 years

if st.button('Submit'):
    results_solar_grid=calculate_solar_grid_costs(n, normal_tariff, extended_outage_status, df, solar_generation, vos, feed_in_tariff, hourly_load_demand, profile_choice, monthly_energy_consumption, solar_system_size, charge_from_grid, discharge_battery, hos, eff, min_charge, demand_charge, increment_on_peak_tariff, decrement_on_non_peak_tariff,  initial_solar_module_cost, initial_battery_cost, dg_cost, metering_option, metering_regime, num_years, discount_factor, grid_carbon_factor, dg_carbon_factor, carbon_cost, solar_degradation_rate_yearly, battery_degradation_rate_yearly, demand_escalation_rate_yearly, om_cost_escalation_rate, tariff_escalation_rate_yearly, fit_tariff_escalation_rate_yearly, demand_charge_escalation_rate_yearly, dg_escalation_rate_yearly, vos_escalation_rate_yearly, num_hours_in_year, charge, battery_replacement_schedule, battery_costs)
    results_grid_dg=calculate_grid_dg_costs(n, normal_tariff, extended_outage_status, df, solar_generation, vos, feed_in_tariff, hourly_load_demand, profile_choice, monthly_energy_consumption, solar_system_size, charge_from_grid, discharge_battery, hos, eff, min_charge, demand_charge, increment_on_peak_tariff, decrement_on_non_peak_tariff,  initial_solar_module_cost, initial_battery_cost, dg_cost, metering_option, metering_regime, num_years, discount_factor, grid_carbon_factor, dg_carbon_factor, carbon_cost, solar_degradation_rate_yearly, battery_degradation_rate_yearly, demand_escalation_rate_yearly, om_cost_escalation_rate, tariff_escalation_rate_yearly, fit_tariff_escalation_rate_yearly, demand_charge_escalation_rate_yearly, dg_escalation_rate_yearly, vos_escalation_rate_yearly, num_hours_in_year, charge, battery_replacement_schedule, battery_costs)
    results_solar_grid_dg=calculate_solar_grid_dg_costs(n, normal_tariff, extended_outage_status, df, solar_generation, vos, feed_in_tariff, hourly_load_demand, profile_choice, monthly_energy_consumption, solar_system_size, charge_from_grid, discharge_battery, hos, eff, min_charge, demand_charge, increment_on_peak_tariff, decrement_on_non_peak_tariff,  initial_solar_module_cost, initial_battery_cost, dg_cost, metering_option, metering_regime, num_years, discount_factor, grid_carbon_factor, dg_carbon_factor, carbon_cost, solar_degradation_rate_yearly, battery_degradation_rate_yearly, demand_escalation_rate_yearly, om_cost_escalation_rate, tariff_escalation_rate_yearly, fit_tariff_escalation_rate_yearly, demand_charge_escalation_rate_yearly, dg_escalation_rate_yearly, vos_escalation_rate_yearly, num_hours_in_year, charge, battery_replacement_schedule, battery_costs)
    if option==1:
        results_solar_grid_bess=calculate_solar_grid_bess_costs(n, normal_tariff, option, extended_outage_status, df, solar_generation, vos, feed_in_tariff, hourly_load_demand, profile_choice, monthly_energy_consumption, solar_system_size, charge_from_grid, discharge_battery, hos, eff, min_charge, demand_charge, increment_on_peak_tariff, decrement_on_non_peak_tariff,  initial_solar_module_cost, initial_battery_cost, dg_cost, metering_option, metering_regime, num_years, discount_factor, grid_carbon_factor, dg_carbon_factor, carbon_cost, solar_degradation_rate_yearly, battery_degradation_rate_yearly, demand_escalation_rate_yearly, om_cost_escalation_rate, tariff_escalation_rate_yearly, fit_tariff_escalation_rate_yearly, demand_charge_escalation_rate_yearly, dg_escalation_rate_yearly, vos_escalation_rate_yearly, num_hours_in_year, charge, battery_replacement_schedule, battery_costs, bpc_wo)
    else:
        results_solar_grid_bess=optimize_solar_grid_bess_costs(n, normal_tariff, option, extended_outage_status, df, solar_generation, vos, feed_in_tariff, hourly_load_demand, profile_choice, monthly_energy_consumption, solar_system_size, charge_from_grid, discharge_battery, hos, eff, min_charge, demand_charge, increment_on_peak_tariff, decrement_on_non_peak_tariff,initial_solar_module_cost, initial_battery_cost, dg_cost, metering_option, metering_regime, num_years, discount_factor, grid_carbon_factor, dg_carbon_factor, carbon_cost, solar_degradation_rate_yearly, battery_degradation_rate_yearly, demand_escalation_rate_yearly, om_cost_escalation_rate, tariff_escalation_rate_yearly, fit_tariff_escalation_rate_yearly, demand_charge_escalation_rate_yearly, dg_escalation_rate_yearly, vos_escalation_rate_yearly, num_hours_in_year, charge, battery_replacement_schedule, battery_costs)

    dashboard_main(results_solar_grid,results_grid_dg, results_solar_grid_dg, results_solar_grid_bess, n, option,  
    extended_outage_status, df, solar_generation,  hourly_load_demand, profile_choice, monthly_energy_consumption, solar_system_size, charge_from_grid, discharge_battery, hos, eff, min_charge, demand_charge, increment_on_peak_tariff, decrement_on_non_peak_tariff, feed_in_tariff, vos, initial_solar_module_cost, initial_battery_cost, dg_cost, metering_option, metering_regime, num_years, discount_factor, grid_carbon_factor, dg_carbon_factor, carbon_cost, solar_degradation_rate_yearly, battery_degradation_rate_yearly, demand_escalation_rate_yearly, om_cost_escalation_rate, tariff_escalation_rate_yearly, fit_tariff_escalation_rate_yearly, demand_charge_escalation_rate_yearly, dg_escalation_rate_yearly, vos_escalation_rate_yearly, num_hours_in_year, charge, battery_replacement_schedule, battery_costs)

