from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import reverse
from functools import wraps

def admin_required(view_func):
    """
    Decorador que requiere que el usuario sea administrador (rol='admin' o is_staff=True)
    Si no es admin, muestra página de acceso denegado
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        
        if not (request.user.rol == 'admin' or request.user.is_staff):
            return render(request, 'usuarios/acceso_denegado.html', {
                'mensaje': 'Esta página está reservada para administradores.',
                'es_admin': False
            })
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def usuario_normal_required(view_func):
    """
    Decorador para vistas que solo pueden ver usuarios normales autenticados
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def anonymous_or_authenticated(view_func):
    """
    Decorador para vistas que pueden ver tanto usuarios anónimos como autenticados
    (como la página principal, login, registro)
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return _wrapped_view

class AdminRequiredMixin:
    """
    Mixin para vistas basadas en clases que requieren permisos de administrador
    """
    def dispatch(self, request, *args, **kwargs):
        # Verificar autenticación
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        
        # Verificar permisos de administrador
        is_admin = (
            hasattr(request.user, 'rol') and request.user.rol == 'admin'
        ) or request.user.is_staff or request.user.is_superuser
        
        if not is_admin:
            return render(request, 'usuarios/acceso_denegado.html', {
                'mensaje': 'Esta página está reservada para administradores.',
                'es_admin': False
            })
        
        return super().dispatch(request, *args, **kwargs)

class UsuarioNormalRequiredMixin:
    """
    Mixin para vistas basadas en clases que requieren usuario autenticado
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        
        return super().dispatch(request, *args, **kwargs)
