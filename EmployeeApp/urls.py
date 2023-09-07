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
    path('edit_all_entries/', views.edit_all_entries, name='edit_all_entries'),
    path('save_all_entries/', views.save_all_entries, name='save_all_entries'),

]
