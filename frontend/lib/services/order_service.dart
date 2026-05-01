import '../core/dio_client.dart';
import '../models/order.dart';

class OrderService {
  final _dio = DioClient.instance;

  Future<List<Order>> getMyOrders() async {
    final response = await _dio.get('/orders/me');
    return (response.data as List).map((o) => Order.fromJson(o)).toList();
  }

  Future<Order> getOrder(int id) async {
    final response = await _dio.get('/orders/me/$id');
    return Order.fromJson(response.data);
  }

  Future<Order> cancelOrder(int id) async {
    final response = await _dio.patch('/orders/me/$id/cancel');
    return Order.fromJson(response.data);
  }
}
