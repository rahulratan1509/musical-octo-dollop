from django import forms
from .models import Entry

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['name', 'employee_number', 'designation', 'last_visit_date', 'last_pme_date', 'date_of_birth']
