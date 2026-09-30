from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    "owner": "you",
    "retries": 1,
}

with DAG(
    dag_id="books_and_jobs_pipeline",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
) as dag:

    scrape_books = BashOperator(
        task_id="scrape_books",
        bash_command="cd /opt/project/scrapers/books_scraper && scrapy crawl books_spider -O books_scraper/books_with_rating.json",
    )

    scrape_jobs = BashOperator(
        task_id="scrape_jobs",
        bash_command="cd /opt/project/scrapers/remoteok_scraper && scrapy crawl remoteok_spider -O jobs.json",
    )

    load_books = BashOperator(
        task_id="load_books",
        bash_command="cd /opt/project/db && cp /opt/project/scrapers/books_scraper/books_scraper/books_with_rating.json . && python load_books.py",
    )

    load_jobs = BashOperator(
        task_id="load_jobs",
        bash_command="cd /opt/project/db && cp /opt/project/scrapers/remoteok_scraper/jobs.json . && python load_jobs.py",
    )

    scrape_books >> load_books
    scrape_jobs >> load_jobs