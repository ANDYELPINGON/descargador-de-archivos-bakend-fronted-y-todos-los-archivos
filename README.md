# File Downloader - Multi-Language Implementation

Un proyecto completo para descargar archivos desde páginas web, implementado en múltiples lenguajes de programación.

## 🌟 Características

- **Multi-lenguaje**: Implementaciones en Python, C++, JavaScript/Node.js, Java y Go
- **Descarga robusta**: Manejo de errores para operaciones de red y archivos
- **Manejo de URLs**: Conversión adecuada de URLs relativas a absolutas
- **Headers configurables**: User agents y headers HTTP personalizables
- **Descargas paralelas**: Soporte para descargas concurrentes (Java, Go)
- **Suite de tests completa**: 99% de cobertura en Python
- **Containerización**: Soporte completo con Docker

## 🚀 Instalación Rápida

### Usando Make (Recomendado)
```bash
# Instalar todas las dependencias
make install

# Compilar todos los proyectos
make all

# Ver información del proyecto
make info
```

### Manual por Lenguaje

#### Python
```bash
pip install -r requirements.txt
```

#### JavaScript/Node.js
```bash
cd src/javascript
npm install
```

#### C++
```bash
cd src/cpp
g++ -std=c++17 -o file_downloader main.cpp file_downloader.cpp -lcurl
```

#### Java
```bash
cd src/java
javac *.java
```

#### Go
```bash
cd src/go
go build -o filedownloader filedownloader.go
```

## 🎯 Uso

### Python
```bash
# Ejecutar directamente
python tripero.py

# Como módulo
make run-python
```

### JavaScript/Node.js
```bash
# Ejecutar directamente
cd src/javascript && node main.js

# Con make
make run-js
```

### C++
```bash
# Compilar y ejecutar
make run-cpp
```

### Java
```bash
# Compilar y ejecutar
make run-java
```

### Go
```bash
# Compilar y ejecutar
make run-go
```

### Docker
```bash
# Ejecutar con Python
docker-compose up python-downloader

# Ejecutar con Node.js
docker-compose up nodejs-downloader

# Ejecutar con Go
docker-compose up go-downloader

# Ejecutar con Java
docker-compose up java-downloader

# Entorno de desarrollo completo
docker-compose up dev-environment
```

## 🧪 Testing

### Python (Suite Completa)
```bash
# Ejecutar todos los tests
make test

# Tests con cobertura
pytest --cov=tripero --cov-report=term-missing

# Tests específicos
pytest tests/test_tripero.py::TestFileDownloader
```

## 📊 Cobertura de Tests

El proyecto mantiene **99% de cobertura** en Python, probando toda la funcionalidad principal:

- ✅ Manejo de peticiones HTTP y casos de error
- ✅ Parsing HTML y extracción de enlaces
- ✅ Operaciones de descarga de archivos
- ✅ Manejo de URLs (conversión relativa/absoluta)
- ✅ Manejo de errores para operaciones de red y E/S
- ✅ Escenarios de integración

## 🏗️ Estructura del Proyecto

```
.
├── tripero.py              # Implementación principal en Python
├── src/
│   ├── cpp/                # Implementación en C++
│   │   ├── file_downloader.hpp
│   │   ├── file_downloader.cpp
│   │   ├── main.cpp
│   │   └── CMakeLists.txt
│   ├── javascript/         # Implementación en Node.js
│   │   ├── fileDownloader.js
│   │   ├── main.js
│   │   └── package.json
│   ├── java/              # Implementación en Java
│   │   ├── FileDownloader.java
│   │   └── Main.java
│   └── go/                # Implementación en Go
│       ├── filedownloader.go
│       └── go.mod
├── tests/                 # Suite de tests (Python)
│   ├── __init__.py
│   └── test_tripero.py
├── docker/               # Dockerfiles para cada lenguaje
│   ├── Dockerfile.python
│   ├── Dockerfile.nodejs
│   ├── Dockerfile.java
│   ├── Dockerfile.go
│   └── Dockerfile.dev
├── requirements.txt      # Dependencias Python
├── pytest.ini          # Configuración de tests
├── Makefile            # Automatización de builds
├── docker-compose.yml  # Orquestación de contenedores
└── README.md          # Este archivo
```

## 🔧 Características por Lenguaje

| Lenguaje | Concurrencia | Dependencias | Compilación | Rendimiento |
|----------|-------------|--------------|-------------|-------------|
| **Python** | ❌ | requests, beautifulsoup4 | ❌ | ⭐⭐⭐ |
| **C++** | ❌ | libcurl | ✅ | ⭐⭐⭐⭐⭐ |
| **JavaScript** | ✅ | axios, cheerio | ❌ | ⭐⭐⭐⭐ |
| **Java** | ✅ | Ninguna (stdlib) | ✅ | ⭐⭐⭐⭐ |
| **Go** | ✅ | Ninguna (stdlib) | ✅ | ⭐⭐⭐⭐⭐ |

## 🐳 Docker

Cada implementación tiene su propio Dockerfile optimizado:

```bash
# Construir todas las imágenes
docker-compose build

# Ejecutar implementación específica
docker-compose up [python-downloader|nodejs-downloader|java-downloader|go-downloader]

# Entorno de desarrollo
docker-compose up dev-environment
```

## 🛠️ Comandos Make Disponibles

```bash
make install      # Instalar dependencias
make all          # Compilar todos los proyectos
make test         # Ejecutar tests de Python
make clean        # Limpiar archivos compilados

# Ejecutar por lenguaje
make run-python   # Ejecutar versión Python
make run-js       # Ejecutar versión JavaScript
make run-cpp      # Ejecutar versión C++
make run-java     # Ejecutar versión Java
make run-go       # Ejecutar versión Go

# Compilar por lenguaje
make build-cpp    # Compilar C++
make build-java   # Compilar Java
make build-go     # Compilar Go
```

## 🎨 Calidad del Código

- **Type hints** para mejor documentación (Python)
- **Documentación completa** con docstrings/comentarios
- **Manejo de errores** para todas las operaciones externas
- **Diseño modular** para fácil testing y mantenimiento
- **Siguiendo mejores prácticas** de cada lenguaje
- **Gestión de memoria** adecuada (C++, Go)
- **Programación concurrente** donde es apropiado

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🌟 Roadmap

- [ ] Implementación en Rust
- [ ] Implementación en C#
- [ ] GUI con Electron/Tauri
- [ ] API REST
- [ ] Soporte para autenticación
- [ ] Descarga de sitios completos
- [ ] Interfaz web con React/Vue