from django.shortcuts import render
from django.http import Http404, FileResponse
from django.conf import settings
import os

def mi_vista_404(request, exception):
    return render(request, '404.html', status=404)

def serve_media(request, path):
    """Vista personalizada para servir archivos media"""
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(open(file_path, 'rb'))
    raise Http404("Archivo no encontrado")

def serve_static(request, path):
    """Vista personalizada para servir archivos static"""
    file_path = os.path.join(settings.STATIC_ROOT, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(open(file_path, 'rb'))
    raise Http404("Archivo no encontrado")
