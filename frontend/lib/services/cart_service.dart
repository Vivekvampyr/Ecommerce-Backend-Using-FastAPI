import '../core/dio_client.dart';
import '../models/cart.dart';
import '../models/order.dart';

class CartService {
  final _dio = DioClient.instance;

  Future<List<CartItem>> getCart() async {
    final response = await _dio.get('/cart/');
    return (response.data as List).map((i) => CartItem.fromJson(i)).toList();
  }

  Future<void> addToCart(int productId, int quantity) async {
    await _dio.post(
      '/cart/add',
      data: {'product_id': productId, 'quantity': quantity},
    );
  }

  Future<void> updateCartItem(int itemId, int quantity) async {
    await _dio.patch(
      '/cart/update/$itemId',
      queryParameters: {'quantity': quantity},
    );
  }

  Future<void> removeFromCart(int itemId) async {
    await _dio.delete('/cart/remove/$itemId');
  }

  Future<Order> checkout({String? couponCode}) async {
    final response = await _dio.post(
      '/cart/checkout',
      data: couponCode != null ? {'code': couponCode} : null,
    );
    return Order.fromJson(response.data);
  }
}
