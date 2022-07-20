from datetime import datetime
from unicodedata import category
from django.db import models
from django.utils import timezone

# Create your models here.

class Employee(models.Model):
    Full_Name = models.TextField(null=True) 
    Address = models.TextField(blank=True,null= True) 
    Contact = models.TextField(null=True) 
    Joined_Date = models.DateField(blank=True,null= True) 
    Gender = models.TextField(null=True) 
    Salary = models.IntegerField(null=True)
    Role = models.TextField(null=True)
    def __str__(self):
        return self.Full_Name

class Category(models.Model):
    name = models.TextField()
    description = models.TextField()
    status = models.IntegerField(default=1) 
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.name

class Products(models.Model):
    code = models.CharField(max_length=100)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.TextField()
    description = models.TextField()
    price = models.FloatField(default=0)
    status = models.IntegerField(default=1) 
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.code + " - " + self.name

class Sales(models.Model):
    code = models.CharField(max_length=100)
    sub_total = models.FloatField(default=0)
    grand_total = models.FloatField(default=0)
    tax_amount = models.FloatField(default=0)
    tax = models.FloatField(default=0)
    tendered_amount = models.FloatField(default=0)
    amount_change = models.FloatField(default=0)
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.code

class salesItems(models.Model):
    sale_id = models.ForeignKey(Sales,on_delete=models.CASCADE)
    product_id = models.ForeignKey(Products,on_delete=models.CASCADE)
    price = models.FloatField(default=0)
    qty = models.FloatField(default=0)
    total = models.FloatField(default=0)

class Payroll(models.Model):
    Empid = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, null=True)
    From_Date = models.DateField(blank=True,null= True)
    To_Date = models.DateField(blank=True,null= True)
    Paid_Date = models.DateField(blank=True,null= True)
    Amount = models.FloatField(null=True)
    Payment_Method = models.TextField(null=True)
    Remarks=models.TextField(null=True)
    def __str__(self):
        return str(self.Empid.Full_Name)


class Payments(models.Model):
    Empid = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, null=True)
    From_Date = models.DateField(blank=True,null= True)
    To_Date = models.DateField(blank=True,null= True)
    Paid_Date = models.DateField(blank=True,null= True)
    Amount = models.FloatField(null=True)
    Payment_Method = models.TextField(null=True)
    Remarks=models.TextField(null=True)
    def __str__(self):
        return str(self.Empid.Full_Name)
    
    
