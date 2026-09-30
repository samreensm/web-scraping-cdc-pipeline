import os
import scrapy
import boto3
from pathlib import Path
from dotenv import load_dotenv
from books_scraper.items import BookItem

env_path = Path(__file__).resolve().parents[4] / ".env"
load_dotenv(dotenv_path=env_path)


class BooksSpiderSpider(scrapy.Spider):
    name = "books_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        s3_client = boto3.client(
            "s3",
            #endpoint_url=f"http://localhost:{os.getenv('MINIO_PORT')}",
            endpoint_url=f"http://{os.getenv('MINIO_HOST', 'localhost')}:{os.getenv('MINIO_PORT')}",
            aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
            aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
        )

        object_key = "books/books_homepage.html"

        s3_client.put_object(
            Bucket="raw-html",
            Key=object_key,
            Body=response.body,
        )

        self.log(f"Uploaded to MinIO as {object_key}")

        books = response.css("article.product_pod")

        for book in books:
            item = BookItem()
            item["title"] = book.css("h3 a::attr(title)").get()
            item["price"] = book.css("p.price_color::text").get()
            item["availability"] = book.css("p.instock.availability::text").getall()[-1].strip()
            rating_class = book.css("p.star-rating::attr(class)").get()
            item["rating"] = rating_class.split(" ")[-1]
            yield item