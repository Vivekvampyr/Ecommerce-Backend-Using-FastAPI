import 'package:frontend/models/product.dart';

class CartItem {
  final int id;
  final int productId;
  final int quantity;
  final Product product;

  CartItem({
    required this.id,
    required this.productId,
    required this.quantity,
    required this.product,
  });

  factory CartItem.fromJson(Map<String, dynamic> json) => CartItem(
    id: json['id'],
    productId: json['product_id'],
    quantity: json['quantity'],
    product: Product.fromJson(json['product']),
  );

  double get subtotal => product.price * quantity;
}
