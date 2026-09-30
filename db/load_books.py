# import os
# import json
# from pathlib import Path
# from datetime import datetime, timezone
# import psycopg
# from dotenv import load_dotenv

# env_path = Path(__file__).resolve().parents[1] / ".env"
# load_dotenv(dotenv_path=env_path)

# conn = psycopg.connect(
#     host="localhost",
#     port=os.getenv("POSTGRES_PORT"),
#     dbname=os.getenv("POSTGRES_DB"),
#     user=os.getenv("POSTGRES_USER"),
#     password=os.getenv("POSTGRES_PASSWORD"),
# )

# with open("books_with_rating.json", "r", encoding="utf-8") as f:
#     books = json.load(f)

# cur = conn.cursor()

# for book in books:
#     title = book["title"]
#     price = book["price"].replace("£", "")
#     availability = book["availability"]
#     rating = book["rating"]
#     book_url = title

#     cur.execute(
#         "SELECT id, price, availability, rating FROM books WHERE book_url = %s AND is_current = TRUE",
#         (book_url,),
#     )
#     existing = cur.fetchone()
#     if existing is None:
#         cur.execute(
#             """
#             INSERT INTO books (book_url, title, price, availability, rating, valid_from, valid_to, is_current, scraped_at)
#             VALUES (%s, %s, %s, %s, %s, NOW(), NULL, TRUE, NOW())
#             """,
#             (book_url, title, price, availability, rating),
#         )
#         print(f"NEW: {title}")

#     else:
#         existing_id, existing_price, existing_availability, existing_rating = existing
#         if (
#             str(existing_price) != price
#             or existing_availability != availability
#             or existing_rating != rating
#         ):
#             cur.execute(
#                 "UPDATE books SET valid_to = NOW(), is_current = FALSE WHERE id = %s",
#                 (existing_id,),
#             )
#             cur.execute(
#                 """
#                 INSERT INTO books (book_url, title, price, availability, rating, valid_from, valid_to, is_current, scraped_at)
#                 VALUES (%s, %s, %s, %s, %s, NOW(), NULL, TRUE, NOW())
#                 """,
#                 (book_url, title, price, availability, rating),
#             )
#             print(f"UPDATED: {title}")
#         else:
#             print(f"UNCHANGED: {title}")

# conn.commit()
# cur.close()
# conn.close()
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

with open("books_with_rating.json", "r", encoding="utf-8") as f:
    raw_books = json.load(f)

EXPECTED_MIN_RECORDS = 15

if len(raw_books) < EXPECTED_MIN_RECORDS:
    logger.error(
        f"Data quality check failed: expected at least {EXPECTED_MIN_RECORDS} books, "
        f"got {len(raw_books)}. Aborting load."
    )
    raise SystemExit(1)

today_books = []
for book in raw_books:
    today_books.append({
        "book_url": book["title"],
        "title": book["title"],
        "price": book["price"].replace("£", ""),
        "availability": book["availability"],
        "rating": book["rating"],
    })

cur.execute("SELECT id, book_url, price, availability, rating FROM books WHERE is_current = TRUE")
rows = cur.fetchall()

db_current_rows = []
for row in rows:
    db_current_rows.append({
        "id": row[0],
        "book_url": row[1],
        "price": row[2],
        "availability": row[3],
        "rating": row[4],
    })

new_books, updated_books, deleted_urls = classify_changes(today_books, db_current_rows)

for book in new_books:
    cur.execute(
        """
        INSERT INTO books (book_url, title, price, availability, rating, valid_from, valid_to, is_current, scraped_at)
        VALUES (%s, %s, %s, %s, %s, NOW(), NULL, TRUE, NOW())
        """,
        (book["book_url"], book["title"], book["price"], book["availability"], book["rating"]),
    )

for book in updated_books:
    cur.execute(
        "UPDATE books SET valid_to = NOW(), is_current = FALSE WHERE book_url = %s AND is_current = TRUE",
        (book["book_url"],),
    )
    cur.execute(
        """
        INSERT INTO books (book_url, title, price, availability, rating, valid_from, valid_to, is_current, scraped_at)
        VALUES (%s, %s, %s, %s, %s, NOW(), NULL, TRUE, NOW())
        """,
        (book["book_url"], book["title"], book["price"], book["availability"], book["rating"]),
    )

for url in deleted_urls:
    cur.execute(
        "UPDATE books SET valid_to = NOW(), is_current = FALSE WHERE book_url = %s AND is_current = TRUE",
        (url,),
    )

conn.commit()
cur.close()
conn.close()
logger.info(f"New: {len(new_books)}")
logger.info(f"Updated: {len(updated_books)}")
logger.info(f"Deleted: {len(deleted_urls)}")
logger.info(f"Unchanged: {len(today_books) - len(new_books) - len(updated_books)}")
# print(f"New: {len(new_books)}")
# print(f"Updated: {len(updated_books)}")
# print(f"Deleted: {len(deleted_urls)}")
# print(f"Unchanged: {len(today_books) - len(new_books) - len(updated_books)}")