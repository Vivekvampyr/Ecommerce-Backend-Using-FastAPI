import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/cart.dart';
import '../models/order.dart';
import '../services/cart_service.dart';

final cartServiceProvider = Provider((ref) => CartService());

final cartProvider =
    StateNotifierProvider<CartNotifier, AsyncValue<List<CartItem>>>(
      (ref) => CartNotifier(ref.read(cartServiceProvider)),
    );

class CartNotifier extends StateNotifier<AsyncValue<List<CartItem>>> {
  final CartService _cartService;

  CartNotifier(this._cartService) : super(const AsyncValue.data([]));

  Future<void> loadCart() async {
    state = const AsyncValue.loading();
    try {
      final items = await _cartService.getCart();
      state = AsyncValue.data(items);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> addItem(int productId, int quantity) async {
    await _cartService.addToCart(productId, quantity);
    await loadCart();
  }

  Future<void> updateItem(int itemId, int quantity) async {
    await _cartService.updateCartItem(itemId, quantity);
    await loadCart();
  }

  Future<void> removeItem(int itemId) async {
    await _cartService.removeFromCart(itemId);
    await loadCart();
  }

  // ✅ this is what cart_screen.dart calls
  Future<Order> checkout({String? couponCode}) async {
    final order = await _cartService.checkout(couponCode: couponCode);
    await loadCart();
    return order;
  }

  int get itemCount => state.maybeWhen(
    data: (items) => items.fold(0, (sum, item) => sum + item.quantity),
    orElse: () => 0,
  );

  double get total => state.maybeWhen(
    data: (items) => items.fold(0.0, (sum, item) => sum + item.subtotal),
    orElse: () => 0.0,
  );

  bool get isEmpty =>
      state.maybeWhen(data: (items) => items.isEmpty, orElse: () => true);

  int get uniqueItemCount =>
      state.maybeWhen(data: (items) => items.length, orElse: () => 0);
}
