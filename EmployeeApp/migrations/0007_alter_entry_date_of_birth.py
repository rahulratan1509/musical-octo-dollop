# Generated by Django 5.0.1 on 2024-01-14 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EmployeeApp', '0006_alter_entry_last_pme_date_alter_entry_last_vt_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
    ]