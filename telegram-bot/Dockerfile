# Usar una imagen de Python como base
FROM python:3.9

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Copiar el archivo de dependencias a la imagen
COPY app/requirements.txt .

# Instalar las dependencias
RUN pip install -r requirements.txt

# Copiar el código de la aplicación a la imagen
COPY app/ /app

# Definir el comando por defecto
CMD ["python", "main.py"]
