from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import JsonResponse
from .models import Area, Entry
from .forms import EntryForm
from django.core.paginator import Paginator
import datetime

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

from django.db.models import Q

@login_required
def dashboard(request):
    user = request.user
    records = Entry.objects.filter(user=user).order_by('name')

    search_query = request.GET.get('search')
    if search_query:
        records = records.filter(
            Q(name__icontains=search_query) |
            Q(employee_number__icontains=search_query)
        )
    if request.method == 'POST':
        if 'edit_all' in request.POST:
            # Mark entries as editable
            for record in records:
                record.editable = True
        elif 'save_all' in request.POST:
            # Save changes for editable entries
            for record in records:
                if record.editable:
                    form_data = request.POST.dict()
                    field_name = f'name_{record.id}'
                    if field_name in form_data:
                        new_name = form_data[field_name]
                        record.name = new_name
                        record.editable = False  # Turn off edit mode
                        record.save()  # Update the record

    paginator = Paginator(records, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'EmployeeApp/dashboard.html', {'user': user, 'records': page_obj})

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

            if not entry.last_vt_date and next_pme_date:
                entry.last_vt_date = next_pme_date

            if not entry.last_pme_date and next_vt_date:
                entry.last_pme_date = next_vt_date

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

def calculate_next_dates(dob, last_pme_date, last_vt_date):
    current_year = datetime.datetime.now().year
    dob_year = dob.year

    age = current_year - dob_year
    retirement_age = 60
    next_vt_date = None
    next_pme_date = None

    if age < retirement_age:
        if last_vt_date:
            next_vt_date = last_vt_date + datetime.timedelta(days=5 * 365)
        else:
            next_vt_date = dob + datetime.timedelta(days=365)

        if age <= 45 and last_pme_date:
            next_pme_date = last_pme_date + datetime.timedelta(days=5 * 365)
        elif last_pme_date:
            next_pme_date = last_pme_date + datetime.timedelta(days=3 * 365)
        elif not last_pme_date:
            next_pme_date = None

        if not last_vt_date:
            next_vt_date = None

        if age + 1 == 59 and current_year == 2023:
            next_vt_date = datetime.date(2023, 6, 15)
            next_pme_date = datetime.date(2023, 8, 25)

        if age == 59 and current_year == 2024:
            next_vt_date = datetime.date(2024, 7, 10)
            next_pme_date = datetime.date(2024, 9, 20)

    return next_vt_date, next_pme_date

@login_required
def edit_all_entries(request):
    entries = Entry.objects.filter(user=request.user)
    for entry in entries:
        entry.editable = True
        entry.save()
    return redirect('dashboard')

@login_required
def save_all_entries(request):
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('name_'):
                entry_id = int(key.split('_')[1])
                entry = Entry.objects.get(id=entry_id)
                entry.name = value
                entry.editable = False
                entry.save()  # Save the changes to the entry

        # Turn off edit mode for all entries for the current user
        entries = Entry.objects.filter(user=request.user)
        for entry in entries:
            entry.editable = False
            entry.save()

    return redirect('dashboard')


