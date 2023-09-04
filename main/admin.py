from django.contrib import admin
from .models import Balance,Transactions,Mpesa

# Register your models here.
admin.site.register(Balance)
admin.site.register(Transactions)
admin.site.register(Mpesa)

