# Generated by Django 4.2.4 on 2023-09-04 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EmployeeApp', '0002_alter_entry_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='last_visit_date',
            field=models.DateField(verbose_name='Last VT Date'),
        ),
    ]
