package com.filedownloader;

/**
 * Clase principal para ejecutar el descargador de archivos
 */
public class Main {
    public static void main(String[] args) {
        System.out.println("=== Descargador de Archivos Java ===");
        
        // Configuración
        String baseUrl = "https://example.com/archives";
        String fileExtension = ".bakent_fronted";
        String downloadDir = "archivos_java";
        
        FileDownloader downloader = null;
        
        try {
            // Crear instancia del descargador
            downloader = new FileDownloader(baseUrl);
            
            System.out.println("Buscando archivos con extensión '" + fileExtension + 
                             "' en: " + baseUrl);
            
            // Descargar archivos
            int downloadedCount = downloader.downloadFilesFromPage(
                baseUrl, fileExtension, downloadDir);
            
            if (downloadedCount > 0) {
                System.out.println("✓ Se descargaron exitosamente " + downloadedCount + " archivos.");
            } else {
                System.out.println("✗ No se descargaron archivos.");
            }
            
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        } finally {
            if (downloader != null) {
                downloader.shutdown();
            }
        }
    }
    
    /**
     * Método para demostrar descarga desde múltiples páginas
     */
    public static void downloadFromMultiplePages() {
        System.out.println("=== Descarga desde Múltiples Páginas ===");
        
        String[] pages = {
            "https://example.com/archives",
            "https://example.com/downloads", 
            "https://example.com/files"
        };
        
        String fileExtension = ".bakent_fronted";
        String downloadDir = "archivos_multiples_java";
        
        FileDownloader downloader = null;
        
        try {
            downloader = new FileDownloader("https://example.com");
            
            int totalDownloads = 0;
            for (String pageUrl : pages) {
                System.out.println("\nProcesando página: " + pageUrl);
                int downloads = downloader.downloadFilesFromPage(
                    pageUrl, fileExtension, downloadDir);
                totalDownloads += downloads;
            }
            
            System.out.println("\n✓ Total de archivos descargados: " + totalDownloads);
            
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        } finally {
            if (downloader != null) {
                downloader.shutdown();
            }
        }
    }
}