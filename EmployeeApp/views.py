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
# ...

from dateutil import parser as date_parser  # Add this import statement
from django.utils.timezone import make_aware
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from django.shortcuts import redirect
from datetime import datetime




# ...

@login_required
def import_entries(request):
    if request.method == 'POST':
        form = ImportEntriesForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            if file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)

                num_entries_created = 0

                for _, row in df.iterrows():
                    dob_str = row['Date of Birth']
                    last_vt_date_str = row['Last VT Date']
                    last_pme_date_str = row['Last PME Date']

                    date_of_birth = None if pd.isna(dob_str) else date_parser.parse(str(dob_str)).date()
                    last_vt_date = None if pd.isna(last_vt_date_str) else date_parser.parse(str(last_vt_date_str)).date()
                    last_pme_date = None if pd.isna(last_pme_date_str) else date_parser.parse(str(last_pme_date_str)).date()

                    next_vt_date, next_pme_date = calculate_next_dates(date_of_birth, last_pme_date, last_vt_date)

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

                    num_entries_created += 1

                return redirect('dashboard')
            else:
                form.add_error('file', 'Invalid file format. Please upload an Excel file.')
    else:
        form = ImportEntriesForm()

    return render(request, 'EmployeeApp/import_entries.html', {'form': form})

# ...

# Utility Functions

def calculate_age(date_of_birth):
    today = date.today()
    age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    return age

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

            if age >= 59 and age <= 60:
                next_pme_date = datetime(current_year, 8, 25).date()
    
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
        print(form.errors)
    return render(request, 'EmployeeApp/registration.html', {'form': form})

def dashboard(request):
    user = request.user
    records = Entry.objects.filter(user=user).order_by('name')

    # Calculate today's date to be used for age calculation
    today = date.today()

    # Calculate the age for each record and add it as a new attribute
    for record in records:
        record.age = calculate_age(record.date_of_birth)

    search_query = request.GET.get('search')
    if search_query:
        records = records.filter(
            Q(name__icontains=search_query) |
            Q(employee_number__icontains=search_query) |
            Q(designation__icontains=search_query)
        )

        for record in records:
            record.age = calculate_age(record.date_of_birth)

    # Calculate the count of records for the current user
    entry_count = records.count()

    paginator = Paginator(records, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'EmployeeApp/dashboard.html', {'user': user, 'records': page_obj, 'entry_count': entry_count})


