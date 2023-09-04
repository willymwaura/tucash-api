from django.db import models
from datetime import datetime

from pytz import timezone

# Create your models here.

from django.db import models


class Balance(models.Model):
    user_id = models.IntegerField(blank=False)  # Field to store the user's ID
    amount = models.FloatField(default=0, blank=False)

    def __str__(self):
        return str(self.amount)
    
class Transactions(models.Model):
    sender = models.IntegerField(blank=False) 
    receiver = models.CharField(blank=False) 
    amount = models.FloatField(blank=False)
    datetime = models.DateTimeField(auto_now_add=True,blank=False)

    def __str__(self):
        return str(self.amount)
    
class Mpesa(models.Model):
    Amount=models.IntegerField(blank=False,default=0)
    PhoneNumber=models.CharField(blank=False,default=3,max_length=12)
