# Usa una imagen de Python con Tkinter preinstalado
FROM python:3.14-rc-slim 

# Instala Tkinter si no viene en la imagen base
RUN apt-get update && apt-get install -y python3-tk

# Configura la zona horaria y variables para evitar problemas gráficos
ENV TZ=America/Argentina/Buenos_Aires
ENV DISPLAY=:0

# Crea y mueve al directorio de la app
WORKDIR /app
COPY requirements.txt .

# Instala las dependencias
RUN pip install --upgrade pip -r requirements.txt

# Copia los archivos al contenedor
COPY . .

# Comando para ejecutar la app
CMD ["python", "main.py"]
