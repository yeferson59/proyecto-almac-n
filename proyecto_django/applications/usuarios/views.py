import pyotp
import qrcode
import base64
from io import BytesIO

from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from .forms import RegistroUsuarioForm
from applications.historial.models import Historial
from django.db.models import Sum, Count

# =========================
# FUNCIONES DE UTILIDAD
# =========================

def generar_qr_otp(user, issuer="MiAppSegura"):
    """Genera el código QR y la clave TOTP para un usuario"""
    if not user.otp_secret:
        user.otp_secret = pyotp.random_base32()
        user.save()

    totp = pyotp.TOTP(user.otp_secret)
    otp_uri = totp.provisioning_uri(name=user.username, issuer_name=issuer)

    qr = qrcode.make(otp_uri)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return qr_base64, totp


# =========================
# AUTENTICACIÓN Y REGISTRO
# =========================

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            request.session['pre_2fa_user_id'] = user.id
            return redirect('usuarios:verificar_otp')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'usuarios/login.html')


def logout_view(request):
    logout(request)
    return redirect('usuarios:login')


def registro_view(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario registrado correctamente.')
            return redirect('usuarios:login')
    else:
        form = RegistroUsuarioForm()

    return render(request, 'usuarios/registro.html', {'form': form})


# =========================
# DOBLE AUTENTICACIÓN (2FA)
# =========================

def verificar_otp(request):
    user_id = request.session.get('pre_2fa_user_id')

    if not user_id:
        messages.error(request, "Sesión no válida.")
        return redirect('usuarios:login')

    User = get_user_model()
    user = User.objects.get(id=user_id)

    # Asegura que tiene otp_secret
    if not user.otp_secret:
        user.otp_secret = pyotp.random_base32()
        user.save()

    # Genera el QR
    totp = pyotp.TOTP(user.otp_secret)
    otp_uri = totp.provisioning_uri(name=user.username, issuer_name="MiSitioDobleAuth")
    qr = qrcode.make(otp_uri)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    if request.method == 'POST':
        otp = request.POST.get('otp')
        if totp.verify(otp):
            login(request, user)
            del request.session['pre_2fa_user_id']
            if user.rol == 'admin':
                return redirect('prendas:listar_prendas')
            else:
                return redirect('usuarios:menu')
        else:
            messages.error(request, "Código OTP inválido.")

    return render(request, 'usuarios/verificar_otp.html', {
        'qr_base64': qr_base64
    })

# =========================
# ====VISTAS DE USUARIO====
# ========================
@login_required
def menu_view(request):
    """Vista del menú de usuario con estadísticas"""
    historial_count = Historial.objects.filter(usuario=request.user).count()
    carrito_count = 0
    total_gastado = 0
    if 'carrito' in request.session:
        carrito_count = len(request.session['carrito'])
    total_gastado = sum(h.total_pago for h in Historial.objects.filter(usuario=request.user))

    # Estadísticas globales para admin
    if request.user.rol == 'admin' or request.user.is_staff:
        ventas_registradas = Historial.objects.count()
        ingresos_totales = Historial.objects.aggregate(total=Sum('total_pago'))['total'] or 0
        usuarios_con_compras = get_user_model().objects.filter(historial__isnull=False).distinct().count()
        context = {
            'historial_count': ventas_registradas,
            'carrito_count': 0,
            'total_gastado': ingresos_totales,
            'usuarios_con_compras': usuarios_con_compras,
        }
        return render(request, 'usuarios/menu_admin.html', context)

    context = {
        'historial_count': historial_count,
        'carrito_count': carrito_count,
        'total_gastado': total_gastado,
    }
    return render(request, 'usuarios/menu_usuario.html', context)

@login_required
def gestion_usuarios(request):
    if not (request.user.is_staff or getattr(request.user, 'rol', None) == 'admin'):
        return HttpResponseForbidden('No tienes permisos para acceder a esta página.')
    User = get_user_model()
    # Todos los usuarios
    usuarios = User.objects.all().annotate(
        total_ventas=Count('historial'),
        total_gastado=Sum('historial__total_pago')
    ).order_by('-date_joined')
    context = {
        'usuarios': usuarios,
    }
    return render(request, 'usuarios/gestion_usuarios.html', context)

@login_required
def detalle_usuario(request, usuario_id):
    if not (request.user.is_staff or getattr(request.user, 'rol', None) == 'admin'):
        return HttpResponseForbidden('No tienes permisos para acceder a esta página.')
    User = get_user_model()
    usuario = get_object_or_404(User, id=usuario_id)
    return render(request, 'usuarios/detalle_usuario.html', {'usuario': usuario})

@login_required
def editar_usuario(request, usuario_id):
    if not (request.user.is_staff or getattr(request.user, 'rol', None) == 'admin'):
        return HttpResponseForbidden('No tienes permisos para acceder a esta página.')
    User = get_user_model()
    usuario = get_object_or_404(User, id=usuario_id)
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('usuarios:gestion_usuarios')
    else:
        form = RegistroUsuarioForm(instance=usuario)
    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario': usuario})

@login_required
def eliminar_usuario(request, usuario_id):
    if not (request.user.is_staff or getattr(request.user, 'rol', None) == 'admin'):
        return HttpResponseForbidden('No tienes permisos para acceder a esta página.')
    User = get_user_model()
    usuario = get_object_or_404(User, id=usuario_id)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
        return redirect('usuarios:gestion_usuarios')
    return redirect('usuarios:gestion_usuarios')

# =========================
# ====Pagina Principal====
# ========================
def principal(request):
    return render(request, 'usuarios/pagina_principal.html')

def acceso_denegado(request):
    """Vista para mostrar cuando un usuario intenta acceder a una página restringida"""
    return render(request, 'usuarios/acceso_denegado.html', {
        'mensaje': 'No tienes permisos para acceder a esta página.',
        'es_admin': request.user.is_authenticated and (request.user.rol == 'admin' or request.user.is_staff)
    })
