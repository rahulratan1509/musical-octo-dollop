# Generated by Django 4.2.4 on 2023-09-04 15:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('EmployeeApp', '0003_alter_entry_last_visit_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entry',
            old_name='last_visit_date',
            new_name='last_vt_date',
        ),
    ]