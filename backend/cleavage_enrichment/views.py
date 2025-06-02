import math
import os
from django.http import FileResponse
from django.shortcuts import render
import pandas as pd

from backend import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

def index(request):
    file_path = os.path.join(settings.STATICFILES_BASE, 'index.html')
    return FileResponse(open(file_path, 'rb'), content_type='text/html')

proteindata: pd.DataFrame = None
peptidedata: pd.DataFrame = None
sample: str = "AD01_C1_INSOLUBLE_01"

def loadProteins():
    global proteindata
    if proteindata is None:
        path = settings.STATICFILES_BASE / "MaxQuantImport_1_protein_df.csv"
        if not os.path.exists(path):
            raise FileNotFoundError(f"Data file not found at {path}")
        
        proteindata = pd.read_csv(path)
    return proteindata

def loadPeptides():
    global peptidedata
    if peptidedata is None:
        path = settings.STATICFILES_BASE / "PeptideImport_1_peptide_df.csv"
        if not os.path.exists(path):
            raise FileNotFoundError(f"Data file not found at {path}")
        
        peptidedata = pd.read_csv(path)
    return peptidedata

def getProteins(request):
    """
    Search for proteins in the dataset based on a filter string.
    """
    loadProteins()

    filter = request.GET.get('filter','')

    global proteindata
        
    # Example data, replace with actual data retrieval logic
    proteins = proteindata[(proteindata["Sample"] == sample) & (proteindata["Protein ID"].str.contains(filter, case=False, na=False))].head(5)["Protein ID"].tolist()
    
    return JsonResponse({"proteins": proteins})


def getPlotDataHelper(protein_id):
    """
    Helper function to get plot data for a specific protein.
    """
    
    peptides = peptidedata[(peptidedata["Protein ID"] == protein_id)]

    if peptides.empty:
        return {
            "protein_id": protein_id,
            "peptide_count": [],
            "peptide_intensity": []
        }

    last_peptide_position = int(peptides["End position"].max())

    count = [0] * last_peptide_position
    intensity = [0] * last_peptide_position

    for _, peptide in peptides.iterrows():
        start = int(peptide["Start position"]) - 1  # assuming positions are 1-based
        end = int(peptide["End position"])          # inclusive
        for i in range(start, end):
            count[i] += 1
            if not math.isnan(peptide["Intensity"]):
                intensity[i] += int(peptide["Intensity"])
    
    return {
        "protein_id": protein_id,
        "peptide_count": count,
        "peptide_intensity": intensity
    }


def getPlotData(request):
    proteins = request.GET.getlist('proteins')
    if not proteins:
        return JsonResponse({"error": "No protein specified"}, status=400)

    loadPeptides()

    data = []

    for protein_id in proteins:
        data.append(getPlotDataHelper(protein_id))

    return JsonResponse({
        "data": data
    })

    


