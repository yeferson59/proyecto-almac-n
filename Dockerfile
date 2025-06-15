# Imagen base oficial de Python
FROM python:3.13.3-slim

# Instala curl para descargar uv (gestor de paquetes ultrarrápido)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Instala uv y agrega al PATH globalmente
RUN pip install --no-cache-dir uv

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de dependencias
COPY pyproject.toml uv.lock ./

# Genera requirements.txt desde pyproject.toml y uv.lock
RUN uv sync

# Copia el resto del código del proyecto Django
COPY . .

# Recolecta archivos estáticos
RUN uv run python proyecto_django/manage.py collectstatic --noinput

# Expone el puerto 8000
EXPOSE 8000

# Comando para producción: Gunicorn + WhiteNoise
CMD ["uv", "run", "gunicorn", "--chdir", "proyecto_django", "--bind", "0.0.0.0:8000", "proyecto_django.wsgi:application"]
