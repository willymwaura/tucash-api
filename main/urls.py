from django.urls import path
from . import views
from main.views import gettoken,lipanampesa


urlpatterns=[
     
     path('homepage/', views.homepage, name='homepage'),
     path('stk',gettoken.as_view()),
     path('stkpush',lipanampesa.as_view()),
     path('callback',views.mpesa_callback,name='callback'),

    
]
