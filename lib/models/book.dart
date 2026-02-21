/// A Bible book (one of the 66 books in the Elberfelder 1905 translation).
class Book {
  final int id;
  final String nameDe;

  const Book({required this.id, required this.nameDe});

  factory Book.fromMap(Map<String, dynamic> map) {
    return Book(
      id: map['id'] as int,
      nameDe: map['name_de'] as String,
    );
  }
}
