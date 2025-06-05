FROM openjdk:17-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar código fuente Java
COPY src/java/ .

# Compilar aplicación Java
RUN javac *.java

# Crear directorio para descargas
RUN mkdir -p downloads

# Comando por defecto
CMD ["java", "com.filedownloader.Main"]