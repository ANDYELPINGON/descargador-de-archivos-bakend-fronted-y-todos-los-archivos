const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs').promises;
const path = require('path');
const { URL } = require('url');

/**
 * Clase para descargar archivos desde páginas web
 */
class FileDownloader {
    /**
     * Constructor
     * @param {string} baseUrl - URL base del sitio web
     * @param {Object} options - Opciones de configuración
     */
    constructor(baseUrl, options = {}) {
        this.baseUrl = baseUrl;
        this.userAgent = options.userAgent || 'Mozilla/5.0 (Node.js FileDownloader)';
        this.timeout = options.timeout || 30000;
        
        // Configurar axios
        this.httpClient = axios.create({
            timeout: this.timeout,
            headers: {
                'User-Agent': this.userAgent
            }
        });
    }

    /**
     * Obtiene el contenido HTML de una página
     * @param {string} url - URL de la página
     * @returns {Promise<string>} Contenido HTML
     */
    async fetchPageContent(url) {
        try {
            const response = await this.httpClient.get(url);
            return response.data;
        } catch (error) {
            console.error(`Error obteniendo contenido de ${url}:`, error.message);
            throw error;
        }
    }

    /**
     * Extrae enlaces de archivos con una extensión específica
     * @param {string} htmlContent - Contenido HTML
     * @param {string} fileExtension - Extensión de archivo a buscar
     * @returns {Array<string>} Array de URLs de archivos
     */
    parseFileLinks(htmlContent, fileExtension) {
        const $ = cheerio.load(htmlContent);
        const fileLinks = [];

        $('a[href]').each((index, element) => {
            const href = $(element).attr('href');
            if (href && href.endsWith(fileExtension)) {
                // Convertir URL relativa a absoluta
                const absoluteUrl = this.resolveUrl(this.baseUrl, href);
                fileLinks.push(absoluteUrl);
            }
        });

        return fileLinks;
    }

    /**
     * Descarga un archivo desde una URL
     * @param {string} fileUrl - URL del archivo
     * @param {string} outputPath - Ruta donde guardar el archivo
     * @returns {Promise<boolean>} true si la descarga fue exitosa
     */
    async downloadFile(fileUrl, outputPath) {
        try {
            // Crear directorio si no existe
            const dir = path.dirname(outputPath);
            await fs.mkdir(dir, { recursive: true });

            // Descargar archivo
            const response = await this.httpClient.get(fileUrl, {
                responseType: 'stream'
            });

            // Guardar archivo
            const writer = require('fs').createWriteStream(outputPath);
            response.data.pipe(writer);

            return new Promise((resolve, reject) => {
                writer.on('finish', () => {
                    console.log(`Descargado: ${path.basename(outputPath)}`);
                    resolve(true);
                });
                writer.on('error', reject);
            });

        } catch (error) {
            console.error(`Error descargando ${fileUrl}:`, error.message);
            return false;
        }
    }

    /**
     * Descarga todos los archivos con una extensión específica desde una página
     * @param {string} pageUrl - URL de la página
     * @param {string} fileExtension - Extensión de archivos a buscar
     * @param {string} downloadDir - Directorio donde guardar los archivos
     * @returns {Promise<number>} Número de archivos descargados exitosamente
     */
    async downloadFilesFromPage(pageUrl, fileExtension, downloadDir = 'archivos_js') {
        try {
            // Obtener contenido de la página
            const htmlContent = await this.fetchPageContent(pageUrl);

            // Parsear enlaces de archivos
            const fileLinks = this.parseFileLinks(htmlContent, fileExtension);

            if (fileLinks.length === 0) {
                console.log(`No se encontraron archivos con extensión '${fileExtension}'`);
                return 0;
            }

            console.log(`Encontrados ${fileLinks.length} archivos para descargar`);

            // Descargar cada archivo
            let successfulDownloads = 0;
            for (const fileUrl of fileLinks) {
                const filename = this.extractFilename(fileUrl);
                const outputPath = path.join(downloadDir, filename);

                if (await this.downloadFile(fileUrl, outputPath)) {
                    successfulDownloads++;
                }
            }

            return successfulDownloads;

        } catch (error) {
            console.error('Error en downloadFilesFromPage:', error.message);
            return 0;
        }
    }

    /**
     * Convierte URL relativa a absoluta
     * @param {string} baseUrl - URL base
     * @param {string} relativeUrl - URL relativa
     * @returns {string} URL absoluta
     */
    resolveUrl(baseUrl, relativeUrl) {
        try {
            return new URL(relativeUrl, baseUrl).href;
        } catch (error) {
            console.error('Error resolviendo URL:', error.message);
            return relativeUrl;
        }
    }

    /**
     * Extrae el nombre del archivo de una URL
     * @param {string} url - URL del archivo
     * @returns {string} Nombre del archivo
     */
    extractFilename(url) {
        try {
            const urlObj = new URL(url);
            const pathname = urlObj.pathname;
            const filename = path.basename(pathname);
            return filename || 'downloaded_file';
        } catch (error) {
            return 'downloaded_file';
        }
    }

    /**
     * Descarga archivos de múltiples páginas
     * @param {Array<string>} pageUrls - Array de URLs de páginas
     * @param {string} fileExtension - Extensión de archivos a buscar
     * @param {string} downloadDir - Directorio donde guardar los archivos
     * @returns {Promise<number>} Total de archivos descargados
     */
    async downloadFromMultiplePages(pageUrls, fileExtension, downloadDir = 'archivos_js') {
        let totalDownloads = 0;

        for (const pageUrl of pageUrls) {
            console.log(`\nProcesando página: ${pageUrl}`);
            const downloads = await this.downloadFilesFromPage(pageUrl, fileExtension, downloadDir);
            totalDownloads += downloads;
        }

        return totalDownloads;
    }
}

module.exports = FileDownloader;