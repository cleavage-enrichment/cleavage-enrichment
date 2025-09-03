import json
import logging
import traceback
import pandas as pd
import plotly.io as pio
from django_server import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse, JsonResponse
from utils.logging import InMemoryLogHandler, with_logging

from cleavviz.data import get_metadata_groups, get_plot, getProteins, read_data, read_fasta, read_metadata, read_peptides

from cleavviz.cleavage_calculation.cleavage_enrichment_analysis import CleavageEnrichmentAnalysis

def index(request):
    file_path = settings.STATICFILES_BASE / 'frontend' / 'index.html'
    return FileResponse(open(file_path, 'rb'), content_type='text/html')

peptides: pd.DataFrame = None
metadata: pd.DataFrame = None
fastadata: pd.DataFrame = None

enrichment_analysis: CleavageEnrichmentAnalysis = CleavageEnrichmentAnalysis()

@csrf_exempt
@with_logging
def upload_view(request, logger):
    """
    Handle file upload and process the data.
    """
    if request.method != 'POST':
        raise ValueError("Invalid request method. Only POST requests are allowed.")

    global peptides
    global metadata
    global fastadata

    peptide_file = request.FILES.get('Peptides', None)
    meta_file = request.FILES.get('Metadata', None)
    fasta_file = request.FILES.get('Fastafile', None)

    if peptide_file is not None:
        peptides = read_peptides(peptide_file)
        enrichment_analysis.set_peptides(peptides)
    elif meta_file is not None:
        metadata = read_metadata(meta_file)
        enrichment_analysis.metadata = metadata
    elif fasta_file is not None:
        fastadata = read_fasta(fasta_file)
        enrichment_analysis.set_fasta(fastadata)
    else:
        raise ValueError("No valid file uploaded. Please upload at least one of the following: Peptides, Metadata, Fastafile.")

    return JsonResponse({"message": "File processed successfully"})


def proteins_view(request):
    """
    Search for proteins in the dataset based on a filter string.
    """
    if peptides is None:
        return JsonResponse({"proteins": []})

    filter = request.GET.get('filter','')
    proteins = getProteins(peptides, filter=filter)

    return JsonResponse({"proteins": proteins})

def enzymes_view(request):
    """
    Get list of enzymes.
    """
    
    filter = request.GET.get('filter')
    enzymes = enrichment_analysis.search_enzymes(filter)

    return JsonResponse({"enzymes": enzymes})

def species_view(request):
    """
    Get list of species.
    """

    filter = request.GET.get('filter')
    species = enrichment_analysis.search_species(filter)

    return JsonResponse({"species": species})

def metadata_view(request):
    """
    Get metadata columns from the dataset.
    """
    metadata_groups = get_metadata_groups(metadata)
    
    return JsonResponse({"metadata_groups": metadata_groups})

@csrf_exempt
@with_logging
def plot_view(request, logger):
    """
    Render the plot view.
    """
    if request.method != "POST":
        raise ValueError("Invalid request method. Only POST requests are allowed.")
    
    formData = json.loads(request.body)

    plot = get_plot(peptides, metadata, fastadata, formData, enrichment_analysis)
    plot_json = pio.to_json(plot)

    return JsonResponse({"plot": plot_json})