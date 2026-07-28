# Usa una imagen oficial y ligera de Python
FROM python:3.11-slim

# Evita que Python escriba archivos .pyc y fuerza el output inmediato en terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo en el contenedor
WORKDIR /app

# Instala dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala requerimientos primero (optimiza el uso de caché)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código del proyecto
COPY . /app/

# Expone el puerto predeterminado de Django
EXPOSE 8000

# Comando para levantar el servidor de desarrollo
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
