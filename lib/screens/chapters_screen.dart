import 'package:flutter/material.dart';

import '../database/bible_db.dart';
import '../models/book.dart';
import 'verses_screen.dart';

/// Displays the chapter list for a given [book].
class ChaptersScreen extends StatefulWidget {
  final Book book;

  const ChaptersScreen({super.key, required this.book});

  @override
  State<ChaptersScreen> createState() => _ChaptersScreenState();
}

class _ChaptersScreenState extends State<ChaptersScreen> {
  late Future<List<int>> _chaptersFuture;

  @override
  void initState() {
    super.initState();
    _chaptersFuture = BibleDatabase.instance.chaptersForBook(widget.book.id);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.book.nameDe)),
      body: FutureBuilder<List<int>>(
        future: _chaptersFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Fehler: ${snapshot.error}'));
          }
          final chapters = snapshot.data!;
          return GridView.builder(
            padding: const EdgeInsets.all(12),
            gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
              maxCrossAxisExtent: 72,
              mainAxisSpacing: 8,
              crossAxisSpacing: 8,
            ),
            itemCount: chapters.length,
            itemBuilder: (context, index) {
              final chapter = chapters[index];
              return ElevatedButton(
                onPressed: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => VersesScreen(
                      book: widget.book,
                      chapter: chapter,
                    ),
                  ),
                ),
                child: Text('$chapter'),
              );
            },
          );
        },
      ),
    );
  }
}
