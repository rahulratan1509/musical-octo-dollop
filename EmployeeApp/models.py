from django.db import models

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
