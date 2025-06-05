cmake_minimum_required(VERSION 3.12)
project(FileDownloader)

# Configurar estándar C++
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Buscar librerías requeridas
find_package(PkgConfig REQUIRED)
pkg_check_modules(CURL REQUIRED libcurl)

# Incluir directorios
include_directories(${CURL_INCLUDE_DIRS})

# Crear ejecutable
add_executable(file_downloader
    main.cpp
    file_downloader.cpp
)

# Enlazar librerías
target_link_libraries(file_downloader ${CURL_LIBRARIES})
target_compile_options(file_downloader PRIVATE ${CURL_CFLAGS_OTHER})

# Configurar flags de compilación
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    target_compile_options(file_downloader PRIVATE -g -Wall -Wextra)
else()
    target_compile_options(file_downloader PRIVATE -O2)
endif()

# Instalar ejecutable
install(TARGETS file_downloader DESTINATION bin)