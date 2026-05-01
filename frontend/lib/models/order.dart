class OrderItem {
  final int productId;
  final int quantity;
  final double priceAtPurchase;

  OrderItem({
    required this.productId,
    required this.quantity,
    required this.priceAtPurchase,
  });

  factory OrderItem.fromJson(Map<String, dynamic> json) => OrderItem(
    productId: json['product_id'],
    quantity: json['quantity'],
    priceAtPurchase: json['price_at_purchase'].toDouble(),
  );
}

class Order {
  final int id;
  final int userId;
  final double totalPrice;
  final double discountAmount;
  final String? couponCode;
  final String status;
  final List<OrderItem> items;

  Order({
    required this.id,
    required this.userId,
    required this.totalPrice,
    required this.discountAmount,
    this.couponCode,
    required this.status,
    required this.items,
  });

  factory Order.fromJson(Map<String, dynamic> json) => Order(
    id: json['id'],
    userId: json['user_id'],
    totalPrice: json['total_price'].toDouble(),
    discountAmount: json['discount_amount'].toDouble(),
    couponCode: json['coupon_code'],
    status: json['status'],
    items: (json['items'] as List).map((i) => OrderItem.fromJson(i)).toList(),
  );
}
