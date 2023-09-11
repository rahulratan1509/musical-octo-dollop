import pandas as pd
import random
from datetime import datetime, timedelta

# Define the number of test entries you want to generate
num_entries = 100

# Create empty lists to store data
names = []
employee_numbers = []
date_of_births = []
last_vt_dates = []
last_pme_dates = []
designations = []

# Generate random test data for entries
for _ in range(num_entries):
    names.append(f"Employee_{random.randint(100, 999)}")
    employee_numbers.append(random.randint(1000, 9999))
    
    # Generate a random date of birth between 1970 and 2000
    date_of_birth = datetime(random.randint(1970, 2000), random.randint(1, 12), random.randint(1, 28))
    date_of_births.append(date_of_birth.strftime('%Y-%m-%d'))
    
    # Generate a random last VT date and last PME date
    last_vt_date = date_of_birth + timedelta(days=random.randint(365, 365 * 10))
    last_pme_date = date_of_birth + timedelta(days=random.randint(365, 365 * 10))
    last_vt_dates.append(last_vt_date.strftime('%Y-%m-%d'))
    last_pme_dates.append(last_pme_date.strftime('%Y-%m-%d'))
    
    designations.append(f"Designation_{random.randint(1, 5)}")

# Create a DataFrame to store the test data
data = {
    'Name': names,
    'Employee Number': employee_numbers,
    'Date of Birth': date_of_births,
    'Last VT Date': last_vt_dates,
    'Last PME Date': last_pme_dates,
    'Designation': designations,
}

df = pd.DataFrame(data)

# Save the DataFrame to an Excel file
df.to_excel('test_entries_100.xlsx', index=False)
print("Test entries saved to 'test_entries_100.xlsx'")
