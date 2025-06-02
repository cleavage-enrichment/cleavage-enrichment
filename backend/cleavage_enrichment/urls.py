from django.urls import path 

from .views import getPlotData, getProteins, index

urlpatterns = [
    path('', index, name='index'),
    path('api/getproteins', getProteins, name='get_proteins'),
    path('api/getplotdata', getPlotData, name='get_plot_data'),
]