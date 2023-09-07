from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import JsonResponse
from .models import Area, Entry
from .forms import EntryForm
from django.core.paginator import Paginator
import datetime  # Import datetime module

def load_areas(request):
    branch_id = request.GET.get('branch')
    areas = Area.objects.filter(branch_id=branch_id).values_list('name', flat=True)
    return JsonResponse({'areas': list(areas)})

def registration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'EmployeeApp/registration.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    records = Entry.objects.filter(user=user)  # Only get records associated with the logged-in user

    # Configure pagination
    paginator = Paginator(records, 10)  # Display 10 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'EmployeeApp/dashboard.html', {'user': user, 'records': page_obj})

@login_required
def add_entry(request):
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)  # Create an entry instance but don't save it yet

            entry.user = request.user  # Associate the entry with the logged-in user

            # Calculate next PME and VT dates
            next_vt_date, next_pme_date = calculate_next_dates(
                entry.date_of_birth,
                entry.last_pme_date,
                entry.last_vt_date
            )

            # Check if last_vt_date is blank and use the value from last_pme_date if available
            if not entry.last_vt_date and next_pme_date:
                entry.last_vt_date = next_pme_date

            # Check if last_pme_date is blank and use the value from last_vt_date if available
            if not entry.last_pme_date and next_vt_date:
                entry.last_pme_date = next_vt_date

            entry.next_vt_date = next_vt_date
            entry.next_pme_date = next_pme_date

            entry.save()  # Now save the entry

            # Debugging messages
            print("Entry saved successfully.")
            print(f"next_vt_date: {next_vt_date}")
            print(f"next_pme_date: {next_pme_date}")

            return redirect('dashboard')  # Redirect to the dashboard page
        else:
            # Debugging message for form validation errors
            print("Form is not valid. Errors:")
            print(form.errors)
    else:
        form = EntryForm()

    return render(request, 'EmployeeApp/add_entry.html', {'form': form})


def calculate_next_dates(dob, last_pme_date, last_vt_date):
    current_year = datetime.datetime.now().year
    dob_year = dob.year

    age = current_year - dob_year
    retirement_age = 60
    next_vt_date = None
    next_pme_date = None

    if age < retirement_age:
        if last_vt_date:
            next_vt_date = last_vt_date + datetime.timedelta(days=5 * 365)  # VT every 5 years
        else:
            next_vt_date = dob + datetime.timedelta(days=365)  # VT after 1 year

        if age <= 45 and last_pme_date:
            next_pme_date = last_pme_date + datetime.timedelta(days=5 * 365)  # PME every 5 years
        elif last_pme_date:
            next_pme_date = last_pme_date + datetime.timedelta(days=3 * 365)  # PME every 3 years
        elif not last_pme_date:  # Handle the case where last_pme_date is not provided
            next_pme_date = None  # Set to None if not provided

        # Handle the case where last_vt_date is not provided
        if not last_vt_date:
            next_vt_date = None  # Set to None if not provided

        # Check if the person will turn 59 in the next year (2024)
        if age + 1 == 59 and current_year == 2023:
            # Set VT and PME dates for 2023 (random date and month)
            next_vt_date = datetime.date(2023, 6, 15)  # Change to your preferred date
            next_pme_date = datetime.date(2023, 8, 25)  # Change to your preferred date

        # Check if the person is 59 years old and it's 2024
        if age == 59 and current_year == 2024:
            # Set VT and PME dates for 2024 (random date and month)
            next_vt_date = datetime.date(2024, 7, 10)  # Change to your preferred date
            next_pme_date = datetime.date(2024, 9, 20)  # Change to your preferred date

    return next_vt_date, next_pme_date

