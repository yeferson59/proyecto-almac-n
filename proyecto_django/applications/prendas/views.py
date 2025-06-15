from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db import transaction
from django.utils import timezone

from .models import Prenda, Carrito, CarritoItem
from .forms import PrendaForm
from applications.usuarios.decorators import AdminRequiredMixin, UsuarioNormalRequiredMixin
from applications.historial.models import Historial

class PrendaListView(AdminRequiredMixin, ListView):
    """Vista de lista de prendas para administradores - CRUD completo"""
    model = Prenda
    template_name = 'prendas/listar.html'
    context_object_name = 'prendas'
    paginate_by = 8  # Muestra 8 productos por página para admin

class PrendaListUser(ListView):
    """Vista de catálogo para usuarios normales - solo visualización"""
    model = Prenda
    template_name = 'prendas/listar_como_usuario.html'
    context_object_name = 'prendas'
    paginate_by = 6  # Muestra 6 productos por página


@method_decorator(login_required, name='dispatch')
class CarritoView(UsuarioNormalRequiredMixin, View):
    """Vista del carrito - requiere usuario autenticado"""
    def get(self, request):
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        items = carrito.items.select_related('prenda').all()
        return render(request, 'prendas/carrito.html', {'carrito': carrito, 'items': items})


@login_required
def agregar_al_carrito(request, prenda_id):
    prenda = get_object_or_404(Prenda, id=prenda_id)
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    item, item_created = CarritoItem.objects.get_or_create(carrito=carrito, prenda=prenda)
    if not item_created:
        item.cantidad += 1
        item.save()
        messages.info(request, f'Se aumentó la cantidad de "{prenda.nombre_prenda}" en tu carrito.')
    else:
        messages.success(request, f'"{prenda.nombre_prenda}" añadido al carrito.')
    return redirect(request.META.get('HTTP_REFERER', reverse('prendas:listar_como_usuario')))

@login_required
def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(CarritoItem, id=item_id, carrito__usuario=request.user)
    item.delete()
    messages.success(request, 'Producto eliminado del carrito.')
    return redirect('prendas:ver_carrito')

@login_required
def actualizar_cantidad_carrito(request, item_id, accion):
    item = get_object_or_404(CarritoItem, id=item_id, carrito__usuario=request.user)
    if accion == 'sumar':
        item.cantidad += 1
        item.save()
    elif accion == 'restar':
        if item.cantidad > 1:
            item.cantidad -= 1
            item.save()
        else:
            item.delete()
    return redirect('prendas:ver_carrito')

class PrendaCreateView(AdminRequiredMixin, CreateView):
    """Vista para crear prendas - solo administradores"""
    model = Prenda
    form_class = PrendaForm
    template_name = 'prendas/crear.html'
    success_url = reverse_lazy('prendas:listar_prendas')

class PrendaUpdateView(AdminRequiredMixin, UpdateView):
    """Vista para editar prendas - solo administradores"""
    model = Prenda
    form_class = PrendaForm
    template_name = 'prendas/editar.html'
    success_url = reverse_lazy('prendas:listar_prendas')

class PrendaDeleteView(AdminRequiredMixin, DeleteView):
    """Vista para eliminar prendas - solo administradores"""
    model = Prenda
    template_name = 'prendas/eliminar.html'
    success_url = reverse_lazy('prendas:listar_prendas')

class PrendaDetailView(DetailView):
    """Vista de detalle de prenda - muestra template especial para admin"""
    model = Prenda
    context_object_name = 'prenda'

    def get_template_names(self):
        user = self.request.user
        if user.is_authenticated and (user.is_staff or hasattr(user, 'rol') and user.rol == 'admin'):
            return ['prendas/detalle_admin.html']
        return ['prendas/detalle.html']

@login_required
def procesar_compra(request):
    """Procesa la compra del carrito actual"""
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.select_related('prenda').all()
    
    if not items:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('prendas:ver_carrito')
      # Verificar stock disponible
    items_sin_stock = []
    for item in items:
        if not item.prenda.tiene_stock(item.cantidad):
            items_sin_stock.append(f"{item.prenda.nombre_prenda} (solicitado: {item.cantidad}, disponible: {item.prenda.stock})")
    
    if items_sin_stock:
        messages.error(request, f'No hay suficiente stock para: {", ".join(items_sin_stock)}')
        return redirect('prendas:ver_carrito')
    
    # Procesar la compra
    try:
        with transaction.atomic():
            total_compra = carrito.total_precio()
            cantidad_productos = sum(item.cantidad for item in items)
            
            # Crear registros en el historial y reducir stock
            for item in items:
                # Crear registro de historial
                Historial.objects.create(
                    usuario=request.user,
                    prenda=item.prenda,
                    cantidad=item.cantidad,
                    total_pago=item.subtotal()
                )
                
                # Reducir stock
                item.prenda.reducir_stock(item.cantidad)
            
            # Limpiar carrito
            carrito.limpiar()
            
            # Redirigir a página de éxito con datos
            request.session['compra_exitosa'] = {
                'total_compra': float(total_compra),
                'cantidad_productos': cantidad_productos,
                'fecha_compra': timezone.now().isoformat()
            }
            return redirect('prendas:compra_exitosa')
    
    except Exception as e:
        messages.error(request, f'Error al procesar la compra: {str(e)}')
        return redirect('prendas:ver_carrito')

@login_required
def confirmar_compra(request):
    """Vista para confirmar la compra antes de procesarla"""
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.select_related('prenda').all()
    
    if not items:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('prendas:ver_carrito')
    
    # Verificar stock y calcular total
    items_con_info = []
    total = 0
    hay_problemas_stock = False
    
    for item in items:
        item_info = {
            'item': item,
            'subtotal': item.subtotal(),
            'stock_suficiente': item.prenda.tiene_stock(item.cantidad),
            'stock_disponible': item.prenda.stock
        }
        if not item_info['stock_suficiente']:
            hay_problemas_stock = True
        items_con_info.append(item_info)
        total += item_info['subtotal']
    
    context = {
        'items': items_con_info,
        'total': total,
        'hay_problemas_stock': hay_problemas_stock
    }
    
    return render(request, 'prendas/confirmar_compra.html', context)

@login_required
def compra_exitosa(request):
    """Vista para mostrar la confirmación de compra exitosa"""
    from datetime import datetime
    
    # Obtener datos de la compra de la sesión
    datos_compra = request.session.get('compra_exitosa')
    
    if not datos_compra:
        messages.error(request, 'No se encontraron datos de la compra.')
        return redirect('prendas:ver_carrito')
    
    # Convertir fecha ISO a datetime
    fecha_compra = datetime.fromisoformat(datos_compra['fecha_compra'])
    
    context = {
        'total_compra': datos_compra['total_compra'],
        'cantidad_productos': datos_compra['cantidad_productos'],
        'fecha_compra': fecha_compra,
    }
    
    # Limpiar datos de la sesión
    del request.session['compra_exitosa']
    
    return render(request, 'prendas/compra_exitosa.html', context)
