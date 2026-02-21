import 'package:flutter/material.dart';

import 'screens/books_screen.dart';

void main() {
  runApp(const ChristusApp());
}

class ChristusApp extends StatelessWidget {
  const ChristusApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Christus – Bibel',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1A237E)),
        useMaterial3: true,
      ),
      home: const BooksScreen(),
    );
  }
}
