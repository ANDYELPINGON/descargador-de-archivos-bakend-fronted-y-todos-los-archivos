const FileDownloader = require('./fileDownloader');

/**
 * Función principal
 */
async function main() {
    console.log('=== Descargador de Archivos JavaScript ===');

    // Configuración
    const baseUrl = 'https://example.com/archives';
    const fileExtension = '.bakent_fronted';
    const downloadDir = 'archivos_js';

    try {
        // Crear instancia del descargador
        const downloader = new FileDownloader(baseUrl, {
            userAgent: 'Mozilla/5.0 (Node.js FileDownloader)',
            timeout: 30000
        });

        console.log(`Buscando archivos con extensión '${fileExtension}' en: ${baseUrl}`);

        // Descargar archivos
        const downloadedCount = await downloader.downloadFilesFromPage(
            baseUrl, 
            fileExtension, 
            downloadDir
        );

        if (downloadedCount > 0) {
            console.log(`✓ Se descargaron exitosamente ${downloadedCount} archivos.`);
        } else {
            console.log('✗ No se descargaron archivos.');
        }

    } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
    }
}

/**
 * Función para descargar desde múltiples páginas
 */
async function downloadFromMultiplePages() {
    console.log('=== Descarga desde Múltiples Páginas ===');

    const pages = [
        'https://example.com/archives',
        'https://example.com/downloads',
        'https://example.com/files'
    ];
    
    const fileExtension = '.bakent_fronted';
    const downloadDir = 'archivos_multiples';

    try {
        const downloader = new FileDownloader('https://example.com');
        
        const totalDownloads = await downloader.downloadFromMultiplePages(
            pages, 
            fileExtension, 
            downloadDir
        );

        console.log(`\n✓ Total de archivos descargados: ${totalDownloads}`);

    } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
    }
}

// Ejecutar función principal si el script se ejecuta directamente
if (require.main === module) {
    // Verificar argumentos de línea de comandos
    const args = process.argv.slice(2);
    
    if (args.includes('--multiple')) {
        downloadFromMultiplePages();
    } else {
        main();
    }
}

module.exports = { main, downloadFromMultiplePages };