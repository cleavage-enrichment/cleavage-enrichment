from django.urls import path 

from .views import metadata_view, proteins_view, index, plot_view, upload_view

urlpatterns = [
    path('', index, name='index'),
    path('api/upload/', upload_view, name='upload'),
    path('api/getproteins', proteins_view, name='get_proteins'),
    path("api/getmetadatagroups", metadata_view, name="get_metadata_groups"),
    path('api/plot', plot_view, name='plot_view'),
]