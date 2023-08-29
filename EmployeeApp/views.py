from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import JsonResponse
from .models import Area, Entry
from .forms import EntryForm

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
    return render(request, 'EmployeeApp/dashboard.html', {'user': user, 'records': records})

@login_required
def add_entry(request):
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)  # Create an entry instance but don't save it yet
            entry.user = request.user  # Associate the entry with the logged-in user
            entry.save()  # Now save the entry
            return redirect('dashboard')  # Redirect to the dashboard page
    else:
        form = EntryForm()
    return render(request, 'EmployeeApp/add_entry.html', {'form': form})
