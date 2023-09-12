from django.urls import path

from . views import Homepage
from main.views import Homepage,gettoken,lipanampesa,UpdateBalanceAPIView ,GetBalanceAPIView,MpesaCallback



urlpatterns=[
  
   
     
     path('homepage/', Homepage.as_view(), name='homepage'),
     path('stk',gettoken.as_view()),
     path('stkpush',lipanampesa.as_view()),
     path('callback/', MpesaCallback.as_view(), name='mpesa-callback'),
     path('get_balance/<int:user_id>/', GetBalanceAPIView.as_view(), name='get_balance_api'),
     path('transact', UpdateBalanceAPIView.as_view(), name='update_balance_api'),  
]

