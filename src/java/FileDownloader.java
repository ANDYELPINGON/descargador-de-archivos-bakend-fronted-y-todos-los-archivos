package com.filedownloader;

import java.io.*;
import java.net.*;
import java.nio.file.*;
import java.util.*;
import java.util.regex.*;
import java.util.concurrent.*;

/**
 * Clase principal para descargar archivos desde páginas web
 */
public class FileDownloader {
    private final String baseUrl;
    private final String userAgent;
    private final int timeout;
    private final ExecutorService executorService;

    /**
     * Constructor
     * @param baseUrl URL base del sitio web
     */
    public FileDownloader(String baseUrl) {
        this(baseUrl, "Mozilla/5.0 (Java FileDownloader)", 30000);
    }

    /**
     * Constructor con parámetros personalizados
     * @param baseUrl URL base del sitio web
     * @param userAgent User agent para las peticiones HTTP
     * @param timeout Timeout en milisegundos
     */
    public FileDownloader(String baseUrl, String userAgent, int timeout) {
        this.baseUrl = baseUrl;
        this.userAgent = userAgent;
        this.timeout = timeout;
        this.executorService = Executors.newFixedThreadPool(5);
    }

    /**
     * Obtiene el contenido HTML de una página
     * @param url URL de la página
     * @return Contenido HTML como String
     * @throws IOException Si hay error en la conexión
     */
    public String fetchPageContent(String url) throws IOException {
        HttpURLConnection connection = null;
        try {
            URL urlObj = new URL(url);
            connection = (HttpURLConnection) urlObj.openConnection();
            
            // Configurar conexión
            connection.setRequestMethod("GET");
            connection.setRequestProperty("User-Agent", userAgent);
            connection.setConnectTimeout(timeout);
            connection.setReadTimeout(timeout);
            
            // Verificar código de respuesta
            int responseCode = connection.getResponseCode();
            if (responseCode != HttpURLConnection.HTTP_OK) {
                throw new IOException("HTTP Error: " + responseCode);
            }
            
            // Leer contenido
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(connection.getInputStream()))) {
                StringBuilder content = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    content.append(line).append("\n");
                }
                return content.toString();
            }
            
        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }
    }

    /**
     * Extrae enlaces de archivos con una extensión específica
     * @param htmlContent Contenido HTML
     * @param fileExtension Extensión de archivo a buscar
     * @return Lista de URLs de archivos
     */
    public List<String> parseFileLinks(String htmlContent, String fileExtension) {
        List<String> fileLinks = new ArrayList<>();
        
        // Expresión regular para encontrar enlaces href
        String regex = "href\\s*=\\s*['\"]\\s*([^'\"]*" + Pattern.quote(fileExtension) + "[^'\"]*)\\s*['\"]";
        Pattern pattern = Pattern.compile(regex, Pattern.CASE_INSENSITIVE);
        Matcher matcher = pattern.matcher(htmlContent);
        
        while (matcher.find()) {
            String link = matcher.group(1);
            String absoluteUrl = resolveUrl(baseUrl, link);
            fileLinks.add(absoluteUrl);
        }
        
        return fileLinks;
    }

    /**
     * Descarga un archivo desde una URL
     * @param fileUrl URL del archivo
     * @param outputPath Ruta donde guardar el archivo
     * @return true si la descarga fue exitosa
     */
    public boolean downloadFile(String fileUrl, String outputPath) {
        HttpURLConnection connection = null;
        try {
            // Crear directorio si no existe
            Path filePath = Paths.get(outputPath);
            Path parentDir = filePath.getParent();
            if (parentDir != null && !Files.exists(parentDir)) {
                Files.createDirectories(parentDir);
            }
            
            // Establecer conexión
            URL url = new URL(fileUrl);
            connection = (HttpURLConnection) url.openConnection();
            connection.setRequestProperty("User-Agent", userAgent);
            connection.setConnectTimeout(timeout);
            connection.setReadTimeout(timeout);
            
            // Verificar código de respuesta
            int responseCode = connection.getResponseCode();
            if (responseCode != HttpURLConnection.HTTP_OK) {
                System.err.println("Error HTTP " + responseCode + " descargando " + fileUrl);
                return false;
            }
            
            // Descargar archivo
            try (InputStream inputStream = connection.getInputStream();
                 FileOutputStream outputStream = new FileOutputStream(outputPath)) {
                
                byte[] buffer = new byte[8192];
                int bytesRead;
                while ((bytesRead = inputStream.read(buffer)) != -1) {
                    outputStream.write(buffer, 0, bytesRead);
                }
            }
            
            System.out.println("Descargado: " + extractFilename(fileUrl));
            return true;
            
        } catch (IOException e) {
            System.err.println("Error descargando " + fileUrl + ": " + e.getMessage());
            return false;
        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }
    }

    /**
     * Descarga todos los archivos con una extensión específica desde una página
     * @param pageUrl URL de la página
     * @param fileExtension Extensión de archivos a buscar
     * @param downloadDir Directorio donde guardar los archivos
     * @return Número de archivos descargados exitosamente
     */
    public int downloadFilesFromPage(String pageUrl, String fileExtension, String downloadDir) {
        try {
            // Obtener contenido de la página
            String htmlContent = fetchPageContent(pageUrl);
            
            // Parsear enlaces de archivos
            List<String> fileLinks = parseFileLinks(htmlContent, fileExtension);
            
            if (fileLinks.isEmpty()) {
                System.out.println("No se encontraron archivos con extensión '" + fileExtension + "'");
                return 0;
            }
            
            System.out.println("Encontrados " + fileLinks.size() + " archivos para descargar");
            
            // Crear directorio de descarga
            Path downloadPath = Paths.get(downloadDir);
            if (!Files.exists(downloadPath)) {
                Files.createDirectories(downloadPath);
            }
            
            // Descargar archivos en paralelo
            List<CompletableFuture<Boolean>> futures = new ArrayList<>();
            
            for (String fileUrl : fileLinks) {
                String filename = extractFilename(fileUrl);
                String outputPath = Paths.get(downloadDir, filename).toString();
                
                CompletableFuture<Boolean> future = CompletableFuture.supplyAsync(
                    () -> downloadFile(fileUrl, outputPath), executorService);
                futures.add(future);
            }
            
            // Esperar a que terminen todas las descargas
            int successfulDownloads = 0;
            for (CompletableFuture<Boolean> future : futures) {
                try {
                    if (future.get()) {
                        successfulDownloads++;
                    }
                } catch (InterruptedException | ExecutionException e) {
                    System.err.println("Error en descarga paralela: " + e.getMessage());
                }
            }
            
            return successfulDownloads;
            
        } catch (IOException e) {
            System.err.println("Error obteniendo la página: " + e.getMessage());
            return 0;
        }
    }

    /**
     * Convierte URL relativa a absoluta
     * @param baseUrl URL base
     * @param relativeUrl URL relativa
     * @return URL absoluta
     */
    public static String resolveUrl(String baseUrl, String relativeUrl) {
        try {
            URI baseUri = new URI(baseUrl);
            URI resolvedUri = baseUri.resolve(relativeUrl);
            return resolvedUri.toString();
        } catch (URISyntaxException e) {
            System.err.println("Error resolviendo URL: " + e.getMessage());
            return relativeUrl;
        }
    }

    /**
     * Extrae el nombre del archivo de una URL
     * @param url URL del archivo
     * @return Nombre del archivo
     */
    public static String extractFilename(String url) {
        try {
            URI uri = new URI(url);
            String path = uri.getPath();
            if (path != null && !path.isEmpty()) {
                String[] parts = path.split("/");
                if (parts.length > 0) {
                    String filename = parts[parts.length - 1];
                    return filename.isEmpty() ? "downloaded_file" : filename;
                }
            }
        } catch (URISyntaxException e) {
            System.err.println("Error extrayendo nombre de archivo: " + e.getMessage());
        }
        return "downloaded_file";
    }

    /**
     * Cierra el executor service
     */
    public void shutdown() {
        executorService.shutdown();
        try {
            if (!executorService.awaitTermination(60, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
        } catch (InterruptedException e) {
            executorService.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}