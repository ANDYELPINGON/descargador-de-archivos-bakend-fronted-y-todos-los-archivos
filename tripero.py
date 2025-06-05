import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
from typing import List, Optional


class FileDownloader:
    """A class for downloading files from web pages."""
    
    def __init__(self, base_url: str, headers: Optional[dict] = None):
        """
        Initialize the FileDownloader.
        
        Args:
            base_url: The base URL of the website
            headers: Optional HTTP headers for requests
        """
        self.base_url = base_url
        self.headers = headers or {'User-Agent': 'Mozilla/5.0'}
    
    def fetch_page_content(self, url: str) -> Optional[str]:
        """
        Fetch the HTML content of a web page.
        
        Args:
            url: The URL to fetch
            
        Returns:
            HTML content as string, or None if request fails
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching page content: {e}")
            return None
    
    def parse_file_links(self, html_content: str, file_extension: str) -> List[str]:
        """
        Parse HTML content to find links with specific file extension.
        
        Args:
            html_content: HTML content to parse
            file_extension: File extension to search for (e.g., '.bakent_fronted')
            
        Returns:
            List of file URLs
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        file_links = []
        
        # Find all anchor tags with href ending in the specified extension
        links = soup.find_all('a', href=lambda x: x and x.endswith(file_extension))
        
        for link in links:
            href = link.get('href')
            if href:
                # Convert relative URLs to absolute URLs
                absolute_url = urljoin(self.base_url, href)
                file_links.append(absolute_url)
        
        return file_links
    
    def download_file(self, file_url: str, download_dir: str) -> bool:
        """
        Download a single file from URL.
        
        Args:
            file_url: URL of the file to download
            download_dir: Directory to save the file
            
        Returns:
            True if download successful, False otherwise
        """
        try:
            response = requests.get(file_url, headers=self.headers)
            response.raise_for_status()
            
            # Extract filename from URL
            filename = os.path.basename(file_url)
            if not filename:
                filename = "downloaded_file"
            
            # Ensure download directory exists
            os.makedirs(download_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(download_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded: {filename}")
            return True
            
        except requests.RequestException as e:
            print(f"Error downloading file {file_url}: {e}")
            return False
        except IOError as e:
            print(f"Error saving file {file_url}: {e}")
            return False
    
    def download_files_from_page(self, url: str, file_extension: str, download_dir: str = "archivos") -> int:
        """
        Download all files with specified extension from a web page.
        
        Args:
            url: URL of the web page to scrape
            file_extension: File extension to look for
            download_dir: Directory to save downloaded files
            
        Returns:
            Number of files successfully downloaded
        """
        # Fetch page content
        html_content = self.fetch_page_content(url)
        if not html_content:
            return 0
        
        # Parse file links
        file_links = self.parse_file_links(html_content, file_extension)
        if not file_links:
            print(f"No files with extension '{file_extension}' found on the page.")
            return 0
        
        # Download each file
        successful_downloads = 0
        for file_url in file_links:
            if self.download_file(file_url, download_dir):
                successful_downloads += 1
        
        return successful_downloads


def main():
    """Main function to run the file downloader."""
    # Configuration
    url = "https://example.com/archives"
    file_extension = ".bakent_fronted"
    download_dir = "archivos"
    
    # Create downloader instance
    downloader = FileDownloader(url)
    
    # Download files
    downloaded_count = downloader.download_files_from_page(url, file_extension, download_dir)
    
    if downloaded_count > 0:
        print(f"Successfully downloaded {downloaded_count} files.")
    else:
        print("No files were downloaded.")


if __name__ == "__main__":
    main()
