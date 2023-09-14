import random
from faker import Faker
from datetime import date, timedelta
import pandas as pd

fake = Faker()

# Define the number of entries you want to create
num_entries = 900

# Define the date range for the last PME and VT dates (last 7 years)
end_date = date.today()
start_date = end_date - timedelta(days=7 * 365)

data = []

for _ in range(num_entries):
    # Generate random data using Faker
    name = fake.name()
    employee_number = fake.unique.random_int(min=1000, max=9999)
    designation = fake.job()
    date_of_birth = fake.date_of_birth(tzinfo=None, minimum_age=20, maximum_age=65)
    
    # Generate random last PME date and last VT date within the last 7 years
    last_pme_date = fake.date_between_dates(date_start=start_date, date_end=end_date)
    last_vt_date = fake.date_between_dates(date_start=start_date, date_end=end_date)

    data.append([name, employee_number, designation, date_of_birth, last_pme_date, last_vt_date])

# Create a pandas DataFrame
df = pd.DataFrame(data, columns=["Name", "Employee Number", "Designation", "Date of Birth", "Last PME Date", "Last VT Date"])

# Save the DataFrame to an Excel file
excel_file_path = "employee_data.xlsx"
df.to_excel(excel_file_path, index=False, engine="openpyxl")

print(f"{num_entries} entries have been created and saved to {excel_file_path}.")
