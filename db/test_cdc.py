from cdc import classify_changes


def test_new_book_detected():
    today = [{"book_url": "book1", "title": "A", "price": "10", "availability": "In stock", "rating": "Two"}]
    db_current = []
    new, updated, deleted = classify_changes(today, db_current)
    assert len(new) == 1
    assert new[0]["book_url"] == "book1"


def test_unchanged_book_not_flagged():
    today = [{"book_url": "book1", "title": "A", "price": "10", "availability": "In stock", "rating": "Two"}]
    db_current = [{"book_url": "book1", "price": "10", "availability": "In stock", "rating": "Two"}]
    new, updated, deleted = classify_changes(today, db_current)
    assert len(new) == 0
    assert len(updated) == 0


def test_price_change_detected():
    today = [{"book_url": "book1", "title": "A", "price": "12", "availability": "In stock", "rating": "Two"}]
    db_current = [{"book_url": "book1", "price": "10", "availability": "In stock", "rating": "Two"}]
    new, updated, deleted = classify_changes(today, db_current)
    assert len(updated) == 1


def test_deleted_book_detected():
    today = []
    db_current = [{"book_url": "book1", "price": "10", "availability": "In stock", "rating": "Two"}]
    new, updated, deleted = classify_changes(today, db_current)
    assert deleted == ["book1"]