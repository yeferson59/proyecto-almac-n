from django.shortcuts import render

def mi_vista_404(request, exception):
    return render(request, '404.html', status=404)
