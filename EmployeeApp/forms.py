from django import forms
from .models import Entry

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['name', 'designation', 'employee_number', 'date_of_birth', 'last_pme_date', 'last_vt_date']
 
    def __init__(self, *args, **kwargs):
        super(EntryForm, self).__init__(*args, **kwargs)
        self.fields['last_pme_date'].required = False
        self.fields['last_vt_date'].required = False