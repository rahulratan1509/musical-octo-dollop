from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Branch(models.Model):
    name = models.CharField(max_length=100)

class Area(models.Model):
    name = models.CharField(max_length=100)

class Subsidiary(models.Model):
    name = models.CharField(max_length=100)

class Colliery(models.Model):
    name = models.CharField(max_length=100)

class Employee(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    subsidiary = models.ForeignKey(Subsidiary, on_delete=models.CASCADE)
    colliery = models.ForeignKey(Colliery, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=100)

class Entry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    employee_number = models.CharField(max_length=10)
    designation = models.CharField(max_length=50)
    last_vt_date = models.DateField(verbose_name='Last VT Date', null=True, blank=True)  # Make it optional
    last_pme_date = models.DateField(null=True, blank=True)  # Make it optional
    date_of_birth = models.DateField(null=True, blank=True)
    next_vt_date = models.DateField(null=True, blank=True)
    next_pme_date = models.DateField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)  # Set default value here
