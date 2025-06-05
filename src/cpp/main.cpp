#include "file_downloader.hpp"
#include <iostream>
#include <string>

int main() {
    std::cout << "=== Descargador de Archivos C++ ===" << std::endl;
    
    // Configuración by andydcc
    std::string base_url = "https://example.com/archives";
    std::string file_extension = ".bakent_fronted";
    std::string download_dir = "archivos_cpp";
    
    try {
        // Crear instancia del descargador
        FileDownloader::WebFileDownloader downloader(base_url);
        
        std::cout << "Buscando archivos con extensión '" << file_extension 
                  << "' en: " << base_url << std::endl;
        
        // Descargar archivos
        int downloaded_count = downloader.DownloadFilesFromPage(base_url, file_extension, download_dir);
        
        if (downloaded_count > 0) {
            std::cout << "✓ Se descargaron exitosamente " << downloaded_count << " archivos." << std::endl;
        } else {
            std::cout << "✗ No se descargaron archivos." << std::endl;
        }
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
