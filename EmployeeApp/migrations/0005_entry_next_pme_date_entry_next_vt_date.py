# Generated by Django 4.2.4 on 2023-09-04 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EmployeeApp', '0004_rename_last_visit_date_entry_last_vt_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='next_pme_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='entry',
            name='next_vt_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]