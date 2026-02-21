-- Bible database schema for Elberfelder 1905
-- Text is in the Public Domain.

CREATE TABLE IF NOT EXISTS books (
    id      INTEGER PRIMARY KEY,  -- Book number (1..66)
    name_de TEXT    NOT NULL       -- German book name from CSV "Book Name" column
);

CREATE TABLE IF NOT EXISTS bible_verses (
    book_id INTEGER NOT NULL,
    chapter INTEGER NOT NULL,
    verse   INTEGER NOT NULL,
    text    TEXT    NOT NULL,
    PRIMARY KEY (book_id, chapter, verse),
    FOREIGN KEY (book_id) REFERENCES books(id)
);

CREATE INDEX IF NOT EXISTS idx_bible_verses_book_chapter
    ON bible_verses (book_id, chapter);

-- FTS5 virtual table for full-text search across verse text.
-- book_id, chapter, verse are stored as UNINDEXED columns so that
-- search results can be navigated back to the exact verse.
CREATE VIRTUAL TABLE IF NOT EXISTS bible_verses_fts USING fts5 (
    text,
    book_id  UNINDEXED,
    chapter  UNINDEXED,
    verse    UNINDEXED,
    content='bible_verses',
    content_rowid='rowid'
);

-- ── Curated key passages ──────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS passage_themes (
    id   INTEGER PRIMARY KEY,
    name TEXT    NOT NULL,
    icon TEXT    NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS key_passages (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    theme_id     INTEGER NOT NULL,
    sort_order   INTEGER NOT NULL DEFAULT 0,
    title        TEXT    NOT NULL,
    book_id      INTEGER NOT NULL,
    chapter_from INTEGER NOT NULL,
    verse_from   INTEGER NOT NULL,
    chapter_to   INTEGER NOT NULL,
    verse_to     INTEGER NOT NULL,
    FOREIGN KEY (theme_id) REFERENCES passage_themes(id)
);

CREATE INDEX IF NOT EXISTS idx_key_passages_theme
    ON key_passages (theme_id, sort_order);
