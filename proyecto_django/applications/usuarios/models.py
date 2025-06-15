from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('usuario', 'Usuario'),
    )
    rol = models.CharField(max_length=10, choices=ROLES, default='usuario')

    otp_secret = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.rol})"

# Create your models here.