def export_entries(request):
    current_user = request.user
    entries = Entry.objects.filter(user=current_user)

    data = {
        'Name': [entry.name for entry in entries],
        'Employee Number': [entry.employee_number for entry in entries],
        'Designation': [entry.designation for entry in entries],
        'Last VT Date': [entry.last_vt_date.strftime('%Y-%m-%d') if entry.last_vt_date else '' for entry in entries],
        'Age': [calculate_age(entry.date_of_birth) for entry in entries],  # Calculate age
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


from .models import Entry  # Import your Entry model

@login_required
def import_entries(request):
    if request.method == 'POST':
        form = ImportEntriesForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            if file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)

                entries_to_create = []  # Collect entries to be created

                for _, row in df.iterrows():
                    dob_str = row['Date of Birth']
                    last_vt_date_str = row['Last VT Date']
                    last_pme_date_str = row['Last PME Date']

                    date_of_birth = None if pd.isna(dob_str) else date_parser.parse(str(dob_str)).date()
                    last_vt_date = None if pd.isna(last_vt_date_str) else date_parser.parse(str(last_vt_date_str)).date()
                    last_pme_date = None if pd.isna(last_pme_date_str) else date_parser.parse(str(last_pme_date_str)).date()

                    next_vt_date, next_pme_date = calculate_next_dates(date_of_birth, last_pme_date, last_vt_date)

                    entry = Entry(
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
                    
                    entries_to_create.append(entry)  # Add the entry to the list

                Entry.objects.bulk_create(entries_to_create)  # Bulk create entries

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
    Entry.objects.filter(user=user).delete()
    messages.success(request, 'All entries have been deleted.')
    return redirect('dashboard')

def filter_entries(request):
    user = request.user
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        entries = Entry.objects.filter(user=user, next_vt_date__range=(start_date, end_date))

        for entry in entries:
            entry.age = calculate_age(entry.date_of_birth)
    else:
        entries = None

    return render(request, 'EmployeeApp/filter_entries.html', {'entries': entries, 'start_date': start_date, 'end_date': end_date})


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta, datetime
from .models import Entry

@login_required
def upcoming_vt_dates(request):
    today = date.today()
    end_of_month = today + timedelta(days=30)

    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    # Initialize with None, to be used in the template
    selected_start_date = None
    selected_end_date = None

    # Check if selected dates are in the session
    if 'selected_start_date' in request.session and 'selected_end_date' in request.session:
        selected_start_date = datetime.strptime(request.session['selected_start_date'], '%Y-%m-%d').date()
        selected_end_date = datetime.strptime(request.session['selected_end_date'], '%Y-%m-%d').date()

    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        if start_date <= end_date:
            # If start_date is less than or equal to end_date, filter by the date range
            upcoming_vt_entries = Entry.objects.filter(
                user=request.user,
                next_vt_date__gte=start_date,
                next_vt_date__lte=end_date
            ).order_by('next_vt_date')

            # Store selected dates in the session as strings
            request.session['selected_start_date'] = start_date.strftime('%Y-%m-%d')
            request.session['selected_end_date'] = end_date.strftime('%Y-%m-%d')
        else:
            # Handle invalid date range (start_date is greater than end_date)
            messages.error(request, 'Invalid date range. Start date should be less than or equal to end date.')
    else:
        # If no date range is provided, show next 30 days entries by default
        upcoming_vt_entries = Entry.objects.filter(
            user=request.user,
            next_vt_date__gte=selected_start_date or today,
            next_vt_date__lte=selected_end_date or end_of_month
        ).order_by('next_vt_date')

    # Handle marking attendance
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        attended = request.POST.get('attended')

        if entry_id and attended:
            entry = Entry.objects.get(pk=entry_id)
            entry.last_vt_date = today
            entry.save()

            entry.next_vt_date = calculate_next_vt_date(entry)
            entry.save()

            # Redirect back to the same page with the selected date range
            return redirect('upcoming_vt_dates')

    context = {
        'upcoming_vt_entries': upcoming_vt_entries,
        'start_date': selected_start_date,  # Pass selected dates to the template
        'end_date': selected_end_date,
    }

    return render(request, 'EmployeeApp/upcoming_vt_dates.html', context)

@login_required
def upcoming_pme_dates(request):
    today = date.today()
    end_of_month = today + timedelta(days=30)

    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    # Initialize with None, to be used in the template
    selected_start_date = None
    selected_end_date = None

    # Check if selected dates are in the session
    if 'selected_start_date' in request.session and 'selected_end_date' in request.session:
        selected_start_date = datetime.strptime(request.session['selected_start_date'], '%Y-%m-%d').date()
        selected_end_date = datetime.strptime(request.session['selected_end_date'], '%Y-%m-%d').date()

    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        if start_date <= end_date:
            # If start_date is less than or equal to end_date, filter by the date range
            upcoming_pme_entries = Entry.objects.filter(
                user=request.user,
                next_pme_date__gte=start_date,
                next_pme_date__lte=end_date
            ).order_by('next_pme_date')

            # Store selected dates in the session as strings
            request.session['selected_start_date'] = start_date.strftime('%Y-%m-%d')
            request.session['selected_end_date'] = end_date.strftime('%Y-%m-%d')
        else:
            # Handle invalid date range (start_date is greater than end_date)
            messages.error(request, 'Invalid date range. Start date should be less than or equal to end date.')
    else:
        # If no date range is provided, show next 30 days entries by default
        upcoming_pme_entries = Entry.objects.filter(
            user=request.user,
            next_pme_date__gte=selected_start_date or today,
            next_pme_date__lte=selected_end_date or end_of_month
        ).order_by('next_pme_date')

    # Handle marking attendance
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        attended = request.POST.get('attended')

        if entry_id and attended:
            entry = Entry.objects.get(pk=entry_id)
            entry.last_pme_date = today
            entry.save()

            entry.next_pme_date = calculate_next_pme_date(entry)
            entry.save()

            # Redirect back to the same page with the selected date range
            return redirect('upcoming_pme_dates')

    context = {
        'upcoming_pme_entries': upcoming_pme_entries,
        'start_date': selected_start_date,  # Pass selected dates to the template
        'end_date': selected_end_date,
    }

    return render(request, 'EmployeeApp/upcoming_pme_dates.html', context)

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
                next_vt_date = entry.last_vt_date + timedelta(days=5 * 365)

    return next_vt_date

def calculate_next_pme_date(entry):
    current_year = datetime.now().year
    dob_year = entry.date_of_birth.year
    age = current_year - dob_year
    retirement_age = 60
    next_pme_date = None

    if age < retirement_age:
        if entry.last_pme_date:
            if age <= 45:
                next_pme_date = entry.last_pme_date + timedelta(days=5 * 365)
            elif age > 45 and age < 59:
                next_pme_date = entry.last_pme_date + timedelta(days=3 * 365)

            if age >= 59 and age <= 60:
                next_pme_date = datetime(current_year, 8, 25).date()

    return next_pme_date


