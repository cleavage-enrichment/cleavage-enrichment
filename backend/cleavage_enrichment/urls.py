from django.urls import path 

from .views import getMetadataGroups, getPlotData, getProteins, index, plot_view, upload, upload_progress

urlpatterns = [
    path('', index, name='index'),
    path('api/upload/', upload, name='upload'),
    path('api/upload_progress/<str:upload_id>/', upload_progress, name='upload_progress'),
    path('api/getproteins', getProteins, name='get_proteins'),
    path('api/getplotdata', getPlotData, name='get_plot_data'),
    path("api/getmetadatagroups", getMetadataGroups, name="get_metadata_groups"),
    path('api/plot', plot_view, name='plot_view'),
]