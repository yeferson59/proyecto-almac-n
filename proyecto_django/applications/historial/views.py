from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import Historial
from applications.usuarios.decorators import AdminRequiredMixin

@login_required
def historial_usuario(request):
    """Vista del historial de compras del usuario actual"""
    historial = Historial.objects.filter(usuario=request.user).order_by('-fecha_compra')
    
    context = {
        'historial': historial,
        'es_usuario': True
    }
    return render(request, 'historial/historial_usuario.html', context)

class HistorialAdminView(AdminRequiredMixin, ListView):
    """Vista del historial de todas las compras para administradores"""
    model = Historial
    template_name = 'historial/historial_admin.html'
    context_object_name = 'historial'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Historial.objects.select_related('usuario', 'prenda').order_by('-fecha_compra')
        
        # Filtro por usuario si se especifica
        usuario_buscar = self.request.GET.get('usuario')
        if usuario_buscar:
            queryset = queryset.filter(
                Q(usuario__username__icontains=usuario_buscar) |
                Q(usuario__first_name__icontains=usuario_buscar) |
                Q(usuario__last_name__icontains=usuario_buscar)
            )
        
        # Filtro por prenda si se especifica
        prenda_buscar = self.request.GET.get('prenda')
        if prenda_buscar:
            queryset = queryset.filter(prenda__nombre_prenda__icontains=prenda_buscar)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_admin'] = True
        context['usuario_buscar'] = self.request.GET.get('usuario', '')
        context['prenda_buscar'] = self.request.GET.get('prenda', '')
        
        # Estadísticas para el admin
        context['total_ventas'] = Historial.objects.count()
        context['total_ingresos'] = sum(h.total_pago for h in Historial.objects.all())
        
        return context

@login_required
def historial_usuario_admin(request, user_id):
    """Vista para que el admin vea el historial de un usuario específico"""
    if not request.user.is_staff and not (hasattr(request.user, 'rol') and request.user.rol == 'admin'):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden('No tienes permisos para ver este historial.')
    User = get_user_model()
    usuario = User.objects.get(pk=user_id)
    historial = Historial.objects.filter(usuario=usuario).order_by('-fecha_compra')
    context = {
        'historial': historial,
        'usuario_obj': usuario,
        'es_usuario': False
    }
    return render(request, 'historial/historial_usuario_admin.html', context)

