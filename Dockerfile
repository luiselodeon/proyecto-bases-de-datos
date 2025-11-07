# Usa una imagen base de Python
FROM python:3.9-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo de requerimientos e instala las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de la aplicación
COPY . .

# Expone el puerto en el que corre la aplicación
EXPOSE 5000

# Comando para correr la aplicación
CMD ["python", "app.py"]
