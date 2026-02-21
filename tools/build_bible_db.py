#!/usr/bin/env python3
"""
build_bible_db.py – Build assets/db/bible.sqlite from elberfelder_1905.csv.

The Elberfelder 1905 Bible text is in the Public Domain.

Usage:
    python3 tools/build_bible_db.py

Run from the repository root.  The script reads
  elberfelder_1905.csv
and writes
  assets/db/bible.sqlite
"""

import csv
import json
import os
import sqlite3
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(REPO_ROOT, "elberfelder_1905.csv")
DB_DIR = os.path.join(REPO_ROOT, "assets", "db")
DB_PATH = os.path.join(DB_DIR, "bible.sqlite")
SCHEMA_PATH = os.path.join(REPO_ROOT, "schema", "bible_schema.sql")
PASSAGES_JSON = os.path.join(REPO_ROOT, "data", "key_passages.json")


def find_header_row(reader):
    """Advance *reader* until a row containing 'Verse ID' and 'Book Number' is found.

    Returns that header row as a list of strings, or raises RuntimeError if
    the header is not found.
    """
    for row in reader:
        if any("Verse ID" in cell for cell in row) and any(
            "Book Number" in cell for cell in row
        ):
            return row
    raise RuntimeError("CSV header row not found – expected columns 'Verse ID' and 'Book Number'")


def build_database(csv_path: str, db_path: str, schema_path: str,
                   passages_json: str = PASSAGES_JSON) -> None:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Remove stale database so we always start fresh.
    if os.path.exists(db_path):
        os.remove(db_path)

    con = sqlite3.connect(db_path)
    try:
        # Apply schema.
        with open(schema_path, encoding="utf-8") as f:
            con.executescript(f.read())

        with open(csv_path, encoding="utf-8", newline="") as fh:
            reader = csv.reader(fh)

            # Skip metadata lines until the real header row.
            header = find_header_row(reader)

            # Map column names → indices (strip surrounding whitespace/quotes).
            col = {name.strip().strip('"'): idx for idx, name in enumerate(header)}
            try:
                idx_book_num = col["Book Number"]
                idx_book_name = col["Book Name"]
                idx_chapter = col["Chapter"]
                idx_verse = col["Verse"]
                idx_text = col["Text"]
            except KeyError as exc:
                raise RuntimeError(f"Expected CSV column not found: {exc}") from exc

            books: dict[int, str] = {}
            verses: list[tuple] = []
            row_count = 0

            for row in reader:
                if not row:
                    continue
                book_id = int(row[idx_book_num])
                book_name = row[idx_book_name]
                chapter = int(row[idx_chapter])
                verse = int(row[idx_verse])
                text = row[idx_text]

                books[book_id] = book_name
                verses.append((book_id, chapter, verse, text))
                row_count += 1

                if row_count % 5000 == 0:
                    print(f"  … {row_count} rows read", flush=True)

        print(f"CSV parsed: {row_count} verses, {len(books)} books", flush=True)

        # Insert in a single transaction for speed.
        with con:
            con.executemany(
                "INSERT OR REPLACE INTO books (id, name_de) VALUES (?, ?)",
                sorted(books.items()),
            )
            con.executemany(
                "INSERT INTO bible_verses (book_id, chapter, verse, text) VALUES (?, ?, ?, ?)",
                verses,
            )

        # Populate FTS table.
        print("Building FTS index …", flush=True)
        with con:
            con.execute(
                """
                INSERT INTO bible_verses_fts (rowid, text, book_id, chapter, verse)
                SELECT rowid, text, book_id, chapter, verse
                FROM   bible_verses
                """
            )

        # Validate.
        verse_count = con.execute("SELECT COUNT(*) FROM bible_verses").fetchone()[0]
        book_count = con.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        fts_count = con.execute("SELECT COUNT(*) FROM bible_verses_fts").fetchone()[0]
        print(
            f"Database written to {db_path}\n"
            f"  books:            {book_count}\n"
            f"  bible_verses:     {verse_count}\n"
            f"  bible_verses_fts: {fts_count}",
            flush=True,
        )

        if verse_count != fts_count:
            print(
                f"WARNING: verse count ({verse_count}) != FTS count ({fts_count})",
                file=sys.stderr,
            )
            sys.exit(1)

        # Populate key passages from JSON.
        if os.path.exists(passages_json):
            _populate_passages(con, passages_json)
        else:
            print(f"  (Skipping key passages – {passages_json} not found)", flush=True)

    finally:
        con.close()


def _populate_passages(con: sqlite3.Connection, json_path: str) -> None:
    """Insert passage_themes and key_passages from the curated JSON file."""
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    with con:
        con.executemany(
            "INSERT OR REPLACE INTO passage_themes (id, name, icon) VALUES (?, ?, ?)",
            [(t["id"], t["name"], t["icon"]) for t in data["themes"]],
        )
        con.executemany(
            """INSERT OR REPLACE INTO key_passages
               (id, theme_id, sort_order, title, book_id,
                chapter_from, verse_from, chapter_to, verse_to)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    p["id"], p["theme_id"], p["sort_order"], p["title"],
                    p["book_id"], p["chapter_from"], p["verse_from"],
                    p["chapter_to"], p["verse_to"],
                )
                for p in data["passages"]
            ],
        )

    theme_count   = con.execute("SELECT COUNT(*) FROM passage_themes").fetchone()[0]
    passage_count = con.execute("SELECT COUNT(*) FROM key_passages").fetchone()[0]
    print(
        f"  passage_themes:   {theme_count}\n"
        f"  key_passages:     {passage_count}",
        flush=True,
    )


if __name__ == "__main__":
    print(f"Reading CSV:  {CSV_PATH}")
    print(f"Schema:       {SCHEMA_PATH}")
    print(f"Passages:     {PASSAGES_JSON}")
    print(f"Output DB:    {DB_PATH}")
    build_database(CSV_PATH, DB_PATH, SCHEMA_PATH)
    print("Done.")
