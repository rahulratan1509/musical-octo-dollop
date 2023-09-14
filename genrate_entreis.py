import pandas as pd
from faker import Faker
from datetime import datetime, timedelta

# Create a Faker instance
fake = Faker()

# Create an empty list to store entries
entries = []

# Generate 100 entries
for _ in range(100):
    name = fake.name()
    employee_number = fake.unique.random_number()
    designation = fake.job()
    dob = fake.date_of_birth(minimum_age=22, maximum_age=60)
    last_vt_date = fake.date_between_dates(date_start=dob, date_end=datetime.now().date())
    last_pme_date = fake.date_between_dates(date_start=last_vt_date, date_end=datetime.now().date())
    
    entries.append({
        'name': name,
        'employee_number': employee_number,
        'designation': designation,
        'date_of_birth': dob,
        'last_vt_date': last_vt_date,
        'last_pme_date': last_pme_date,
    })

# Create a DataFrame from the list of entries
df = pd.DataFrame(entries)

# Export the DataFrame to an Excel file
df.to_excel('fake_entries.xlsx', index=False)
