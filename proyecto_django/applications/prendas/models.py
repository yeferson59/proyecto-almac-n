from django.db import models
from django.conf import settings

class Prenda(models.Model):
    nombre_prenda = models.CharField(max_length=100)
    color_prenda = models.CharField(max_length=50)
    talla_prenda = models.CharField(max_length=10)
    categoria_prenda = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock = models.PositiveIntegerField(default=0)  # Inventario disponible
    imagen = models.ImageField(upload_to='prendas/', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_prenda} - {self.talla_prenda}"

    def tiene_stock(self, cantidad=1):
        """Verifica si hay suficiente stock para la cantidad solicitada"""
        return self.stock >= cantidad

    def reducir_stock(self, cantidad):
        """Reduce el stock de la prenda"""
        if self.tiene_stock(cantidad):
            self.stock -= cantidad
            self.save()
            return True
        return False

class Carrito(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carrito')
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito de {self.usuario.username}"

    def total_items(self):
        return sum(item.cantidad for item in self.items.all())

    def total_precio(self):
        """Calcula el precio total del carrito"""
        return sum(item.subtotal() for item in self.items.all())

    def limpiar(self):
        """Vacía el carrito"""
        self.items.all().delete()

class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    prenda = models.ForeignKey(Prenda, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('carrito', 'prenda')

    def __str__(self):
        return f"{self.cantidad} x {self.prenda.nombre_prenda} en carrito de {self.carrito.usuario.username}"

    def subtotal(self):
        """Calcula el subtotal para este item"""
        return self.cantidad * self.prenda.precio
