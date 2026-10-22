import asyncio
import csv
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig


BASE_URL = "https://books.toscrape.com/"
START_URL = urljoin(BASE_URL, "catalogue/page-1.html")
OUTPUT_FILE = "books_crawl4ai.csv"
TARGET_BOOKS = 100
MAX_LISTING_PAGES = 5
REQUEST_DELAY_SECONDS = 0.25
CSV_FIELDS = ["title", "price", "availability", "rating", "category", "product_url"]


async def fetch_html(crawler, url, run_config):
    for attempt in range(1, 4):
        await asyncio.sleep(REQUEST_DELAY_SECONDS)
        error_message = "Crawl returned no HTML"
        try:
            result = await crawler.arun(url=url, config=run_config)
            if result.success and result.html:
                return result.html
            error_message = result.error_message or error_message
        except Exception as error:
            error_message = str(error)

        print(f"Attempt {attempt}/3 failed for {url}: {error_message}")
        if attempt < 3:
            await asyncio.sleep(attempt)
    return None


def text_or_empty(element):
    return " ".join(element.stripped_strings) if element else ""


async def scrape_books():
    books = []
    seen_urls = set()
    browser_config = BrowserConfig(headless=True)
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, page_timeout=30000)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        listing_url = START_URL
        page_number = 0

        while listing_url and page_number < MAX_LISTING_PAGES and len(books) < TARGET_BOOKS:
            listing_html = await fetch_html(crawler, listing_url, run_config)
            if not listing_html:
                break

            listing = BeautifulSoup(listing_html, "html.parser")
            for card in listing.select("article.product_pod"):
                anchor = card.select_one("h3 a[href]")
                if anchor is None:
                    continue

                product_url = urljoin(listing_url, anchor["href"])
                if product_url in seen_urls:
                    continue
                seen_urls.add(product_url)

                rating_element = card.select_one("p.star-rating")
                rating_classes = rating_element.get("class", []) if rating_element else []
                rating = next((name for name in rating_classes if name != "star-rating"), "")
                book = {
                    "title": anchor.get("title", "").strip(),
                    "price": text_or_empty(card.select_one(".price_color")),
                    "availability": text_or_empty(card.select_one(".availability")),
                    "rating": rating,
                    "category": "",
                    "product_url": product_url,
                }

                detail_html = await fetch_html(crawler, product_url, run_config)
                if detail_html:
                    detail = BeautifulSoup(detail_html, "html.parser")
                    category = detail.select_one("ul.breadcrumb li:nth-child(3) a")
                    book["category"] = text_or_empty(category)

                books.append(book)
                print(f"Collected {len(books)}: {book['title'] or product_url}")
                if len(books) >= TARGET_BOOKS:
                    break

            next_link = listing.select_one("li.next a[href]")
            listing_url = urljoin(listing_url, next_link["href"]) if next_link else ""
            page_number += 1

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(books)

    print(f"Saved {len(books)} unique books to {OUTPUT_FILE}")
    if len(books) < TARGET_BOOKS:
        print(f"Warning: collected {len(books)} books; target was {TARGET_BOOKS}.")


if __name__ == "__main__":
    asyncio.run(scrape_books())