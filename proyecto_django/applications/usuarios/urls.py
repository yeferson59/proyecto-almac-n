from django.urls import path
from applications.usuarios import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.principal, name='principal'),
    path('menu/', views.menu_view, name='menu'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view,name='logout'),
    path('registro/', views.registro_view, name='registro'),
    path('verificar-otp/', views.verificar_otp, name='verificar_otp'),
    path('acceso-denegado/', views.acceso_denegado, name='acceso_denegado'),
    path('gestion-usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('usuario/<int:usuario_id>/', views.detalle_usuario, name='detalle_usuario'),
    path('usuario/<int:usuario_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuario/<int:usuario_id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
]
