# Helper function to convert time in "HH:MM A.M./P.M." format to slot-based format
def time_to_slot(time_str, n):
    time_parts = time_str.strip().split()
    hh_mm = time_parts[0].split(':')
    period = time_parts[1] if len(time_parts) > 1 else 'A.M.'  # Default to 'A.M.' if period is missing

    hour = int(hh_mm[0])
    minute = int(hh_mm[1])

    if period == 'P.M.' and hour != 12:
        hour += 12
    elif period == 'A.M.' and hour == 12:
        hour = 0

    total_minutes = hour * 60 + minute

    # Adjust minutes to align with the nearest slot boundary
    adjusted_minutes = total_minutes // (60 // n) * (60 // n)

    slot = adjusted_minutes // (60 // n)

    return slot

# Validate outage time blocks
def validate_time_blocks(time_blocks, n):
    try:
        max_slots = 24 * n
        for block in time_blocks:
            start, end = block.split('-')
            start_slot = time_to_slot(start, n)
            end_slot = time_to_slot(end, n)
            
            # Handle crossing midnight scenario
            if start_slot >= max_slots or end_slot >= max_slots or start_slot < 0 or end_slot < 0:
                return False
    except Exception as e:
        print(e)
        return False
    return True

# Function to generate time options based on interval
def generate_time_options(n):
    times = []
    if n == 1:  # Hourly slots
        times = [f"{hour:02d}:00 A.M." if hour < 12 else (f"{hour-12:02d}:00 P.M." if hour != 12 else "12:00 P.M.") for hour in range(24)]
    elif n == 2:  # 30 min slots
        times = [f"{hour:02d}:{minute:02d} A.M." if hour < 12 else (f"{hour-12:02d}:{minute:02d} P.M." if hour != 12 else f"12:{minute:02d} P.M.") for hour in range(24) for minute in [0, 30]]
    elif n == 4:  # 15 min slots
        times = [f"{hour:02d}:{minute:02d} A.M." if hour < 12 else (f"{hour-12:02d}:{minute:02d} P.M." if hour != 12 else f"12:{minute:02d} P.M.") for hour in range(24) for minute in [0, 15, 30, 45]]
    return times

# Function to get outage schedule
def get_outage_schedule(n):
    outage_schedule = {}
    months = ['January', 'February', 'March', 'April', 'May', 'June', 
              'July', 'August', 'September', 'October', 'November', 'December']

    frequency_choices = [
        "No outage", "Daily", "Weekly two days", "Weekly three days",
        "Once in a month", "Twice a month", "Thrice a month"
    ]

    # Get common outage frequency and time blocks
    st.write("Select common outage frequency:")
    common_frequency = st.selectbox("Outage frequency", frequency_choices)

    time_options = generate_time_options(n)
    
    common_time_blocks = []
    if common_frequency != "No outage":
        st.write("Select outage time block:")
        start_time = st.selectbox(f"Start time block ", time_options, key=f"common_start")
        end_time = st.selectbox(f"End time block", time_options, key=f"common_end")
        if start_time and end_time:
            common_time_blocks = [f"{start_time}-{end_time}"]

    # Collecting data from user for each month with default settings
    for month in months:
        outage_frequency = common_frequency
        outage_time_blocks = common_time_blocks

        if outage_frequency == "No outage":
            outage_days = []
        elif outage_frequency == "Daily":
            outage_days = list(range(1, calendar.monthrange(2023, months.index(month) + 1)[1] + 1))
        elif outage_frequency == "Weekly two days":
            outage_days = [3, 5, 10, 12, 15, 17, 22, 24]
        elif outage_frequency == "Weekly three days":
            outage_days = [1, 3, 5, 8, 10, 13, 15, 17, 19, 23, 25, 27]
        elif outage_frequency == "Once in a month":
            outage_days = [15]
        elif outage_frequency == "Twice a month":
            outage_days = [14, 27]
        elif outage_frequency == "Thrice a month":
            outage_days = [8, 17, 24]

        outage_schedule[month] = {
            'frequency': outage_frequency,
            'days': outage_days,
            'time_blocks': outage_time_blocks
        }

    # Optional Overrides for each month
    use_optional_timeblocks = st.checkbox("Use Optional Inputs? (yes/no)", key='optionaltime')
    with st.expander("Optional Inputs:"):
        for month in months:
            st.write(f"\nEnter outage details for {month}:")
            frequency_choice = st.selectbox(f"Outage frequency for {month}", frequency_choices, key=month)
            month_time_blocks = []
            if frequency_choice != "No outage":
                st.write(f"Select outage time blocks for {month}:")
                start_time = st.selectbox(f"Start time block for {month}", time_options, key=f"{month}_start")
                end_time = st.selectbox(f"End time block for {month}", time_options, key=f"{month}_end")
                if start_time and end_time:
                    month_time_blocks = [f"{start_time}-{end_time}"]

            if frequency_choice == 'Daily':
                outage_days = list(range(1, calendar.monthrange(2023, months.index(month) + 1)[1] + 1))
            elif frequency_choice == 'Weekly two days':
                outage_days = [3, 5, 10, 12, 15, 17, 22, 24]
            elif frequency_choice == 'Weekly three days':
                outage_days = [1, 3, 5, 8, 10, 13, 15, 17, 19, 23, 25, 27]
            elif frequency_choice == 'Once in a month':
                outage_days = [15]
            elif frequency_choice == 'Twice a month':
                outage_days = [14, 27]
            elif frequency_choice == 'Thrice a month':
                outage_days = [8, 17, 24]
            else:
                outage_days = []

            if use_optional_timeblocks:
                outage_schedule[month] = {
                    'frequency': frequency_choice,
                    'days': outage_days,
                    'time_blocks': month_time_blocks
                }

    return outage_schedule

