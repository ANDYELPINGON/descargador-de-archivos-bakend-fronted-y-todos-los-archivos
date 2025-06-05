# File Downloader

A Python script for downloading files with specific extensions from web pages.

## Features

- Download files with custom extensions from web pages
- Robust error handling for network and file operations
- Proper URL handling (relative to absolute conversion)
- Configurable headers for HTTP requests
- Comprehensive test suite with 99% coverage

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### As a Script
```bash
python tripero.py
```

### As a Module
```python
from tripero import FileDownloader

# Create downloader instance
downloader = FileDownloader("https://example.com")

# Download files from a page
count = downloader.download_files_from_page(
    "https://example.com/downloads", 
    ".bakent_fronted", 
    "downloads"
)
print(f"Downloaded {count} files")
```

## Testing

Run all tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=tripero --cov-report=term-missing
```

Run specific test class:
```bash
pytest tests/test_tripero.py::TestFileDownloader
```

## Test Coverage

The project maintains 99% test coverage, testing all major functionality including:

- HTTP request handling and error cases
- HTML parsing and link extraction
- File download operations
- URL handling (relative/absolute conversion)
- Error handling for network and I/O operations
- Integration scenarios

## Project Structure

```
.
├── tripero.py          # Main module with FileDownloader class
├── tests/
│   ├── __init__.py
│   └── test_tripero.py # Comprehensive test suite
├── requirements.txt    # Project dependencies
├── pytest.ini        # Test configuration
└── README.md          # This file
```

## Code Quality

- Type hints for better code documentation
- Comprehensive docstrings
- Error handling for all external operations
- Modular design for easy testing and maintenance
- Following Python best practices