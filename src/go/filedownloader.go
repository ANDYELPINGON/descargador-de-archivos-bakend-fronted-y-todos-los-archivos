package main

import (
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"path"
	"path/filepath"
	"regexp"
	"strings"
	"sync"
	"time"
)

// FileDownloader estructura principal para descargar archivos
type FileDownloader struct {
	BaseURL   string
	UserAgent string
	Timeout   time.Duration
	Client    *http.Client
}

// NewFileDownloader crea una nueva instancia del descargador
func NewFileDownloader(baseURL string) *FileDownloader {
	return &FileDownloader{
		BaseURL:   baseURL,
		UserAgent: "Mozilla/5.0 (Go FileDownloader)",
		Timeout:   30 * time.Second,
		Client: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// NewFileDownloaderWithOptions crea una instancia con opciones personalizadas
func NewFileDownloaderWithOptions(baseURL, userAgent string, timeout time.Duration) *FileDownloader {
	return &FileDownloader{
		BaseURL:   baseURL,
		UserAgent: userAgent,
		Timeout:   timeout,
		Client: &http.Client{
			Timeout: timeout,
		},
	}
}

// FetchPageContent obtiene el contenido HTML de una página
func (fd *FileDownloader) FetchPageContent(url string) (string, error) {
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return "", fmt.Errorf("error creando request: %v", err)
	}

	req.Header.Set("User-Agent", fd.UserAgent)

	resp, err := fd.Client.Do(req)
	if err != nil {
		return "", fmt.Errorf("error obteniendo página: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("HTTP error: %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("error leyendo contenido: %v", err)
	}

	return string(body), nil
}

// ParseFileLinks extrae enlaces de archivos con una extensión específica
func (fd *FileDownloader) ParseFileLinks(htmlContent, fileExtension string) []string {
	var fileLinks []string

	// Expresión regular para encontrar enlaces href
	pattern := fmt.Sprintf(`href\s*=\s*['"]([^'"]*%s[^'"]*)['"]`, regexp.QuoteMeta(fileExtension))
	re := regexp.MustCompile(pattern)

	matches := re.FindAllStringSubmatch(htmlContent, -1)
	for _, match := range matches {
		if len(match) > 1 {
			link := match[1]
			absoluteURL := fd.ResolveURL(fd.BaseURL, link)
			fileLinks = append(fileLinks, absoluteURL)
		}
	}

	return fileLinks
}

// DownloadFile descarga un archivo desde una URL
func (fd *FileDownloader) DownloadFile(fileURL, outputPath string) error {
	// Crear directorio si no existe
	dir := filepath.Dir(outputPath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return fmt.Errorf("error creando directorio: %v", err)
	}

	// Crear request
	req, err := http.NewRequest("GET", fileURL, nil)
	if err != nil {
		return fmt.Errorf("error creando request: %v", err)
	}

	req.Header.Set("User-Agent", fd.UserAgent)

	// Realizar request
	resp, err := fd.Client.Do(req)
	if err != nil {
		return fmt.Errorf("error descargando archivo: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("HTTP error: %d", resp.StatusCode)
	}

	// Crear archivo
	file, err := os.Create(outputPath)
	if err != nil {
		return fmt.Errorf("error creando archivo: %v", err)
	}
	defer file.Close()

	// Copiar contenido
	_, err = io.Copy(file, resp.Body)
	if err != nil {
		return fmt.Errorf("error escribiendo archivo: %v", err)
	}

	fmt.Printf("Descargado: %s\n", ExtractFilename(fileURL))
	return nil
}

// DownloadFilesFromPage descarga todos los archivos con una extensión específica desde una página
func (fd *FileDownloader) DownloadFilesFromPage(pageURL, fileExtension, downloadDir string) int {
	// Obtener contenido de la página
	htmlContent, err := fd.FetchPageContent(pageURL)
	if err != nil {
		fmt.Printf("Error obteniendo la página: %v\n", err)
		return 0
	}

	// Parsear enlaces de archivos
	fileLinks := fd.ParseFileLinks(htmlContent, fileExtension)

	if len(fileLinks) == 0 {
		fmt.Printf("No se encontraron archivos con extensión '%s'\n", fileExtension)
		return 0
	}

	fmt.Printf("Encontrados %d archivos para descargar\n", len(fileLinks))

	// Crear directorio de descarga
	if err := os.MkdirAll(downloadDir, 0755); err != nil {
		fmt.Printf("Error creando directorio: %v\n", err)
		return 0
	}

	// Descargar archivos en paralelo
	var wg sync.WaitGroup
	var mu sync.Mutex
	successfulDownloads := 0

	for _, fileURL := range fileLinks {
		wg.Add(1)
		go func(url string) {
			defer wg.Done()

			filename := ExtractFilename(url)
			outputPath := filepath.Join(downloadDir, filename)

			if err := fd.DownloadFile(url, outputPath); err == nil {
				mu.Lock()
				successfulDownloads++
				mu.Unlock()
			} else {
				fmt.Printf("Error descargando %s: %v\n", url, err)
			}
		}(fileURL)
	}

	wg.Wait()
	return successfulDownloads
}

// ResolveURL convierte URL relativa a absoluta
func (fd *FileDownloader) ResolveURL(baseURL, relativeURL string) string {
	base, err := url.Parse(baseURL)
	if err != nil {
		return relativeURL
	}

	relative, err := url.Parse(relativeURL)
	if err != nil {
		return relativeURL
	}

	resolved := base.ResolveReference(relative)
	return resolved.String()
}

// ExtractFilename extrae el nombre del archivo de una URL
func ExtractFilename(fileURL string) string {
	u, err := url.Parse(fileURL)
	if err != nil {
		return "downloaded_file"
	}

	filename := path.Base(u.Path)
	if filename == "." || filename == "/" {
		return "downloaded_file"
	}

	return filename
}

// DownloadFromMultiplePages descarga archivos de múltiples páginas
func (fd *FileDownloader) DownloadFromMultiplePages(pageURLs []string, fileExtension, downloadDir string) int {
	totalDownloads := 0

	for _, pageURL := range pageURLs {
		fmt.Printf("\nProcesando página: %s\n", pageURL)
		downloads := fd.DownloadFilesFromPage(pageURL, fileExtension, downloadDir)
		totalDownloads += downloads
	}

	return totalDownloads
}

func main() {
	fmt.Println("=== Descargador de Archivos Go ===")

	// Configuración
	baseURL := "https://example.com/archives"
	fileExtension := ".bakent_fronted"
	downloadDir := "archivos_go"

	// Crear instancia del descargador
	downloader := NewFileDownloader(baseURL)

	fmt.Printf("Buscando archivos con extensión '%s' en: %s\n", fileExtension, baseURL)

	// Descargar archivos
	downloadedCount := downloader.DownloadFilesFromPage(baseURL, fileExtension, downloadDir)

	if downloadedCount > 0 {
		fmt.Printf("✓ Se descargaron exitosamente %d archivos.\n", downloadedCount)
	} else {
		fmt.Println("✗ No se descargaron archivos.")
	}
}

// DemoMultiplePages demuestra descarga desde múltiples páginas
func DemoMultiplePages() {
	fmt.Println("=== Descarga desde Múltiples Páginas ===")

	pages := []string{
		"https://example.com/archives",
		"https://example.com/downloads",
		"https://example.com/files",
	}

	fileExtension := ".bakent_fronted"
	downloadDir := "archivos_multiples_go"

	downloader := NewFileDownloader("https://example.com")

	totalDownloads := downloader.DownloadFromMultiplePages(pages, fileExtension, downloadDir)

	fmt.Printf("\n✓ Total de archivos descargados: %d\n", totalDownloads)
}