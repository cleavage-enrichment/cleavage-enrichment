from django.urls import path 

from .views import getGroups, getPlotData, getProteins, getSamples, index

urlpatterns = [
    path('', index, name='index'),
    path('api/getproteins', getProteins, name='get_proteins'),
    path('api/getgroups', getGroups, name='get_groups'),
    path('api/getsamples', getSamples, name='get_samples'),
    path('api/getplotdata', getPlotData, name='get_plot_data'),
]