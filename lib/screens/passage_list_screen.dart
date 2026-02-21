import 'package:flutter/material.dart';

import '../database/bible_db.dart';
import '../models/passage.dart';
import '../models/passage_theme.dart';
import 'passage_screen.dart';

/// Displays the list of curated passages for a given [theme].
class PassageListScreen extends StatefulWidget {
  final PassageTheme theme;
  final Color color;

  const PassageListScreen({super.key, required this.theme, required this.color});

  @override
  State<PassageListScreen> createState() => _PassageListScreenState();
}

class _PassageListScreenState extends State<PassageListScreen> {
  late Future<List<Passage>> _future;

  @override
  void initState() {
    super.initState();
    _future = BibleDatabase.instance.passagesForTheme(widget.theme.id);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('${widget.theme.icon}  ${widget.theme.name}'),
        backgroundColor: widget.color,
        foregroundColor: Colors.white,
      ),
      body: FutureBuilder<List<Passage>>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Fehler: ${snapshot.error}'));
          }
          final passages = snapshot.data!;
          return ListView.separated(
            itemCount: passages.length,
            separatorBuilder: (_, __) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final passage = passages[index];
              return ListTile(
                leading: CircleAvatar(
                  backgroundColor: widget.color,
                  foregroundColor: Colors.white,
                  radius: 16,
                  child: Text(
                    '${index + 1}',
                    style: const TextStyle(fontSize: 12),
                  ),
                ),
                title: Text(passage.title),
                subtitle: Text(
                  passage.reference,
                  style: TextStyle(color: widget.color, fontSize: 12),
                ),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => PassageScreen(
                      passage: passage,
                      color: widget.color,
                    ),
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
