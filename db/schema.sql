CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    book_url TEXT NOT NULL,
    title TEXT NOT NULL,
    price NUMERIC(10, 2),
    availability TEXT,
    rating TEXT,
    valid_from TIMESTAMP NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMP,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    scraped_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    job_id TEXT NOT NULL,
    title TEXT NOT NULL,
    company TEXT,
    location TEXT,
    tags TEXT,
    apply_url TEXT,
    posted_date TIMESTAMP,
    valid_from TIMESTAMP NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMP,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    scraped_at TIMESTAMP NOT NULL DEFAULT NOW()
);