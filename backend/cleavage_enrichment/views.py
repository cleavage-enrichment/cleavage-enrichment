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

def getGroups(request):
    """
    Get unique groups from the metadata.
    """
    
    groups = cleavage_enrichment.getGroups()
    
    return JsonResponse({"groups": groups})

def getSamples(request):
    """
    Get unique samples from the metadata.
    """
    
    samples = cleavage_enrichment.getSamples()
    
    return JsonResponse({"samples": samples})


@csrf_exempt
def getPlotData(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        formData = json.loads(request.body)
        proteins = formData.get("proteins", [])
        groups = formData.get("groups", None)
        samples = formData.get("samples", None)
        grouping_method = formData.get("grouping_method", "mean")
        print(formData)
        print((grouping_method))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({
        "data": cleavage_enrichment.get_plot_data(proteins, groups, samples, grouping_method)
    })

    


