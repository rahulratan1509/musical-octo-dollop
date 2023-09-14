from datetime import datetime, timedelta, date
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from .models import Area, Entry
from .forms import EntryForm, ImportEntriesForm
from django.contrib import messages

# Utility Functions
def calculate_age(date_of_birth):
    today = date.today()
    age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    return age

from datetime import datetime, timedelta

def calculate_next_dates(dob, last_pme_date, last_vt_date):
    current_year = datetime.now().year
    dob_year = dob.year
    age = current_year - dob_year
    retirement_age = 60
    next_vt_date = None
    next_pme_date = None

    if age < retirement_age:
        if last_vt_date:
            if age >= 59 and age <= 60:
                next_vt_date = datetime(current_year, 6, 15).date()
            else:
                next_vt_date = last_vt_date + timedelta(days=5 * 365)  # VT every 5 years
        else:
            next_vt_date = None

        if last_pme_date:
            if age <= 45:
                next_pme_date = last_pme_date + timedelta(days=5 * 365)  # PME every 5 years
            elif age > 45 and age < 59:
                next_pme_date = last_pme_date + timedelta(days=3 * 365)  # PME every 3 years

            # Handle the case for ages 59-60
            if age >= 59 and age <= 60:
                next_pme_date = datetime(current_year, 8, 25).date()

    # # Mark as "Retired" if the person is retired
    # if age >= retirement_age:
    #     next_vt_date = "Retired"
    #     next_pme_date = "Retired"
    
    return next_vt_date, next_pme_date


# Views

@login_required
def edit_entry(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)
    if request.method == 'POST':
        form = EntryForm(request.POST, instance=entry)
        if form.is_valid():
            entry = form.save(commit=False)

            next_vt_date, next_pme_date = calculate_next_dates(
                entry.date_of_birth,
                entry.last_pme_date,
                entry.last_vt_date
            )

            entry.last_vt_date = next_vt_date if not entry.last_vt_date else entry.last_vt_date
            entry.last_pme_date = next_pme_date if not entry.last_pme_date else entry.last_pme_date
            entry.next_vt_date = next_vt_date
            entry.next_pme_date = next_pme_date

            entry.save()
            return redirect('dashboard')
    else:
        form = EntryForm(instance=entry)

    return render(request, 'EmployeeApp/edit_entry.html', {'form': form, 'entry': entry})

@login_required
def add_entry(request):
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user

            next_vt_date, next_pme_date = calculate_next_dates(
                entry.date_of_birth,
                entry.last_pme_date,
                entry.last_vt_date
            )

            entry.last_vt_date = next_pme_date if not entry.last_vt_date else entry.last_vt_date
            entry.last_pme_date = next_vt_date if not entry.last_pme_date else entry.last_pme_date
            entry.next_vt_date = next_vt_date
            entry.next_pme_date = next_pme_date

            entry.save()
            return redirect('dashboard')
        else:
            print("Form is not valid. Errors:")
            print(form.errors)
    else:
        form = EntryForm()

    return render(request, 'EmployeeApp/add_entry.html', {'form': form})

def load_areas(request):
    branch_id = request.GET.get('branch')
    areas = Area.objects.filter(branch_id=branch_id).values_list('name', flat=True)
    return JsonResponse({'areas': list(areas)})

def registration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'EmployeeApp/registration.html', {'form': form})

def dashboard(request):
    user = request.user
    records = Entry.objects.filter(user=user).order_by('name')

    search_query = request.GET.get('search')
    if search_query:
        records = records.filter(
            Q(name__icontains=search_query) |
            Q(employee_number__icontains=search_query) |
            Q(designation__icontains=search_query)
        )

    paginator = Paginator(records, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'EmployeeApp/dashboard.html', {'user': user, 'records': page_obj})

def export_entries(request):
    current_user = request.user
    entries = Entry.objects.filter(user=current_user)

    data = {
        'Name': [entry.name for entry in entries],
        'Employee Number': [entry.employee_number for entry in entries],
        'Designation': [entry.designation for entry in entries],
        'Last VT Date': [entry.last_vt_date.strftime('%Y-%m-%d') if entry.last_vt_date else '' for entry in entries],
        'Last PME Date': [entry.last_pme_date.strftime('%Y-%m-%d') if entry.last_pme_date else '' for entry in entries],
        'Next VT Date': [entry.next_vt_date.strftime('%Y-%m-%d') if entry.next_vt_date else '' for entry in entries],
        'Next PME Date': [entry.next_pme_date.strftime('%Y-%m-%d') if entry.next_pme_date else '' for entry in entries],
        'Date of Birth': [entry.date_of_birth.strftime('%Y-%m-%d') if entry.date_of_birth else '' for entry in entries],
    }

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=employee_entries.xlsx'

    df.to_excel(response, index=False)

    return response

from datetime import datetime
import pandas as pd

# ...

from dateutil import parser as date_parser

