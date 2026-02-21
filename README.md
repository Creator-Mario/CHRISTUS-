# CHRISTUS-
Bibelstellen

## Bible Database

The repository includes the **Elberfelder 1905** German Bible translation as a
CSV file (`elberfelder_1905.csv`).  The text is in the **Public Domain** (see
the header of the CSV file).

A Python build script converts the CSV into a SQLite database
(`assets/db/bible.sqlite`) that is suitable for use in Flutter apps and
supports:

- Hierarchical Bible browsing (book → chapter → verses)
- Global full-text search via an **FTS5** virtual table

### Prerequisites

- Python 3.8 or later (no third-party packages required – uses the standard
  library only)

### Building the database

Run the following command from the **repository root**:

```bash
python3 tools/build_bible_db.py
```

The script will:

1. Read `elberfelder_1905.csv`
2. Apply the schema in `schema/bible_schema.sql`
3. Write `assets/db/bible.sqlite`

Progress and validation counts are printed to stdout.

### Database schema

| Table | Purpose |
|---|---|
| `books` | One row per Bible book (id 1–66, German name) |
| `bible_verses` | All verses, primary key `(book_id, chapter, verse)` |
| `bible_verses_fts` | FTS5 virtual table for full-text search |

#### Example queries

```sql
-- List all books
SELECT id, name_de FROM books ORDER BY id;

-- Read Genesis chapter 1
SELECT verse, text
FROM   bible_verses
WHERE  book_id = 1 AND chapter = 1
ORDER  BY verse;

-- Full-text search
SELECT b.name_de, v.chapter, v.verse, v.text
FROM   bible_verses_fts f
JOIN   bible_verses v ON v.book_id = f.book_id
                     AND v.chapter = f.chapter
                     AND v.verse   = f.verse
JOIN   books b ON b.id = f.book_id
WHERE  bible_verses_fts MATCH 'Licht'
LIMIT  20;
```

> **Note:** `assets/db/bible.sqlite` is listed in `.gitignore` and must be
> regenerated locally after checkout.
