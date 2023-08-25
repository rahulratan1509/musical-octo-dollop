from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Area

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
    return render(request, 'EmployeeApp/dashboard.html', {'user': user})
