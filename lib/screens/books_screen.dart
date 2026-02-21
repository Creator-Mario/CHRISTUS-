import 'package:flutter/material.dart';

import '../database/bible_db.dart';
import '../models/book.dart';
import 'chapters_screen.dart';
import 'search_screen.dart';

/// Home screen – lists all 66 Bible books.
class BooksScreen extends StatefulWidget {
  const BooksScreen({super.key});

  @override
  State<BooksScreen> createState() => _BooksScreenState();
}

class _BooksScreenState extends State<BooksScreen> {
  late Future<List<Book>> _booksFuture;

  @override
  void initState() {
    super.initState();
    _booksFuture = BibleDatabase.instance.allBooks();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Christus – Bibel'),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            tooltip: 'Suchen',
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const SearchScreen()),
            ),
          ),
        ],
      ),
      body: FutureBuilder<List<Book>>(
        future: _booksFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Fehler: ${snapshot.error}'));
          }
          final books = snapshot.data!;
          return ListView.builder(
            itemCount: books.length,
            itemBuilder: (context, index) {
              final book = books[index];
              return ListTile(
                leading: CircleAvatar(child: Text('${book.id}')),
                title: Text(book.nameDe),
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => ChaptersScreen(book: book),
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
