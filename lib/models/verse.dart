/// A single Bible verse.
class Verse {
  final int bookId;
  final int chapter;
  final int verse;
  final String text;

  const Verse({
    required this.bookId,
    required this.chapter,
    required this.verse,
    required this.text,
  });

  factory Verse.fromMap(Map<String, dynamic> map) {
    return Verse(
      bookId: map['book_id'] as int,
      chapter: map['chapter'] as int,
      verse: map['verse'] as int,
      text: map['text'] as String,
    );
  }
}
