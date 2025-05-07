from django.urls import path 

from .views import react

urlpatterns = [ path('', react, name='index'), ]