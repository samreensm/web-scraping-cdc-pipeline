def classify_changes(today_books, db_current_rows):
    db_lookup = {row["book_url"]: row for row in db_current_rows}
    today_urls = {book["book_url"] for book in today_books}

    new_books = []
    updated_books = []
    deleted_urls = []

    for book in today_books:
        url = book["book_url"]
        if url not in db_lookup:
            new_books.append(book)
        else:
            existing = db_lookup[url]
            if (
                str(existing["price"]) != book["price"]
                or existing["availability"] != book["availability"]
                or existing["rating"] != book["rating"]
            ):
                updated_books.append(book)

    for url in db_lookup:
        if url not in today_urls:
            deleted_urls.append(url)

    return new_books, updated_books, deleted_urls