# ...
@login_required
def import_entries(request):
    if request.method == 'POST':
        form = ImportEntriesForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            if file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)

                # Initialize the counter for entries created
                num_entries_created = 0

                for _, row in df.iterrows():
                    dob_str = row['Date of Birth']
                    last_vt_date_str = row['Last VT Date']
                    last_pme_date_str = row['Last PME Date']

                    # Parse dates using dateutil.parser.parse
                    date_of_birth = None if pd.isna(dob_str) else date_parser.parse(str(dob_str)).date()
                    last_vt_date = None if pd.isna(last_vt_date_str) else date_parser.parse(str(last_vt_date_str)).date()
                    last_pme_date = None if pd.isna(last_pme_date_str) else date_parser.parse(str(last_pme_date_str)).date()

                    next_vt_date, next_pme_date = calculate_next_dates(date_of_birth, last_pme_date, last_vt_date)

                    # Create the entry
                    Entry.objects.create(
                        user=request.user,
                        name=row['Name'],
                        employee_number=row['Employee Number'],
                        date_of_birth=date_of_birth,
                        last_vt_date=last_vt_date,
                        last_pme_date=last_pme_date,
                        next_vt_date=next_vt_date,
                        next_pme_date=next_pme_date,
                        designation=row['Designation'],
                    )

                    # Increment the counter for entries created
                    num_entries_created += 1

                # Return the number of entries created in the JSON response
                return redirect('dashboard')
            else:
                form.add_error('file', 'Invalid file format. Please upload an Excel file.')
    else:
        form = ImportEntriesForm()

    return render(request, 'EmployeeApp/import_entries.html', {'form': form})


def delete_entry(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)
    if request.method == 'POST':
        entry.delete()
        return redirect('dashboard')
    return render(request, 'EmployeeApp/delete_entry.html', {'entry': entry})

@login_required
def flush_entries(request):
    user = request.user

    # Delete all entries associated with the user
    Entry.objects.filter(user=user).delete()

    # Optionally, you can add a success message
    messages.success(request, 'All entries have been deleted.')

    return redirect('dashboard')

def filter_entries(request):
    user = request.user  # Get the current user
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    if start_date and end_date:
        # Convert start_date and end_date to date objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Filter entries by the current user and date range
        entries = Entry.objects.filter(user=user, next_vt_date__range=(start_date, end_date))

        # Calculate age for each entry
        for entry in entries:
            entry.age = calculate_age(entry.date_of_birth)
    else:
        # If no date range is selected, set entries to None
        entries = None

    return render(request, 'EmployeeApp/filter_entries.html', {'entries': entries, 'start_date': start_date, 'end_date': end_date})

# In your views.py

from datetime import date, timedelta, datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Entry

@login_required
def upcoming_vt_dates(request):
    today = date.today()
    end_of_month = today + timedelta(days=30)  # Assuming each month has 30 days

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if start_date and end_date:
            start_date = date.fromisoformat(start_date)
            end_date = date.fromisoformat(end_date)

            # Filter entries where next VT date is within the selected date range
            upcoming_vt_entries = Entry.objects.filter(
                user=request.user,
                next_vt_date__gte=start_date,
                next_vt_date__lte=end_date
            ).order_by('next_vt_date')
        else:
            # If no date range is selected, show all upcoming VT dates for the current month
            upcoming_vt_entries = Entry.objects.filter(
                user=request.user,
                next_vt_date__gte=today,
                next_vt_date__lte=end_of_month
            ).order_by('next_vt_date')
    else:
        # Show all upcoming VT dates for the current month by default
        upcoming_vt_entries = Entry.objects.filter(
            user=request.user,
            next_vt_date__gte=today,
            next_vt_date__lte=end_of_month
        ).order_by('next_vt_date')

    context = {
        'upcoming_vt_entries': upcoming_vt_entries,
    }

    return render(request, 'EmployeeApp/upcoming_vt_dates.html', context)

@login_required
def upcoming_pme_dates(request):
    today = date.today()
    end_of_month = today + timedelta(days=30)  # Assuming each month has 30 days

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if start_date and end_date:
            start_date = date.fromisoformat(start_date)
            end_date = date.fromisoformat(end_date)

            # Filter entries where next PME date is within the selected date range
            upcoming_pme_entries = Entry.objects.filter(
                user=request.user,
                next_pme_date__gte=start_date,
                next_pme_date__lte=end_date
            ).order_by('next_pme_date')
        else:
            # If no date range is selected, show all upcoming PME dates for the current month
            upcoming_pme_entries = Entry.objects.filter(
                user=request.user,
                next_pme_date__gte=today,
                next_pme_date__lte=end_of_month
            ).order_by('next_pme_date')
    else:
        # Show all upcoming PME dates for the current month by default
        upcoming_pme_entries = Entry.objects.filter(
            user=request.user,
            next_pme_date__gte=today,
            next_pme_date__lte=end_of_month
        ).order_by('next_pme_date')

    context = {
        'upcoming_pme_entries': upcoming_pme_entries,
    }

    return render(request, 'EmployeeApp/upcoming_pme_dates.html', context)

# ...

# Define a function to calculate the next VT date
def calculate_next_vt_date(entry):
    current_year = datetime.now().year
    dob_year = entry.date_of_birth.year
    age = current_year - dob_year
    retirement_age = 60
    next_vt_date = None

    if age < retirement_age:
        if entry.last_vt_date:
            if age >= 59 and age <= 60:
                next_vt_date = datetime(current_year, 6, 15).date()
            else:
                next_vt_date = entry.last_vt_date + timedelta(days=5 * 365)  # VT every 5 years

    return next_vt_date

# Define a function to calculate the next PME date
def calculate_next_pme_date(entry):
    current_year = datetime.now().year
    dob_year = entry.date_of_birth.year
    age = current_year - dob_year
    retirement_age = 60
    next_pme_date = None

    if age < retirement_age:
        if entry.last_pme_date:
            if age <= 45:
                next_pme_date = entry.last_pme_date + timedelta(days=5 * 365)  # PME every 5 years
            elif age > 45 and age < 59:
                next_pme_date = entry.last_pme_date + timedelta(days=3 * 365)  # PME every 3 years

            # Handle the case for ages 59-60
            if age >= 59 and age <= 60:
                next_pme_date = datetime(current_year, 8, 25).date()

    return next_pme_date
