# 🔧 GUÍA DE PRUEBA DE RESTRICCIONES DE ACCESO

El servidor está ejecutándose en: http://127.0.0.1:8000/

## USUARIOS DE PRUEBA DISPONIBLES:

👤 USUARIOS NORMALES (NO deben acceder al CRUD):

- Username: daniel, Password: (usar la que configuraste)
- Username: yan1234, Password: (usar la que configuraste)
- Username: prueba123, Password: (usar la que configuraste)
- Username: yeferson59, Password: (usar la que configuraste)

👨‍💼 ADMINISTRADORES (SÍ pueden acceder al CRUD):

- Username: admin, Password: (usar la que configuraste) [is_staff=True]
- Username: administrador, Password: (usar la que configuraste) [rol=admin]
- Username: yeferson, Password: (usar la que configuraste) [rol=admin]

## PRUEBAS A REALIZAR:

1. 🔒 PRUEBA CON USUARIO NORMAL:
   a) Ir a: http://127.0.0.1:8000/login/
   b) Iniciar sesión con: daniel (usuario normal)
   c) Intentar acceder directamente a: http://127.0.0.1:8000/prendas/crear/
   d) RESULTADO ESPERADO: Página de "Acceso Restringido"

2. 🔒 PRUEBA ADICIONAL CON USUARIO NORMAL:
   a) Intentar acceder a: http://127.0.0.1:8000/prendas/1/editar/
   b) RESULTADO ESPERADO: Página de "Acceso Restringido"

   c) Intentar acceder a: http://127.0.0.1:8000/prendas/1/eliminar/
   d) RESULTADO ESPERADO: Página de "Acceso Restringido"

3. ✅ PRUEBA CON ADMINISTRADOR:
   a) Cerrar sesión
   b) Iniciar sesión con: admin (administrador)
   c) Intentar acceder a: http://127.0.0.1:8000/prendas/crear/
   d) RESULTADO ESPERADO: Página de crear prenda (formulario)

4. 🔍 VERIFICAR NAVEGACIÓN EN HEADER:
   a) Con usuario normal logueado: debe ver "Catálogo"
   b) Con administrador logueado: debe ver "Gestionar Prendas"

## URLs A PROBAR:

- /prendas/crear/ (crear prenda)
- /prendas/1/editar/ (editar prenda - cambiar el 1 por un ID existente)
- /prendas/1/eliminar/ (eliminar prenda - cambiar el 1 por un ID existente)
- /prendas/ (lista de prendas admin)

## URLs QUE DEBEN FUNCIONAR PARA TODOS:

- /prendas/listar_prendas_usuario (catálogo de usuario)
- /prendas/1/ (detalle de prenda)
- /prendas/carrito/ (carrito - solo usuarios autenticados)

## RESULTADOS ESPERADOS:

✅ Usuario normal + URL de CRUD = Página "Acceso Restringido"
✅ Administrador + URL de CRUD = Página del formulario correspondiente
✅ Usuario no autenticado + cualquier URL protegida = Redirección a login
