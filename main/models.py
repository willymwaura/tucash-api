from django.db import models
from django.utils import timezone

# Create your models here.

from django.db import models


class Balance(models.Model):
    user_id = models.IntegerField(blank=False)  # Field to store the user's ID
    amount = models.FloatField(default=0, blank=False)

    def __str__(self):
        return str(self.amount)
    
class TucashTransactions(models.Model):
    sender = models.IntegerField(blank=False) 
    receiver = models.CharField(blank=False) 
    amount = models.FloatField(blank=False)
    datetime = models.DateTimeField(auto_now_add=True,blank=False)

    def __str__(self):
        return str(self.amount)
    
class MpesaDeposits(models.Model):
    Amount=models.IntegerField(blank=False,default=0)
    PhoneNumber=models.CharField(blank=False,default=3,max_length=12)
    datetime=models.DateTimeField(blank=False,default=timezone.now)
    status=models.BooleanField(default=False)

class PaybillTranscations(models.Model):
    paybill=models.IntegerField(blank=False,default=0)
    account_number=models.CharField(blank=False,default=3)
    amount=models.IntegerField(blank=False,default=0)
    datetime=models.DateTimeField(auto_now_add=True,blank=False)
    status=models.BooleanField(default=False,blank=False)
    OriginatorConversationID=models.CharField(max_length=30,default=111,blank=False)

class TillTranscations(models.Model):
    till_number=models.IntegerField(blank=False,default=0)
    amount=models.IntegerField(blank=False,default=0)
    datetime=models.DateTimeField(auto_now_add=True,blank=False)
    status=models.BooleanField(default=False)
    OriginatorConversationID=models.CharField(max_length=30,default=111,blank=False)
