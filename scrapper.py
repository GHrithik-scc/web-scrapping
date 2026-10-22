
import scrapy
from scrapy.crawler import CrawlerProcess


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 0.25,
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 3,
        "RETRY_HTTP_CODES": [429, 500, 502, 503, 504],
        "FEEDS": {
            "books.csv": {
                "format": "csv",
                "overwrite": True,
                "encoding": "utf-8-sig",
                "fields": [
                    "title",
                    "price",
                    "availability",
                    "rating",
                    "category",
                    "product_url",
                ],
            }
        },
    }

    def parse(self, response):
        page_number = response.meta.get("page_number", 1)

        for book in response.css("article.product_pod"):
            relative_url = book.css("h3 a::attr(href)").get()
            if not relative_url:
                continue

            yield response.follow(
                relative_url,
                callback=self.parse_book,
                meta={
                    "title": book.css("h3 a::attr(title)").get(default="").strip(),
                    "price": book.css(".price_color::text").get(default="").strip(),
                    "availability": " ".join(book.css(".availability ::text").getall()).strip(),
                    "rating": next(
                        (
                            value
                            for value in book.css("p.star-rating::attr(class)").get(default="").split()
                            if value != "star-rating"
                        ),
                        "",
                    ),
                },
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page and page_number < 5:
            yield response.follow(
                next_page,
                callback=self.parse,
                meta={"page_number": page_number + 1},
            )

    def parse_book(self, response):
        category = response.css("ul.breadcrumb li:nth-child(3) a::text").get(default="")
        yield {
            "title": response.meta.get("title", ""),
            "price": response.meta.get("price", ""),
            "availability": response.meta.get("availability", ""),
            "rating": response.meta.get("rating", ""),
            "category": category.strip(),
            "product_url": response.url,
        }


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(BooksSpider)
    process.start()
