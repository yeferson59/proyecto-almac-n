import pyotp
from django import forms
from .models import Usuario
from django.contrib.auth.forms import UserCreationForm

class RegistroUsuarioForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'rol', 'password1', 'password2']
    def save(self, commit=True):
        user = super().save(commit=False)
        user.otp_secret = pyotp.random_base32()  # Genera el secreto OTP único
        if commit:
            user.save()
        return user


    