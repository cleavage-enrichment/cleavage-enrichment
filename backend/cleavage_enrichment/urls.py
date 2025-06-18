from django.urls import path 

from .views import getBatches, getGroups, getPlotData, getProteins, getSamples, index

urlpatterns = [
    path('', index, name='index'),
    path('api/getproteins', getProteins, name='get_proteins'),
    path('api/getgroups', getGroups, name='get_groups'),
    path('api/getsamples', getSamples, name='get_samples'),
    path('api/getbatches', getBatches, name='get_batches'),
    path('api/getplotdata', getPlotData, name='get_plot_data'),
]