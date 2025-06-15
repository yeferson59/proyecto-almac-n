from django.urls import path
from applications.historial import views
from .views import HistorialAdminView, historial_usuario

app_name = 'historial'

urlpatterns = [
    path('', historial_usuario, name='mi_historial'),
    path('admin/', HistorialAdminView.as_view(), name='historial_admin'),
    path('admin/usuario/<int:user_id>/', views.historial_usuario_admin, name='historial_usuario_admin'),
]

