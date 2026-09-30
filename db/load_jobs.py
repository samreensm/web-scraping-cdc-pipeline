import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

import os
import json
from pathlib import Path
from dotenv import load_dotenv
import psycopg
from cdc import classify_changes

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

conn = psycopg.connect(
    #host="localhost",
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("POSTGRES_PORT"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)
cur = conn.cursor()

with open("jobs.json", "r", encoding="utf-8") as f:
    raw_jobs = json.load(f)

EXPECTED_MIN_RECORDS = 15

if len(raw_jobs) < EXPECTED_MIN_RECORDS:
    logger.error(
        f"Data quality check failed: expected at least {EXPECTED_MIN_RECORDS} jobs, "
        f"got {len(raw_jobs)}. Aborting load."
    )
    raise SystemExit(1)

today_jobs = []
for job in raw_jobs:
    today_jobs.append({
        "book_url": job["job_id"],
        "title": job["title"],
        "price": job["company"] or "",
        "availability": job["location"] or "",
        "rating": job["tags"] or "",
    })

cur.execute("SELECT id, job_id, title, company, location, tags FROM jobs WHERE is_current = TRUE")
rows = cur.fetchall()

db_current_rows = []
for row in rows:
    db_current_rows.append({
        "id": row[0],
        "book_url": row[1],
        "price": row[3],
        "availability": row[4],
        "rating": row[5],
    })

new_jobs, updated_jobs, deleted_ids = classify_changes(today_jobs, db_current_rows)

for job in new_jobs:
    cur.execute(
        """
        INSERT INTO jobs (job_id, title, company, location, tags, apply_url, posted_date, valid_from, valid_to, is_current, scraped_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NULL, TRUE, NOW())
        """,
        (
            job["book_url"],
            job["title"],
            job["price"],
            job["availability"],
            job["rating"],
            next(j["apply_url"] for j in raw_jobs if j["job_id"] == job["book_url"]),
            next(j["posted_date"] for j in raw_jobs if j["job_id"] == job["book_url"]),
        ),
    )

for job in updated_jobs:
    cur.execute(
        "UPDATE jobs SET valid_to = NOW(), is_current = FALSE WHERE job_id = %s AND is_current = TRUE",
        (job["book_url"],),
    )
    cur.execute(
        """
        INSERT INTO jobs (job_id, title, company, location, tags, apply_url, posted_date, valid_from, valid_to, is_current, scraped_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NULL, TRUE, NOW())
        """,
        (
            job["book_url"],
            job["title"],
            job["price"],
            job["availability"],
            job["rating"],
            next(j["apply_url"] for j in raw_jobs if j["job_id"] == job["book_url"]),
            next(j["posted_date"] for j in raw_jobs if j["job_id"] == job["book_url"]),
        ),
    )

for job_id in deleted_ids:
    cur.execute(
        "UPDATE jobs SET valid_to = NOW(), is_current = FALSE WHERE job_id = %s AND is_current = TRUE",
        (job_id,),
    )

conn.commit()
cur.close()
conn.close()

# print(f"New: {len(new_jobs)}")
# print(f"Updated: {len(updated_jobs)}")
# print(f"Deleted: {len(deleted_ids)}")
# print(f"Unchanged: {len(today_jobs) - len(new_jobs) - len(updated_jobs)}")

logger.info(f"New: {len(new_jobs)}")
logger.info(f"Updated: {len(updated_jobs)}")
logger.info(f"Deleted: {len(deleted_ids)}")
logger.info(f"Unchanged: {len(today_jobs) - len(new_jobs) - len(updated_jobs)}")