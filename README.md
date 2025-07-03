# GazetteBot2

GazetteBot2 is a Python-based web scraper designed to automatically fetch, process, and store announcements from the Maldivian Government Gazette website (`gazette.gov.mv`). It uses `httpx` for asynchronous HTTP requests, `BeautifulSoup` for HTML parsing, and `SQLite` for local data storage.

## Features

- **Asynchronous Scraping**: Utilizes `asyncio` and `httpx` for efficient, non-blocking web scraping.
- **Configurable**: Easily configure which gazette types to scrape, set concurrency limits, and define request delays.
- **Data Persistence**: Stores scraped data in a local SQLite database, avoiding duplicate entries for already fetched announcements.
- **Modular Design**: The project is structured into distinct modules for scraping, data management, and type definitions.
- **Extensible**: The database schema and data models can be easily extended to accommodate new data fields.

## Installation and Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd GazetteBot2
    ```

2.  **Create a virtual environment and install dependencies:**
    This project uses `uv` for package management.
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install uv
    uv pip install -r requirements.txt
    ```

## Usage

### Configuration

The `config.py` file contains all the runtime settings for the scraper. You can modify this file to change the scraper's behavior.

- `TARGET_GAZETTE_TYPE`: A list of `GazetteType` enums to be scraped.
- `BASE_URL`: The base URL of the gazette website.
- `DATABASE_PATH`: The path to the SQLite database file.
- `MAX_CONCURRENT_REQUESTS`: The number of parallel requests to the server.
- `REQUEST_DELAY`: The delay in seconds between batches of requests.
- `MAX_INDEX_PAGES`: An optional limit on the number of index pages to fetch for each gazette type.

### Running the Scraper

To start the scraping process, run the `sync.py` script:

```bash
python -m sync
```

The script will fetch the specified gazette types, parse the announcements, and store them in the database.

### Manual Scraping

You can also fetch and display a single announcement by running the `scraper.py` script directly with an `iulaan_id`:

```bash
python -m api.scraper <iulaan_id>
```

## Project Structure

```
.
├── api/
│   ├── gazette_types.py  # Defines the data models and enums
│   └── scraper.py        # Core scraping and parsing logic
├── data/
│   └── gazettedb.py      # Database management (SQLite)
├── config.py             # Configuration settings
├── sync.py               # Main script to run the scraper
├── pyproject.toml        # Project metadata and dependencies
└── README.md             # This file
```

## Dependencies

- `beautifulsoup4`: For parsing HTML.
- `httpx`: For making asynchronous HTTP requests.
- `python-dotenv`: For managing environment variables (if needed).
