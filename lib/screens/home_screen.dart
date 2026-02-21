import 'package:flutter/material.dart';

import '../database/bible_db.dart';
import '../models/passage_theme.dart';
import 'books_screen.dart';
import 'passage_list_screen.dart';
import 'search_screen.dart';

// Colours cycle for each of the 18 theme cards.
const List<Color> _kThemeColors = [
  Color(0xFF1A237E), Color(0xFF4A148C), Color(0xFF880E4F),
  Color(0xFFBF360C), Color(0xFF1B5E20), Color(0xFF006064),
  Color(0xFF0D47A1), Color(0xFF37474F), Color(0xFF4E342E),
  Color(0xFF1A237E), Color(0xFF6A1B9A), Color(0xFF01579B),
  Color(0xFF2E7D32), Color(0xFFE65100), Color(0xFF3E2723),
  Color(0xFF283593), Color(0xFF558B2F), Color(0xFF4527A0),
];

/// Home screen – shows 18 thematic categories of curated Bible passages.
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late Future<List<PassageTheme>> _themesFuture;

  @override
  void initState() {
    super.initState();
    _themesFuture = BibleDatabase.instance.allThemes();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Christus – Bibel'),
        actions: [
          IconButton(
            icon: const Icon(Icons.menu_book_outlined),
            tooltip: 'Alle 66 Bücher',
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const BooksScreen()),
            ),
          ),
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
      body: FutureBuilder<List<PassageTheme>>(
        future: _themesFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Fehler: ${snapshot.error}'));
          }
          final themes = snapshot.data!;
          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 14, 16, 4),
                child: Text(
                  'Wichtige Bibelstellen',
                  style: Theme.of(context)
                      .textTheme
                      .titleMedium
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
              ),
              Expanded(
                child: GridView.builder(
                  padding: const EdgeInsets.all(12),
                  gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
                    maxCrossAxisExtent: 200,
                    mainAxisSpacing: 10,
                    crossAxisSpacing: 10,
                    childAspectRatio: 1.3,
                  ),
                  itemCount: themes.length,
                  itemBuilder: (context, index) {
                    final theme = themes[index];
                    final color = _kThemeColors[index % _kThemeColors.length];
                    return _ThemeCard(
                      theme: theme,
                      color: color,
                      onTap: () => Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) =>
                              PassageListScreen(theme: theme, color: color),
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _ThemeCard extends StatelessWidget {
  final PassageTheme theme;
  final Color color;
  final VoidCallback onTap;

  const _ThemeCard({
    required this.theme,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 3,
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [color, color.withOpacity(0.75)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(theme.icon, style: const TextStyle(fontSize: 28)),
              Text(
                theme.name,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
