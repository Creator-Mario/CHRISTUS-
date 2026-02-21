/// A curated Bible passage (a range of verses within one book).
class Passage {
  final int id;
  final int themeId;
  final int sortOrder;
  final String title;
  final int bookId;
  final int chapterFrom;
  final int verseFrom;
  final int chapterTo;
  final int verseTo;

  const Passage({
    required this.id,
    required this.themeId,
    required this.sortOrder,
    required this.title,
    required this.bookId,
    required this.chapterFrom,
    required this.verseFrom,
    required this.chapterTo,
    required this.verseTo,
  });

  factory Passage.fromMap(Map<String, dynamic> map) {
    return Passage(
      id:          map['id']           as int,
      themeId:     map['theme_id']     as int,
      sortOrder:   map['sort_order']   as int,
      title:       map['title']        as String,
      bookId:      map['book_id']      as int,
      chapterFrom: map['chapter_from'] as int,
      verseFrom:   map['verse_from']   as int,
      chapterTo:   map['chapter_to']   as int,
      verseTo:     map['verse_to']     as int,
    );
  }

  /// A human-readable reference string, e.g. "1Mo 3,1-24" or "Mt 5,1-12".
  String get reference {
    if (chapterFrom == chapterTo) {
      return '$chapterFrom,$verseFrom–$verseTo';
    }
    return '$chapterFrom,$verseFrom – $chapterTo,$verseTo';
  }
}
