import os
import json
import boto3
from pathlib import Path
from datetime import datetime, timezone
import scrapy
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[4] / ".env"
load_dotenv(dotenv_path=env_path)


class RemoteokSpiderSpider(scrapy.Spider):
    name = "remoteok_spider"
    allowed_domains = ["remoteok.com"]
    start_urls = ["https://remoteok.com/api"]
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    def parse(self, response):
        s3_client = boto3.client(
            "s3",
            endpoint_url=f"http://{os.getenv('MINIO_HOST', 'localhost')}:{os.getenv('MINIO_PORT')}",
            aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
            aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
        )

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        object_key = f"jobs/{today}/remoteok_raw.json"

        s3_client.put_object(
            Bucket="raw-html",
            Key=object_key,
            Body=response.body,
        )

        self.log(f"Uploaded raw feed to MinIO as {object_key}")

        data = response.json()
        jobs = data[1:21]

        for job in jobs:
            yield {
                "job_id": job.get("id"),
                "title": job.get("position"),
                "company": job.get("company"),
                "location": job.get("location"),
                "tags": ", ".join(job.get("tags", [])),
                "apply_url": job.get("url"),
                "posted_date": job.get("date"),
            }