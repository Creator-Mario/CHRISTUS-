/// A thematic group of curated Bible passages.
class PassageTheme {
  final int id;
  final String name;
  final String icon;

  const PassageTheme({required this.id, required this.name, required this.icon});

  factory PassageTheme.fromMap(Map<String, dynamic> map) {
    return PassageTheme(
      id:   map['id']   as int,
      name: map['name'] as String,
      icon: map['icon'] as String,
    );
  }
}
