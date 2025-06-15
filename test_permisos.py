#!/usr/bin/env python
"""
Script de prueba para verificar las restricciones de acceso
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/Users/yefersontoloza/Downloads/experimento/proyecto_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_django.settings.local')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory
from django.urls import reverse
from applications.prendas.views import PrendaCreateView

User = get_user_model()

# Crear un cliente de prueba
client = Client()
factory = RequestFactory()

# Verificar si existen usuarios de prueba
try:
    # Buscar un usuario normal (no admin)
    usuario_normal = User.objects.filter(rol='usuario', is_staff=False).first()

    if usuario_normal:
        print(f"✓ Usuario normal encontrado: {usuario_normal.username}")
        print(f"  - Rol: {usuario_normal.rol}")
        print(f"  - is_staff: {usuario_normal.is_staff}")

        # Simular login
        client.force_login(usuario_normal)

        # Probar acceso a crear prenda
        response = client.get('/prendas/crear/')
        print(f"\n🔒 Probando acceso a /prendas/crear/:")
        print(f"  - Status code: {response.status_code}")

        if response.status_code == 200:
            print("  ❌ PROBLEMA: Usuario normal puede acceder al CRUD")
            print("  📝 Contenido de la respuesta:", response.content[:200].decode())
        else:
            print("  ✅ CORRECTO: Usuario normal bloqueado")
            if hasattr(response, 'url'):
                print(f"  📍 Redirigido a: {response.url}")
    else:
        print("❌ No se encontró ningún usuario normal de prueba")
        print("💡 Usuarios disponibles:")
        for user in User.objects.all()[:5]:
            print(f"   - {user.username}: rol={user.rol}, is_staff={user.is_staff}")

except Exception as e:
    print(f"❌ Error: {e}")
