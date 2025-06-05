#ifndef FILE_DOWNLOADER_HPP
#define FILE_DOWNLOADER_HPP

#include <string>
#include <vector>
#include <memory>
#include <curl/curl.h>

namespace FileDownloader {

/**
 * @brief Estructura para almacenar la respuesta HTTP
 */
struct HttpResponse {
    std::string data;
    long response_code;
    std::string error_message;
    
    HttpResponse() : response_code(0) {}
};

/**
 * @brief Clase principal para descargar archivos desde páginas web
 */
class WebFileDownloader {
private:
    std::string base_url_;
    std::string user_agent_;
    CURL* curl_handle_;
    
    // Callback para escribir datos recibidos
    static size_t WriteCallback(void* contents, size_t size, size_t nmemb, HttpResponse* response);
    
    // Función auxiliar para inicializar curl
    bool InitializeCurl();
    
    // Función auxiliar para limpiar recursos
    void Cleanup();

public:
    /**
     * @brief Constructor
     * @param base_url URL base del sitio web
     * @param user_agent User agent para las peticiones HTTP
     */
    explicit WebFileDownloader(const std::string& base_url, 
                              const std::string& user_agent = "Mozilla/5.0 (C++ FileDownloader)");
    
    /**
     * @brief Destructor
     */
    ~WebFileDownloader();
    
    /**
     * @brief Obtiene el contenido HTML de una página
     * @param url URL de la página a obtener
     * @return Respuesta HTTP con el contenido
     */
    HttpResponse FetchPageContent(const std::string& url);
    
    /**
     * @brief Extrae enlaces de archivos con una extensión específica
     * @param html_content Contenido HTML a analizar
     * @param file_extension Extensión de archivo a buscar
     * @return Vector con las URLs de los archivos encontrados
     */
    std::vector<std::string> ParseFileLinks(const std::string& html_content, 
                                           const std::string& file_extension);
    
    /**
     * @brief Descarga un archivo desde una URL
     * @param file_url URL del archivo a descargar
     * @param output_path Ruta donde guardar el archivo
     * @return true si la descarga fue exitosa, false en caso contrario
     */
    bool DownloadFile(const std::string& file_url, const std::string& output_path);
    
    /**
     * @brief Descarga todos los archivos con una extensión específica desde una página
     * @param page_url URL de la página a analizar
     * @param file_extension Extensión de archivos a buscar
     * @param download_dir Directorio donde guardar los archivos
     * @return Número de archivos descargados exitosamente
     */
    int DownloadFilesFromPage(const std::string& page_url, 
                             const std::string& file_extension,
                             const std::string& download_dir = "downloads");
    
    /**
     * @brief Convierte URL relativa a absoluta
     * @param base_url URL base
     * @param relative_url URL relativa
     * @return URL absoluta
     */
    static std::string ResolveUrl(const std::string& base_url, const std::string& relative_url);
    
    /**
     * @brief Crea un directorio si no existe
     * @param path Ruta del directorio
     * @return true si el directorio existe o fue creado exitosamente
     */
    static bool CreateDirectory(const std::string& path);
    
    /**
     * @brief Extrae el nombre del archivo de una URL
     * @param url URL del archivo
     * @return Nombre del archivo
     */
    static std::string ExtractFilename(const std::string& url);
};

} // namespace FileDownloader

#endif // FILE_DOWNLOADER_HPP