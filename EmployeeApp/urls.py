from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', auth_views.LoginView.as_view(), name='login'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_entry/', views.add_entry, name='add_entry'),
    path('ajax/load-areas/', views.load_areas, name='ajax_load_areas'),
    path('register/', views.registration, name='registration'),
    path('delete_entry/<int:entry_id>/', views.delete_entry, name='delete_entry'),
    path('edit_entry/<int:entry_id>/', views.edit_entry, name='edit_entry'),
    # ...
    
    path('export_entries/', views.export_entries, name='export_entries'),
    path('import_entries/', views.import_entries, name='import_entries'),
    
]
