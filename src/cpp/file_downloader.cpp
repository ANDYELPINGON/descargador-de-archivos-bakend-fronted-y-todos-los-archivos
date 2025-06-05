#include "file_downloader.hpp"
#include <iostream>
#include <fstream>
#include <regex>
#include <filesystem>
#include <algorithm>

namespace FileDownloader {

// Implementación del callback para escribir datos
size_t WebFileDownloader::WriteCallback(void* contents, size_t size, size_t nmemb, HttpResponse* response) {
    size_t total_size = size * nmemb;
    response->data.append(static_cast<char*>(contents), total_size);
    return total_size;
}

WebFileDownloader::WebFileDownloader(const std::string& base_url, const std::string& user_agent)
    : base_url_(base_url), user_agent_(user_agent), curl_handle_(nullptr) {
    InitializeCurl();
}

WebFileDownloader::~WebFileDownloader() {
    Cleanup();
}

bool WebFileDownloader::InitializeCurl() {
    curl_global_init(CURL_GLOBAL_DEFAULT);
    curl_handle_ = curl_easy_init();
    
    if (!curl_handle_) {
        std::cerr << "Error: No se pudo inicializar CURL" << std::endl;
        return false;
    }
    
    // Configurar opciones básicas de CURL
    curl_easy_setopt(curl_handle_, CURLOPT_USERAGENT, user_agent_.c_str());
    curl_easy_setopt(curl_handle_, CURLOPT_FOLLOWLOCATION, 1L);
    curl_easy_setopt(curl_handle_, CURLOPT_TIMEOUT, 30L);
    curl_easy_setopt(curl_handle_, CURLOPT_WRITEFUNCTION, WriteCallback);
    
    return true;
}

void WebFileDownloader::Cleanup() {
    if (curl_handle_) {
        curl_easy_cleanup(curl_handle_);
        curl_handle_ = nullptr;
    }
    curl_global_cleanup();
}

HttpResponse WebFileDownloader::FetchPageContent(const std::string& url) {
    HttpResponse response;
    
    if (!curl_handle_) {
        response.error_message = "CURL no está inicializado";
        return response;
    }
    
    curl_easy_setopt(curl_handle_, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl_handle_, CURLOPT_WRITEDATA, &response);
    
    CURLcode res = curl_easy_perform(curl_handle_);
    
    if (res != CURLE_OK) {
        response.error_message = curl_easy_strerror(res);
        return response;
    }
    
    curl_easy_getinfo(curl_handle_, CURLINFO_RESPONSE_CODE, &response.response_code);
    
    return response;
}

std::vector<std::string> WebFileDownloader::ParseFileLinks(const std::string& html_content, 
                                                          const std::string& file_extension) {
    std::vector<std::string> file_links;
    
    // Expresión regular para encontrar enlaces href
    std::regex href_regex(R"(href\s*=\s*['"]\s*([^'"]*)" + file_extension + R"([^'"]*)\s*['"])");
    std::sregex_iterator iter(html_content.begin(), html_content.end(), href_regex);
    std::sregex_iterator end;
    
    for (; iter != end; ++iter) {
        std::string link = (*iter)[1].str();
        
        // Convertir URL relativa a absoluta
        std::string absolute_url = ResolveUrl(base_url_, link);
        file_links.push_back(absolute_url);
    }
    
    return file_links;
}

bool WebFileDownloader::DownloadFile(const std::string& file_url, const std::string& output_path) {
    if (!curl_handle_) {
        std::cerr << "Error: CURL no está inicializado" << std::endl;
        return false;
    }
    
    // Crear directorio si no existe
    std::filesystem::path file_path(output_path);
    std::filesystem::path dir_path = file_path.parent_path();
    
    if (!dir_path.empty() && !std::filesystem::exists(dir_path)) {
        if (!std::filesystem::create_directories(dir_path)) {
            std::cerr << "Error: No se pudo crear el directorio " << dir_path << std::endl;
            return false;
        }
    }
    
    // Abrir archivo para escritura
    std::ofstream file(output_path, std::ios::binary);
    if (!file.is_open()) {
        std::cerr << "Error: No se pudo abrir el archivo " << output_path << std::endl;
        return false;
    }
    
    // Configurar CURL para escribir directamente al archivo
    curl_easy_setopt(curl_handle_, CURLOPT_URL, file_url.c_str());
    curl_easy_setopt(curl_handle_, CURLOPT_WRITEDATA, &file);
    curl_easy_setopt(curl_handle_, CURLOPT_WRITEFUNCTION, nullptr); // Usar función por defecto
    
    CURLcode res = curl_easy_perform(curl_handle_);
    file.close();
    
    if (res != CURLE_OK) {
        std::cerr << "Error descargando " << file_url << ": " << curl_easy_strerror(res) << std::endl;
        std::filesystem::remove(output_path); // Eliminar archivo parcial
        return false;
    }
    
    long response_code;
    curl_easy_getinfo(curl_handle_, CURLINFO_RESPONSE_CODE, &response_code);
    
    if (response_code != 200) {
        std::cerr << "Error HTTP " << response_code << " descargando " << file_url << std::endl;
        std::filesystem::remove(output_path);
        return false;
    }
    
    std::cout << "Descargado: " << ExtractFilename(file_url) << std::endl;
    return true;
}

int WebFileDownloader::DownloadFilesFromPage(const std::string& page_url, 
                                            const std::string& file_extension,
                                            const std::string& download_dir) {
    // Obtener contenido de la página
    HttpResponse response = FetchPageContent(page_url);
    
    if (response.response_code != 200) {
        std::cerr << "Error obteniendo la página: " << response.error_message << std::endl;
        return 0;
    }
    
    // Parsear enlaces de archivos
    std::vector<std::string> file_links = ParseFileLinks(response.data, file_extension);
    
    if (file_links.empty()) {
        std::cout << "No se encontraron archivos con extensión '" << file_extension << "'" << std::endl;
        return 0;
    }
    
    // Crear directorio de descarga
    if (!CreateDirectory(download_dir)) {
        std::cerr << "Error: No se pudo crear el directorio " << download_dir << std::endl;
        return 0;
    }
    
    // Descargar cada archivo
    int successful_downloads = 0;
    for (const std::string& file_url : file_links) {
        std::string filename = ExtractFilename(file_url);
        std::string output_path = download_dir + "/" + filename;
        
        if (DownloadFile(file_url, output_path)) {
            successful_downloads++;
        }
    }
    
    return successful_downloads;
}

std::string WebFileDownloader::ResolveUrl(const std::string& base_url, const std::string& relative_url) {
    // Si ya es una URL absoluta, devolverla tal como está
    if (relative_url.find("http://") == 0 || relative_url.find("https://") == 0) {
        return relative_url;
    }
    
    std::string resolved_url = base_url;
    
    // Asegurar que base_url termine con '/'
    if (!resolved_url.empty() && resolved_url.back() != '/') {
        resolved_url += '/';
    }
    
    // Si relative_url comienza con '/', es relativo a la raíz del dominio
    if (!relative_url.empty() && relative_url[0] == '/') {
        // Encontrar la raíz del dominio
        size_t pos = resolved_url.find("://");
        if (pos != std::string::npos) {
            pos = resolved_url.find('/', pos + 3);
            if (pos != std::string::npos) {
                resolved_url = resolved_url.substr(0, pos);
            }
        }
        resolved_url += relative_url;
    } else {
        resolved_url += relative_url;
    }
    
    return resolved_url;
}

bool WebFileDownloader::CreateDirectory(const std::string& path) {
    try {
        return std::filesystem::create_directories(path) || std::filesystem::exists(path);
    } catch (const std::filesystem::filesystem_error& e) {
        std::cerr << "Error creando directorio: " << e.what() << std::endl;
        return false;
    }
}

std::string WebFileDownloader::ExtractFilename(const std::string& url) {
    size_t pos = url.find_last_of('/');
    if (pos != std::string::npos && pos < url.length() - 1) {
        return url.substr(pos + 1);
    }
    return "downloaded_file";
}

} // namespace FileDownloader