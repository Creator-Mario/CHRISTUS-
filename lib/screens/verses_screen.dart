import 'package:flutter/material.dart';

import '../database/bible_db.dart';
import '../models/book.dart';
import '../models/verse.dart';

/// Displays all verses in a chapter.
class VersesScreen extends StatefulWidget {
  final Book book;
  final int chapter;

  const VersesScreen({super.key, required this.book, required this.chapter});

  @override
  State<VersesScreen> createState() => _VersesScreenState();
}

class _VersesScreenState extends State<VersesScreen> {
  late Future<List<Verse>> _versesFuture;

  @override
  void initState() {
    super.initState();
    _versesFuture = BibleDatabase.instance
        .versesForChapter(widget.book.id, widget.chapter);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('${widget.book.nameDe} ${widget.chapter}'),
      ),
      body: FutureBuilder<List<Verse>>(
        future: _versesFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Fehler: ${snapshot.error}'));
          }
          final verses = snapshot.data!;
          return ListView.builder(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            itemCount: verses.length,
            itemBuilder: (context, index) {
              final v = verses[index];
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 6),
                child: RichText(
                  text: TextSpan(
                    style: DefaultTextStyle.of(context).style,
                    children: [
                      TextSpan(
                        text: '${v.verse}  ',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Theme.of(context).colorScheme.primary,
                        ),
                      ),
                      TextSpan(text: v.text),
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
