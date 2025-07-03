# Gazettegram

Gazettegram is a Python scraper for the Maldivian Government Gazette (`gazette.gov.mv`). It automatically fetches, processes, and stores announcements in a local SQLite database, with an option to send Telegram notifications for relevant new posts.

## Setup and Usage

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd Gazettegram
    ```

2.  **Install dependencies using uv:**
    This project uses `uv` for package management.
    ```bash
    uv sync
    ```

3.  **Configure Environment Variables:**
    Create a `.env` file in the project root and add the following variables for Telegram bot integration.
    ```env
    # Telegram Bot Config
    TG_ADMIN_CHATID=<your_admin_chat_id>
    TG_BOT_TOKEN=<your_telegram_bot_token>
    TG_CHAT_ID=<your_target_telegram_channel_id>
    ```

4.  **Review `config.py`:**
    This file contains the main settings for the scraper. Adjust as needed:
    *   `TARGET_GAZETTE_TYPE`: List of gazette categories to scrape.
    *   `MAX_CONCURRENT_REQUESTS`: Number of parallel scraping workers.
    *   `REQUEST_DELAY`: Delay between requests.
    *   `MAX_INDEX_PAGES`: Optional limit on pages to scrape per category.
    *   `KEYWORD_MAP`: Scoring system for classifying announcements.

5.  **Run the Scraper:**
    To start the scraping process, run the `sync.py` script:
    ```bash
    python sync.py
    ```
    The script will fetch new announcements based on your configuration and save them to the `gazette.db` SQLite file.
6.  **[optional] Send Telegram Notifications:**  
    To send Telegram notifications for new announcements, run the `post_telegram.py` script:
    ```bash
    python post_telegram.py
    ```