from django.urls import path
from applications.prendas import views

from django.urls import path
from .views import (
    PrendaListView,
    PrendaListUser,
    PrendaCreateView,
    PrendaUpdateView,
    PrendaDeleteView,
    PrendaDetailView,
    CarritoView,
    agregar_al_carrito,
    eliminar_del_carrito,
    actualizar_cantidad_carrito,
    procesar_compra,
    confirmar_compra,
    compra_exitosa,
)

app_name = 'prendas'

urlpatterns = [
    path('carrito/', CarritoView.as_view(), name='ver_carrito'),
    path('carrito/agregar/<int:prenda_id>/', agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:item_id>/', eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/actualizar/<int:item_id>/<str:accion>/', actualizar_cantidad_carrito, name='actualizar_cantidad_carrito'),
    path('carrito/confirmar/', confirmar_compra, name='confirmar_compra'),
    path('carrito/procesar/', procesar_compra, name='procesar_compra'),
    path('compra-exitosa/', views.compra_exitosa, name='compra_exitosa'),
    path('', PrendaListView.as_view(), name='listar_prendas'),
    path('listar_prendas_usuario',views.PrendaListUser.as_view(),name='listar_como_usuario'),
    path('crear/', PrendaCreateView.as_view(), name='crear_prenda'),
    path('<int:pk>/editar/', PrendaUpdateView.as_view(), name='editar_prenda'),
    path('<int:pk>/eliminar/', PrendaDeleteView.as_view(), name='eliminar_prenda'),
    path('<int:pk>/', PrendaDetailView.as_view(), name='detalle_prenda'),
]
