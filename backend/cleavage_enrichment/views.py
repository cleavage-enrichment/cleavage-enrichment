import json
import math
import os
from django.http import FileResponse
from django.shortcuts import render
import pandas as pd

from backend import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from . import importing

def index(request):
    file_path = settings.STATICFILES_BASE / 'frontend' / 'index.html'
    return FileResponse(open(file_path, 'rb'), content_type='text/html')

cleavage_enrichment = importing.CleavageEnrichment()

def getProteins(request):
    """
    Search for proteins in the dataset based on a filter string.
    """

    filter = request.GET.get('filter','')
    proteins = cleavage_enrichment.getProteins(filter=filter)
        
    return JsonResponse({"proteins": proteins})

def getMetadataGroups(request):
    """
    Get metadata columns from the dataset.
    """
    
    metadata_groups = cleavage_enrichment.get_metadata_groups()
    
    return JsonResponse({"metadata_groups": metadata_groups})

@csrf_exempt
def getPlotData(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        formData = json.loads(request.body)
        print(f"Received formData: {formData}")
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({
        "data": cleavage_enrichment.get_plot_data(formData)
    })