## Function to define outage schedule
def generate_outage_status(outage_schedule, months, n):
    # Calculate the number of time slots per hour
    slots_per_hour = n
    total_slots = 24 * slots_per_hour

    # Initialize a list to store outage status for each time slot of the year
    yearly_outage_status = []

    # Iterate over each month in the year
    for month, data in outage_schedule.items():
        # Get outage frequency for the month
        outage_frequency = data['frequency']

        # Get outage days for the month
        outage_days = data.get('days', [])

        # Get outage time blocks for the month
        outage_time_blocks = data['time_blocks']

        # Extend yearly_outage_status with outage status for the month
        for day in range(1, calendar.monthrange(2023, months.index(month) + 1)[1] + 1):
            if day in outage_days:
                for slot in range(total_slots):
                    for block in outage_time_blocks:
                        start, end = block.split('-')
                        start_slot = time_to_slot(start, n)
                        end_slot = time_to_slot(end, n)
                        
                        # Handle crossing midnight scenario and 24-hour outage
                        if start_slot == end_slot or start_slot <= slot < end_slot or (end_slot < start_slot and (slot >= start_slot or slot < end_slot)):
                            yearly_outage_status.append(1)
                            break
                    else:
                        yearly_outage_status.append(0)
            else:
                for _ in range(total_slots):
                    yearly_outage_status.append(0)

    # Ensure that the number of slots is correct for the entire year

    expected_slots_per_year = 365 * total_slots
    yearly_outage_status = yearly_outage_status[:expected_slots_per_year]
    
    return yearly_outage_status

def calculate_month_key(index):
    if 0 <= index <= (743 *n +(n-1)):
        return 1  # January
    elif (743 *n +(n-1)) < index <= (1415 * n +(n-1)):
        return 2  # February
    elif (1415 * n+(n-1)) < index <= (2159 * n+(n-1)):
        return 3  # March
    elif (2159 * n+(n-1)) < index <= (2879 * n+(n-1)):
        return 4  # April
    elif (2879 * n+(n-1)) < index <= (3623 * n+(n-1)):
        return 5  # May
    elif (3623 * n+(n-1)) < index <= (4343 * n+(n-1)):
        return 6  # June
    elif (4343 * n+(n-1)) < index <= (5087 * n+(n-1)):
        return 7  # July
    elif (5087 * n+(n-1)) < index <= (5831 * n+(n-1)):
        return 8  # August
    elif (5831 * n+(n-1)) < index <= (6551 * n+(n-1)):
        return 9  # September
    elif (6551 * n+(n-1)) < index <= (7295 * n+(n-1)):
        return 10  # October
    elif (7295 * n+(n-1)) < index <= (8015 * n+(n-1)):
        return 11  # November
    elif (8015 * n+(n-1)) < index <= (8759 * n+(n-1)):
        return 12  # December

#Define function for net-metering calculation mechanism
def calculate_billing(units):
    banked_units = 0
    billing_units = []

    for month, unit in enumerate(units):
        if unit >= 0:
            if unit <= banked_units:
                banked_units -= unit
                billing_units.append(0)
            else:
                billing_units.append(unit - banked_units)
                banked_units = 0
        else:
            banked_units += abs(unit)
            billing_units.append(0)
        
        #print(f"Month {month+1}: Unit = {unit}, Banked = {banked_units}, Billed = {billing_units[-1]}")

    return billing_units, banked_units

# Define a function to format a number into Indian currency format
def format_indian_currency(amount):
    # Convert the amount to a string with commas for thousands separator
    formatted_amount = "{:,.0f}".format(amount)
    # Add the Indian Rupee symbol before the amount
    formatted_amount = "₹" + formatted_amount
    return formatted_amount
