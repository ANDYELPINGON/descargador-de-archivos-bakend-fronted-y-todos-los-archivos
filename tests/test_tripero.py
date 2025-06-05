import pytest
import requests
from unittest.mock import Mock, patch, mock_open
import os
import tempfile
import shutil
from bs4 import BeautifulSoup

# Import the module to test
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tripero import FileDownloader


class TestFileDownloader:
    """Test suite for FileDownloader class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.base_url = "https://example.com"
        self.downloader = FileDownloader(self.base_url)
        self.test_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_init_default_headers(self):
        """Test FileDownloader initialization with default headers."""
        downloader = FileDownloader("https://test.com")
        assert downloader.base_url == "https://test.com"
        assert downloader.headers == {'User-Agent': 'Mozilla/5.0'}
    
    def test_init_custom_headers(self):
        """Test FileDownloader initialization with custom headers."""
        custom_headers = {'User-Agent': 'Custom Agent', 'Accept': 'text/html'}
        downloader = FileDownloader("https://test.com", custom_headers)
        assert downloader.base_url == "https://test.com"
        assert downloader.headers == custom_headers
    
    @patch('tripero.requests.get')
    def test_fetch_page_content_success(self, mock_get):
        """Test successful page content fetching."""
        # Mock successful response
        mock_response = Mock()
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.downloader.fetch_page_content("https://example.com/test")
        
        assert result == "<html><body>Test content</body></html>"
        mock_get.assert_called_once_with("https://example.com/test", headers=self.downloader.headers)
    
    @patch('tripero.requests.get')
    def test_fetch_page_content_failure(self, mock_get):
        """Test page content fetching failure."""
        # Mock failed response
        mock_get.side_effect = requests.RequestException("Connection error")
        
        result = self.downloader.fetch_page_content("https://example.com/test")
        
        assert result is None
        mock_get.assert_called_once_with("https://example.com/test", headers=self.downloader.headers)
    
    def test_parse_file_links_with_files(self):
        """Test parsing HTML content with file links."""
        html_content = """
        <html>
            <body>
                <a href="file1.bakent_fronted">File 1</a>
                <a href="/downloads/file2.bakent_fronted">File 2</a>
                <a href="https://other.com/file3.bakent_fronted">File 3</a>
                <a href="document.pdf">PDF File</a>
                <a href="image.jpg">Image</a>
            </body>
        </html>
        """
        
        result = self.downloader.parse_file_links(html_content, ".bakent_fronted")
        
        expected = [
            "https://example.com/file1.bakent_fronted",
            "https://example.com/downloads/file2.bakent_fronted",
            "https://other.com/file3.bakent_fronted"
        ]
        assert result == expected
    
    def test_parse_file_links_no_files(self):
        """Test parsing HTML content with no matching file links."""
        html_content = """
        <html>
            <body>
                <a href="document.pdf">PDF File</a>
                <a href="image.jpg">Image</a>
                <a href="page.html">HTML Page</a>
            </body>
        </html>
        """
        
        result = self.downloader.parse_file_links(html_content, ".bakent_fronted")
        
        assert result == []
    
    def test_parse_file_links_empty_html(self):
        """Test parsing empty HTML content."""
        html_content = "<html><body></body></html>"
        
        result = self.downloader.parse_file_links(html_content, ".bakent_fronted")
        
        assert result == []
    
    def test_parse_file_links_malformed_html(self):
        """Test parsing malformed HTML content."""
        html_content = "<html><body><a href='file.bakent_fronted'>File</a>"
        
        result = self.downloader.parse_file_links(html_content, ".bakent_fronted")
        
        assert len(result) == 1
        assert result[0] == "https://example.com/file.bakent_fronted"
    
    @patch('tripero.requests.get')
    @patch('tripero.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_file_success(self, mock_file, mock_makedirs, mock_get):
        """Test successful file download."""
        # Mock successful response
        mock_response = Mock()
        mock_response.content = b"file content"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.downloader.download_file("https://example.com/file.bakent_fronted", self.test_dir)
        
        assert result is True
        mock_get.assert_called_once_with("https://example.com/file.bakent_fronted", headers=self.downloader.headers)
        mock_makedirs.assert_called_once_with(self.test_dir, exist_ok=True)
        mock_file.assert_called_once()
        mock_file().write.assert_called_once_with(b"file content")
    
    @patch('tripero.requests.get')
    def test_download_file_request_failure(self, mock_get):
        """Test file download with request failure."""
        mock_get.side_effect = requests.RequestException("Network error")
        
        result = self.downloader.download_file("https://example.com/file.bakent_fronted", self.test_dir)
        
        assert result is False
        mock_get.assert_called_once_with("https://example.com/file.bakent_fronted", headers=self.downloader.headers)
    
    @patch('tripero.requests.get')
    @patch('tripero.os.makedirs')
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_download_file_io_error(self, mock_file, mock_makedirs, mock_get):
        """Test file download with IO error."""
        # Mock successful response
        mock_response = Mock()
        mock_response.content = b"file content"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.downloader.download_file("https://example.com/file.bakent_fronted", self.test_dir)
        
        assert result is False
    
    def test_download_file_no_filename(self):
        """Test download file with URL that has no filename."""
        with patch('tripero.requests.get') as mock_get, \
             patch('tripero.os.makedirs') as mock_makedirs, \
             patch('builtins.open', mock_open()) as mock_file:
            
            mock_response = Mock()
            mock_response.content = b"file content"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = self.downloader.download_file("https://example.com/", self.test_dir)
            
            assert result is True
            # Should use default filename
            expected_path = os.path.join(self.test_dir, "downloaded_file")
            mock_file.assert_called_with(expected_path, 'wb')
    
    @patch.object(FileDownloader, 'fetch_page_content')
    @patch.object(FileDownloader, 'parse_file_links')
    @patch.object(FileDownloader, 'download_file')
    def test_download_files_from_page_success(self, mock_download, mock_parse, mock_fetch):
        """Test successful download of files from page."""
        # Mock the method calls
        mock_fetch.return_value = "<html>content</html>"
        mock_parse.return_value = ["https://example.com/file1.bakent_fronted", "https://example.com/file2.bakent_fronted"]
        mock_download.side_effect = [True, True]
        
        result = self.downloader.download_files_from_page("https://example.com/page", ".bakent_fronted", self.test_dir)
        
        assert result == 2
        mock_fetch.assert_called_once_with("https://example.com/page")
        mock_parse.assert_called_once_with("<html>content</html>", ".bakent_fronted")
        assert mock_download.call_count == 2
    
    @patch.object(FileDownloader, 'fetch_page_content')
    def test_download_files_from_page_fetch_failure(self, mock_fetch):
        """Test download files when page fetch fails."""
        mock_fetch.return_value = None
        
        result = self.downloader.download_files_from_page("https://example.com/page", ".bakent_fronted", self.test_dir)
        
        assert result == 0
        mock_fetch.assert_called_once_with("https://example.com/page")
    
    @patch.object(FileDownloader, 'fetch_page_content')
    @patch.object(FileDownloader, 'parse_file_links')
    def test_download_files_from_page_no_files(self, mock_parse, mock_fetch):
        """Test download files when no files are found."""
        mock_fetch.return_value = "<html>content</html>"
        mock_parse.return_value = []
        
        result = self.downloader.download_files_from_page("https://example.com/page", ".bakent_fronted", self.test_dir)
        
        assert result == 0
        mock_fetch.assert_called_once_with("https://example.com/page")
        mock_parse.assert_called_once_with("<html>content</html>", ".bakent_fronted")
    
    @patch.object(FileDownloader, 'fetch_page_content')
    @patch.object(FileDownloader, 'parse_file_links')
    @patch.object(FileDownloader, 'download_file')
    def test_download_files_from_page_partial_success(self, mock_download, mock_parse, mock_fetch):
        """Test download files with partial success."""
        mock_fetch.return_value = "<html>content</html>"
        mock_parse.return_value = ["https://example.com/file1.bakent_fronted", "https://example.com/file2.bakent_fronted"]
        mock_download.side_effect = [True, False]  # First succeeds, second fails
        
        result = self.downloader.download_files_from_page("https://example.com/page", ".bakent_fronted", self.test_dir)
        
        assert result == 1
        assert mock_download.call_count == 2


class TestIntegration:
    """Integration tests for the FileDownloader."""
    
    def test_parse_real_html(self):
        """Test parsing with real HTML structure."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Downloads</title></head>
        <body>
            <h1>Available Files</h1>
            <ul>
                <li><a href="data/file1.bakent_fronted">Data File 1</a></li>
                <li><a href="/absolute/file2.bakent_fronted">Data File 2</a></li>
                <li><a href="https://external.com/file3.bakent_fronted">External File</a></li>
                <li><a href="readme.txt">Readme</a></li>
            </ul>
        </body>
        </html>
        """
        
        downloader = FileDownloader("https://example.com/downloads/")
        result = downloader.parse_file_links(html_content, ".bakent_fronted")
        
        expected = [
            "https://example.com/downloads/data/file1.bakent_fronted",
            "https://example.com/absolute/file2.bakent_fronted",
            "https://external.com/file3.bakent_fronted"
        ]
        assert result == expected
    
    def test_edge_cases(self):
        """Test various edge cases."""
        downloader = FileDownloader("https://example.com")
        
        # Test with None href
        html_with_none = '<a>No href</a><a href="">Empty href</a>'
        result = downloader.parse_file_links(html_with_none, ".bakent_fronted")
        assert result == []
        
        # Test with special characters in URL
        html_with_special = '<a href="file%20with%20spaces.bakent_fronted">File</a>'
        result = downloader.parse_file_links(html_with_special, ".bakent_fronted")
        assert len(result) == 1
        assert "file%20with%20spaces.bakent_fronted" in result[0]


class TestMainFunction:
    """Test the main function."""
    
    @patch.object(FileDownloader, 'download_files_from_page')
    def test_main_success(self, mock_download):
        """Test main function with successful downloads."""
        mock_download.return_value = 3
        
        # Import and run main
        from tripero import main
        
        # Capture stdout to verify print statements
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            main()
            output = captured_output.getvalue()
            assert "Successfully downloaded 3 files." in output
        finally:
            sys.stdout = sys.__stdout__
        
        mock_download.assert_called_once_with(
            "https://example.com/archives", 
            ".bakent_fronted", 
            "archivos"
        )
    
    @patch.object(FileDownloader, 'download_files_from_page')
    def test_main_no_downloads(self, mock_download):
        """Test main function with no downloads."""
        mock_download.return_value = 0
        
        # Import and run main
        from tripero import main
        
        # Capture stdout to verify print statements
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            main()
            output = captured_output.getvalue()
            assert "No files were downloaded." in output
        finally:
            sys.stdout = sys.__stdout__
        
        mock_download.assert_called_once_with(
            "https://example.com/archives", 
            ".bakent_fronted", 
            "archivos"
        )


if __name__ == "__main__":
    pytest.main([__file__])