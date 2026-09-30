from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Book,Job

app = FastAPI(title="Web Scraping Pipeline API")


@app.get("/")
def root():
    return {"message": "API is running"}


@app.get("/books")
def get_books(db: Session = Depends(get_db)):
    books = db.query(Book).filter(Book.is_current == True).all()
    return books

@app.get("/jobs")
def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).filter(Job.is_current == True).all()
    return jobs

@app.get("/books/{book_url}/history")
def get_book_history(book_url: str, db: Session = Depends(get_db)):
    history = (
        db.query(Book)
        .filter(Book.book_url == book_url)
        .order_by(Book.valid_from)
        .all()
    )
    return history

@app.get("/jobs/{job_id}/history")
def get_job_history(job_id: str, db: Session = Depends(get_db)):
    history = (
        db.query(Job)
        .filter(Job.job_id == job_id)
        .order_by(Job.valid_from)
        .all()
    )
    return history