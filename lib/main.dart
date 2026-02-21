import 'package:flutter/material.dart';

import 'screens/home_screen.dart';

void main() {
  runApp(const BDEApp());
}

class BDEApp extends StatelessWidget {
  const BDEApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Buch des Dienstes zur Evangelisation',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF0D1B2A),
          primary: const Color(0xFF0D1B2A),
          secondary: const Color(0xFFC9A227),
          background: const Color(0xFFF7F3E9),
        ),
        useMaterial3: true,
        fontFamily: 'Georgia',
      ),
      home: const HomeScreen(),
    );
  }
}
