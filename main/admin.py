from django.contrib import admin
from .models import Balance,TucashTransactions,MpesaDeposits,TillTranscations,PaybillTranscations

# Register your models here.
admin.site.register(Balance)
admin.site.register(TucashTransactions)
admin.site.register(MpesaDeposits)
admin.site.register(TillTranscations)
admin.site.register(PaybillTranscations)

