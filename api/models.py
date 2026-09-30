from sqlalchemy import Column, Integer, Text, Numeric, Boolean, TIMESTAMP
from database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    book_url = Column(Text)
    title = Column(Text)
    price = Column(Numeric)
    availability = Column(Text)
    rating = Column(Text)
    valid_from = Column(TIMESTAMP)
    valid_to = Column(TIMESTAMP)
    is_current = Column(Boolean)
    scraped_at = Column(TIMESTAMP)

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    job_id = Column(Text)
    title = Column(Text)
    company = Column(Text)
    location = Column(Text)
    tags = Column(Text)
    apply_url = Column(Text)
    posted_date = Column(TIMESTAMP)
    valid_from = Column(TIMESTAMP)
    valid_to = Column(TIMESTAMP)
    is_current = Column(Boolean)
    scraped_at = Column(TIMESTAMP)