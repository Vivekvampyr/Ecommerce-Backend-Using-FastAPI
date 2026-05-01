class Product {
  final int id;
  final String name;
  final String? description;
  final double price;
  final int stock;
  final int? categoryId;
  final double? averageRating;
  final int? totalReviews;

  Product({
    required this.id,
    required this.name,
    this.description,
    required this.price,
    required this.stock,
    this.categoryId,
    this.averageRating,
    this.totalReviews,
  });

  factory Product.fromJson(Map<String, dynamic> json) => Product(
    id: json['id'],
    name: json['name'],
    description: json['description'],
    price: json['price'].toDouble(),
    stock: json['stock'],
    categoryId: json['category_id'],
    averageRating: json['average_rating']?.toDouble(),
    totalReviews: json['total_reviews'],
  );
}
