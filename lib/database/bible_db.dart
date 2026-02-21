import 'dart:io';

import 'package:flutter/services.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:sqflite/sqflite.dart';

import '../models/book.dart';
import '../models/verse.dart';

/// Singleton that opens (and, on first launch, copies from assets) the
/// Elberfelder 1905 SQLite database.
class BibleDatabase {
  BibleDatabase._();
  static final BibleDatabase instance = BibleDatabase._();

  Database? _db;

  Future<Database> get database async {
    _db ??= await _open();
    return _db!;
  }

  Future<Database> _open() async {
    final dir = await getApplicationDocumentsDirectory();
    final dbPath = p.join(dir.path, 'bible.sqlite');

    // Copy bundled asset to writable location on first run.
    if (!File(dbPath).existsSync()) {
      final data = await rootBundle.load('assets/db/bible.sqlite');
      final bytes = data.buffer.asUint8List();
      await File(dbPath).writeAsBytes(bytes, flush: true);
    }

    return openDatabase(dbPath, readOnly: true);
  }

  // ── Books ────────────────────────────────────────────────────────────────

  Future<List<Book>> allBooks() async {
    final db = await database;
    final rows = await db.query('books', orderBy: 'id');
    return rows.map(Book.fromMap).toList();
  }

  // ── Chapters ─────────────────────────────────────────────────────────────

  /// Returns the distinct chapter numbers available for [bookId].
  Future<List<int>> chaptersForBook(int bookId) async {
    final db = await database;
    final rows = await db.rawQuery(
      'SELECT DISTINCT chapter FROM bible_verses WHERE book_id = ? ORDER BY chapter',
      [bookId],
    );
    return rows.map((r) => r['chapter'] as int).toList();
  }

  // ── Verses ───────────────────────────────────────────────────────────────

  Future<List<Verse>> versesForChapter(int bookId, int chapter) async {
    final db = await database;
    final rows = await db.query(
      'bible_verses',
      where: 'book_id = ? AND chapter = ?',
      whereArgs: [bookId, chapter],
      orderBy: 'verse',
    );
    return rows.map(Verse.fromMap).toList();
  }

  // ── Full-text search ─────────────────────────────────────────────────────

  /// Searches all verses using FTS5 and returns up to [limit] matches.
  Future<List<({int bookId, int chapter, int verse, String text})>> search(
    String query, {
    int limit = 50,
  }) async {
    if (query.trim().isEmpty) return [];
    final db = await database;
    // Build a safe FTS5 query: split into tokens, wrap each in double quotes
    // (escaping any embedded double quotes) and implicitly AND them.
    // This prevents FTS5 metacharacters (*, :, (, ), ^, etc.) from causing
    // parse errors while still supporting multi-word searches.
    final tokens = query.trim().split(RegExp(r'\s+')).where((t) => t.isNotEmpty);
    final ftsQuery =
        tokens.map((t) => '"${t.replaceAll('"', '""')}"').join(' ');
    final rows = await db.rawQuery(
      '''
      SELECT f.book_id, f.chapter, f.verse, v.text
      FROM   bible_verses_fts f
      JOIN   bible_verses v ON v.book_id = f.book_id
                           AND v.chapter  = f.chapter
                           AND v.verse    = f.verse
      WHERE  bible_verses_fts MATCH ?
      LIMIT  ?
      ''',
      [ftsQuery, limit],
    );
    return rows
        .map(
          (r) => (
            bookId: r['book_id'] as int,
            chapter: r['chapter'] as int,
            verse: r['verse'] as int,
            text: r['text'] as String,
          ),
        )
        .toList();
  }

  Future<void> close() async {
    await _db?.close();
    _db = null;
  }
}
