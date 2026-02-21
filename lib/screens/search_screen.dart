import 'package:flutter/material.dart';

import '../database/bible_db.dart';
import '../models/book.dart';
import 'verses_screen.dart';

/// Global full-text search screen using the FTS5 index.
class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final TextEditingController _controller = TextEditingController();
  List<({int bookId, int chapter, int verse, String text})> _results = [];
  Map<int, Book> _bookCache = {};
  bool _loading = false;
  String? _error;

  Future<void> _runSearch(String query) async {
    if (query.trim().isEmpty) {
      setState(() => _results = []);
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final results = await BibleDatabase.instance.search(query);
      // Pre-load book names we haven't seen yet.
      final db = BibleDatabase.instance;
      final books = await db.allBooks();
      final cache = {for (final b in books) b.id: b};
      setState(() {
        _results = results;
        _bookCache = cache;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: TextField(
          controller: _controller,
          autofocus: true,
          decoration: const InputDecoration(
            hintText: 'Bibelstellen suchen …',
            border: InputBorder.none,
          ),
          onSubmitted: _runSearch,
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () => _runSearch(_controller.text),
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_error != null) return Center(child: Text('Fehler: $_error'));
    if (_results.isEmpty && _controller.text.isNotEmpty) {
      return const Center(child: Text('Keine Ergebnisse gefunden.'));
    }
    return ListView.builder(
      itemCount: _results.length,
      itemBuilder: (context, index) {
        final r = _results[index];
        final bookName = _bookCache[r.bookId]?.nameDe ?? '?';
        return ListTile(
          title: Text(r.text),
          subtitle: Text('$bookName ${r.chapter},${r.verse}'),
          onTap: () {
            final book = _bookCache[r.bookId];
            if (book == null) return;
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) =>
                    VersesScreen(book: book, chapter: r.chapter),
              ),
            );
          },
        );
      },
    );
  }
}
