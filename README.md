# Books to Scrape Assessment

This assessment includes two versions that collect 100 books from multiple catalog pages on [books.toscrape.com](https://books.toscrape.com/): a Scrapy spider and a Crawl4AI crawler. They produce separate CSV files.

## Requirements

- Python 3.8 or newer
- Internet access

## Run

From this directory, install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

To run the Scrapy version and create `books.csv`:

```powershell
python scrapper.py
```

To run the Crawl4AI version, first install its Chromium browser once, then launch the script:

```powershell
python -m playwright install chromium
python crawl4ai_scraper.py
```

The Crawl4AI version creates `books_crawl4ai.csv`; the Scrapy version creates `books.csv`. Both CSV files contain `title`, `price`, `availability`, `rating`, `category`, and `product_url` columns.

The Scrapy spider uses Scrapy for HTTP requests, CSS-selector parsing, pagination, retries, and feed export. The Crawl4AI version uses its asynchronous browser crawler to fetch pages, then BeautifulSoup for CSS-selector parsing.

## Handling and limitations

- Both versions crawl the first five catalog pages, which contain 100 books, and skip duplicate product URLs.
- Each version waits 0.25 seconds between requests and retries request failures up to three times with backoff.
- Missing product links are skipped. Other missing fields are written as empty values; request errors are logged.
- Product pages are requested individually to obtain each book's category.
- This is a short assessment script, not a production crawler. It does not persist partial results if interrupted, and only the first 100 unique books are collected.

## Challenges

The initial workspace used the filename `scrapper.py` (three consecutive `p` characters in “scrapper”), while an earlier run attempted `scraper.py`. Crawl4AI also requires a Playwright-managed Chromium browser; install it once with the command above before running the Crawl4AI version. The Crawl4AI output is saved separately so running either version does not overwrite the other CSV.