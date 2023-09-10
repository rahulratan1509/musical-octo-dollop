from datetime import datetime, timedelta
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

def calculate_next_dates(dob, last_pme_date, last_vt_date):
    current_year = datetime.now().year
    dob_year = dob.year
    age = current_year - dob_year
    retirement_age = 60
    next_vt_date = None
    next_pme_date = None

    if age < retirement_age:
        if last_vt_date:
            next_vt_date = last_vt_date + timedelta(days=5 * 365)  # VT every 5 years
        else:
            next_vt_date = dob + timedelta(days=365)  # VT after 1 year

        if age <= 45 and last_pme_date:
            next_pme_date = last_pme_date + timedelta(days=5 * 365)  # PME every 5 years
        elif last_pme_date:
            next_pme_date = last_pme_date + timedelta(days=3 * 365)  # PME every 3 years

        if age + 1 == 59 and current_year == 2023:
            next_vt_date = datetime(2023, 6, 15).date()  # Set VT and PME dates for 2023 (adjust as needed)
            next_pme_date = datetime(2023, 8, 25).date()

        if age == 59 and current_year == 2024:
            next_vt_date = datetime(2024, 7, 10).date()  # Set VT and PME dates for 2024 (adjust as needed)
            next_pme_date = datetime(2024, 9, 20).date()

    return next_vt_date, next_pme_date

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
    }

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=employee_entries.xlsx'

    df.to_excel(response, index=False)

    return response

from django.http import JsonResponse

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
                    date_of_birth = row.get('Date of Birth')
                    last_vt_date_str = row.get('Last VT Date')
                    last_pme_date_str = row.get('Last PME Date')

                    if not pd.isna(date_of_birth):
                        date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
                    else:
                        date_of_birth = None

                    if last_vt_date_str:
                        last_vt_date = datetime.strptime(last_vt_date_str, '%Y-%m-%d').date()
                    else:
                        last_vt_date = None

                    if last_pme_date_str:
                        last_pme_date = datetime.strptime(last_pme_date_str, '%Y-%m-%d').date()
                    else:
                        last_pme_date = None

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
from django.contrib import messages
from django.shortcuts import redirect

@login_required
def flush_entries(request):
    user = request.user

    # Delete all entries associated with the user
    Entry.objects.filter(user=user).delete()

    # Optionally, you can add a success message
    messages.success(request, 'All entries have been deleted.')

    return redirect('dashboard')

