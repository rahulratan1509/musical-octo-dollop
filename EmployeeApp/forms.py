from django import forms
from .models import Entry

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['name', 'employee_number', 'designation', 'last_pme_date', 'last_vt_date', 'date_of_birth']




class ImportEntriesForm(forms.Form):
    file = forms.FileField()