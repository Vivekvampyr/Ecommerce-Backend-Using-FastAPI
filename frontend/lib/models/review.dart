class Review {
  final int id;
  final int productId;
  final int userId;
  final int rating;
  final String? title;
  final String? body;
  final String createdAt;
  final Map<String, dynamic> author;

  Review({
    required this.id,
    required this.productId,
    required this.userId,
    required this.rating,
    this.title,
    this.body,
    required this.createdAt,
    required this.author,
  });

  factory Review.fromJson(Map<String, dynamic> json) => Review(
    id: json['id'],
    productId: json['product_id'],
    userId: json['user_id'],
    rating: json['rating'],
    title: json['title'],
    body: json['body'],
    createdAt: json['created_at'],
    author: json['author'],
  );
}
