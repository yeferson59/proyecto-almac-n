# Generated by Django 5.1.2 on 2025-06-07 22:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('prendas', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Historial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_compra', models.DateTimeField(auto_now_add=True)),
                ('cantidad', models.PositiveIntegerField()),
                ('total_pago', models.DecimalField(decimal_places=2, max_digits=10)),
                ('prenda', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='prendas.prenda')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
