"""
URL configuration for proyecto_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from two_factor.urls import urlpatterns as tf_urls
from django.conf.urls import handler404
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve



urlpatterns = [
    path('', include(tf_urls)),
    path('admin/', admin.site.urls),
    re_path('',include(('applications.usuarios.urls', 'usuarios'), namespace='usuarios')),  # Ajusta según tu estructura
    re_path('prendas/', include(('applications.prendas.urls', 'prendas'), namespace='prendas')),
    re_path('historial/', include(('applications.historial.urls', 'historial'), namespace='historial')),
    # Servir archivos media y static siempre (para Docker)
    path('media/<path:path>', views.serve_media, name='serve_media'),
    path('static/<path:path>', views.serve_static, name='serve_static'),
]

handler404 = 'proyecto_django.views.mi_vista_404'
