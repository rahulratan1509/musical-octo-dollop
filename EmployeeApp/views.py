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

            entry.next_vt_date = next_vt_date
            entry.next_pme_date = next_pme_date

            entry.save()  # Now save the entry
            return redirect('dashboard')  # Redirect to the dashboard page
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
        else:
            next_pme_date = dob + datetime.timedelta(days=(45 - age - 3) * 365)  # PME after 3 years

    return next_vt_date, next_pme_date
