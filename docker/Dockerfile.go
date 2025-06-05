FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copiar archivos Go
COPY src/go/ .

# Compilar aplicación
RUN go build -o filedownloader filedownloader.go

# Imagen final
FROM alpine:latest

WORKDIR /app

# Instalar certificados SSL
RUN apk --no-cache add ca-certificates

# Copiar ejecutable
COPY --from=builder /app/filedownloader .

# Crear directorio para descargas
RUN mkdir -p downloads

# Comando por defecto
CMD ["./filedownloader"]