import 'package:flutter/material.dart';

import '../database/bible_db.dart';
import '../models/book.dart';
import '../models/passage.dart';
import '../models/verse.dart';

/// Displays all verses of a curated [passage], with chapter headings when
/// the passage spans multiple chapters.
class PassageScreen extends StatefulWidget {
  final Passage passage;
  final Color color;

  const PassageScreen({super.key, required this.passage, required this.color});

  @override
  State<PassageScreen> createState() => _PassageScreenState();
}

class _PassageScreenState extends State<PassageScreen> {
  late Future<_PassageData> _future;

  @override
  void initState() {
    super.initState();
    _future = _load();
  }

  Future<_PassageData> _load() async {
    final verses = await BibleDatabase.instance.versesForPassage(widget.passage);
    final book = await BibleDatabase.instance.bookById(widget.passage.bookId);
    return _PassageData(verses: verses, book: book);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.passage.title),
        backgroundColor: widget.color,
        foregroundColor: Colors.white,
      ),
      body: FutureBuilder<_PassageData>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Fehler: ${snapshot.error}'));
          }
          final data = snapshot.data!;
          if (data.verses.isEmpty) {
            return const Center(child: Text('Keine Verse gefunden.'));
          }

          // Build items: insert chapter heading whenever chapter changes.
          final items = <_Item>[];
          int? lastChapter;
          for (final v in data.verses) {
            if (v.chapter != lastChapter) {
              final bookName = data.book?.nameDe ?? '';
              items.add(_Item.heading('$bookName ${v.chapter}'));
              lastChapter = v.chapter;
            }
            items.add(_Item.verse(v));
          }

          return ListView.builder(
            padding: const EdgeInsets.symmetric(vertical: 8),
            itemCount: items.length,
            itemBuilder: (context, index) {
              final item = items[index];
              if (item.isHeading) {
                return Padding(
                  padding:
                      const EdgeInsets.fromLTRB(16, 16, 16, 4),
                  child: Text(
                    item.heading!,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 15,
                      color: widget.color,
                    ),
                  ),
                );
              }
              final v = item.verse!;
              return Padding(
                padding: const EdgeInsets.symmetric(
                    horizontal: 16, vertical: 5),
                child: RichText(
                  text: TextSpan(
                    style: DefaultTextStyle.of(context).style,
                    children: [
                      TextSpan(
                        text: '${v.verse}  ',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: widget.color,
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

class _PassageData {
  final List<Verse> verses;
  final Book? book;
  _PassageData({required this.verses, required this.book});
}

class _Item {
  final String? heading;
  final Verse? verse;

  _Item.heading(String h) : heading = h, verse = null;
  _Item.verse(Verse v)    : verse = v,   heading = null;

  bool get isHeading => heading != null;
}
