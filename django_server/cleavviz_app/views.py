import json
import logging
import traceback
import pandas as pd
import plotly.io as pio
from django_server import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse, JsonResponse
from utils.logging import InMemoryLogHandler

from cleavviz.data import get_metadata_groups, get_plot, getProteins, read_data, read_fasta, read_metadata, read_peptides

def index(request):
    file_path = settings.STATICFILES_BASE / 'frontend' / 'index.html'
    return FileResponse(open(file_path, 'rb'), content_type='text/html')

peptides: pd.DataFrame = None
metadata: pd.DataFrame = None
fastadata: pd.DataFrame = None

@csrf_exempt
def upload_view(request):
    """
    Handle file upload and process the data.
    """
    if request.method == 'POST':
        global peptides
        global metadata
        global fastadata

        peptide_file = request.FILES.get('Peptides', None)
        meta_file = request.FILES.get('Metadata', None)
        fasta_file = request.FILES.get('Fastafile', None)

        if peptide_file is not None:
            peptides = read_peptides(peptide_file)
        elif meta_file is not None:
            metadata = read_metadata(meta_file)
        elif fasta_file is not None:
            fastadata = read_fasta(fasta_file)
        else:
            return JsonResponse({"error": "Unsupported file upload."}, status=400)

        try:
            return JsonResponse({"message": "File processed successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

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
    onlyStandardEnzymes = request.GET.get('onlyStandardEnzymes', 'true') == 'true'

    if onlyStandardEnzymes:
        enzymes = ["Standard Enzyme 1", "Standard Enzyme 2"]
    else:
        enzymes = ["Test Enzyme 1", "Test Enzyme 2"]

    return JsonResponse({"enzymes": enzymes})


def metadata_view(request):
    """
    Get metadata columns from the dataset.
    """
    metadata_groups = get_metadata_groups(metadata)
    
    return JsonResponse({"metadata_groups": metadata_groups})

@csrf_exempt
def plot_view(request):
    """
    Render the plot view.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)
    
    logger = logging.getLogger()
    log_handler = InMemoryLogHandler()
    log_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    logger.propagate = False

    try:
        formData = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    try:
        plot = get_plot(peptides, metadata, fastadata, formData)
        plot_json = pio.to_json(plot)
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error creating plot: {e}")
        response = JsonResponse({
            "logs": list(set(log_handler.get_logs().splitlines())),
        })
    else:
        response = JsonResponse({
            "plot": plot_json,
            "logs": list(set(log_handler.get_logs().splitlines())),
        })

    logger.removeHandler(log_handler)
    log_handler.close()

    return response