import os
from django.http import FileResponse
from django.shortcuts import render

from backend import settings

def react(request):
    file_path = os.path.join(settings.STATICFILES_BASE, 'index.html')
    return FileResponse(open(file_path, 'rb'), content_type='text/html')