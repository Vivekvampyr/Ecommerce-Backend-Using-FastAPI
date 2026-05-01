import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/cart_provider.dart';
import '../../models/cart.dart';

class CartScreen extends ConsumerStatefulWidget {
  const CartScreen({super.key});

  @override
  ConsumerState<CartScreen> createState() => _CartScreenState();
}

class _CartScreenState extends ConsumerState<CartScreen> {
  final _couponCtrl = TextEditingController();
  bool _checkingOut = false;
  bool _couponApplied = false;

  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(cartProvider.notifier).loadCart());
  }

  @override
  void dispose() {
    _couponCtrl.dispose();
    super.dispose();
  }

  Future<void> _checkout() async {
    setState(() => _checkingOut = true);
    try {
      final order = await ref
          .read(cartProvider.notifier)
          .checkout(
            couponCode:
                _couponCtrl.text.trim().isEmpty
                    ? null
                    : _couponCtrl.text.trim(),
          );
      if (mounted) {
        context.go('/orders/${order.id}');
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Order placed successfully!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Checkout failed: ${_parseError(e)}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _checkingOut = false);
    }
  }

  Future<void> _removeItem(int itemId) async {
    try {
      await ref.read(cartProvider.notifier).removeItem(itemId);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Item removed'),
            duration: Duration(seconds: 1),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to remove item: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _updateQuantity(int itemId, int newQty) async {
    try {
      if (newQty <= 0) {
        await ref.read(cartProvider.notifier).removeItem(itemId);
      } else {
        await ref.read(cartProvider.notifier).updateItem(itemId, newQty);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to update: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  String _parseError(Object e) {
    final msg = e.toString();
    if (msg.contains('400')) return 'Insufficient stock or invalid coupon';
    if (msg.contains('401')) return 'Please login again';
    if (msg.contains('404')) return 'Item not found';
    return msg;
  }

  // ─── Confirm delete dialog ───────────────────────────────
  Future<void> _confirmRemove(BuildContext context, CartItem item) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder:
          (_) => AlertDialog(
            title: const Text('Remove Item'),
            content: Text('Remove "${item.product.name}" from cart?'),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('Cancel'),
              ),
              TextButton(
                onPressed: () => Navigator.pop(context, true),
                child: const Text(
                  'Remove',
                  style: TextStyle(color: Colors.red),
                ),
              ),
            ],
          ),
    );
    if (confirmed == true) await _removeItem(item.id);
  }

  @override
  Widget build(BuildContext context) {
    final cartState = ref.watch(cartProvider);
    final cartNotifier = ref.read(cartProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Cart'),
        actions: [
          // Clear cart button — only show when cart has items
          cartState.maybeWhen(
            data:
                (items) =>
                    items.isNotEmpty
                        ? TextButton.icon(
                          onPressed: () async {
                            final confirmed = await showDialog<bool>(
                              context: context,
                              builder:
                                  (_) => AlertDialog(
                                    title: const Text('Clear Cart'),
                                    content: const Text(
                                      'Remove all items from cart?',
                                    ),
                                    actions: [
                                      TextButton(
                                        onPressed:
                                            () => Navigator.pop(context, false),
                                        child: const Text('Cancel'),
                                      ),
                                      TextButton(
                                        onPressed:
                                            () => Navigator.pop(context, true),
                                        child: const Text(
                                          'Clear',
                                          style: TextStyle(color: Colors.red),
                                        ),
                                      ),
                                    ],
                                  ),
                            );
                            if (confirmed == true) {
                              for (final item in items) {
                                await cartNotifier.removeItem(item.id);
                              }
                            }
                          },
                          icon: const Icon(
                            Icons.delete_outline,
                            color: Colors.white,
                          ),
                          label: const Text(
                            'Clear',
                            style: TextStyle(color: Colors.white),
                          ),
                        )
                        : const SizedBox(),
            orElse: () => const SizedBox(),
          ),
        ],
      ),
      body: cartState.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error:
            (e, _) => Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, size: 60, color: Colors.red),
                  const SizedBox(height: 16),
                  Text('Failed to load cart: $e'),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () => cartNotifier.loadCart(),
                    child: const Text('Retry'),
                  ),
                ],
              ),
            ),
        data: (items) {
          // ─── Empty cart ────────────────────────────────────
          if (items.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.shopping_cart_outlined,
                    size: 100,
                    color: Colors.grey.shade300,
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'Your cart is empty',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Add some products to get started',
                    style: TextStyle(color: Colors.grey),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton.icon(
                    onPressed: () => context.go('/products'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.deepPurple,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 24,
                        vertical: 12,
                      ),
                    ),
                    icon: const Icon(Icons.store),
                    label: const Text(
                      'Start Shopping',
                      style: TextStyle(fontSize: 16),
                    ),
                  ),
                ],
              ),
            );
          }

          // ─── Cart with items ───────────────────────────────
          return Column(
            children: [
              // ─── Cart item count banner ────────────────────
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 10,
                ),
                color: Colors.deepPurple.shade50,
                child: Text(
                  "Hey There",
                  //'${cartNotifier.uniqueItemCount} item${cartNotifier.uniqueItemCount > 1 ? 's' : ''} in your cart',
                  style: const TextStyle(
                    color: Colors.deepPurple,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),

              // ─── Item list ────────────────────────────────
              Expanded(
                child: RefreshIndicator(
                  onRefresh: () => cartNotifier.loadCart(),
                  child: ListView.builder(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 8,
                    ),
                    itemCount: items.length,
                    itemBuilder: (_, i) {
                      final item = items[i];
                      return _CartItemCard(
                        item: item,
                        onRemove: () => _confirmRemove(context, item),
                        onIncrease:
                            () => _updateQuantity(item.id, item.quantity + 1),
                        onDecrease:
                            () => _updateQuantity(item.id, item.quantity - 1),
                      );
                    },
                  ),
                ),
              ),

              // ─── Bottom panel ──────────────────────────────
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.08),
                      blurRadius: 10,
                      offset: const Offset(0, -4),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    // ─── Coupon field ────────────────────────
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _couponCtrl,
                            textCapitalization: TextCapitalization.characters,
                            decoration: InputDecoration(
                              labelText: 'Coupon code',
                              hintText: 'e.g. SAVE20',
                              prefixIcon: const Icon(Icons.discount_outlined),
                              border: const OutlineInputBorder(),
                              suffixIcon:
                                  _couponCtrl.text.isNotEmpty
                                      ? IconButton(
                                        icon: const Icon(Icons.clear),
                                        onPressed: () {
                                          _couponCtrl.clear();
                                          setState(
                                            () => _couponApplied = false,
                                          );
                                        },
                                      )
                                      : null,
                            ),
                            onChanged:
                                (_) => setState(() => _couponApplied = false),
                          ),
                        ),
                        const SizedBox(width: 8),
                        ElevatedButton(
                          onPressed:
                              _couponCtrl.text.trim().isEmpty
                                  ? null
                                  : () => setState(() => _couponApplied = true),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.deepPurple,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(
                              vertical: 16,
                              horizontal: 16,
                            ),
                          ),
                          child: const Text('Apply'),
                        ),
                      ],
                    ),

                    if (_couponApplied)
                      Padding(
                        padding: const EdgeInsets.only(top: 8),
                        child: Row(
                          children: [
                            const Icon(
                              Icons.check_circle,
                              color: Colors.green,
                              size: 16,
                            ),
                            const SizedBox(width: 4),
                            Text(
                              'Coupon "${_couponCtrl.text.trim()}" will be applied at checkout',
                              style: const TextStyle(
                                color: Colors.green,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      ),

                    const SizedBox(height: 16),

                    // ─── Price summary ───────────────────────
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          '${cartNotifier.itemCount} item${cartNotifier.itemCount > 1 ? 's' : ''}',
                          style: const TextStyle(color: Colors.grey),
                        ),
                        Text(
                          '₹${cartNotifier.total.toStringAsFixed(0)}',
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: Colors.deepPurple,
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 12),

                    // ─── Checkout button ─────────────────────
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: _checkingOut ? null : _checkout,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.deepPurple,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child:
                            _checkingOut
                                ? const Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    SizedBox(
                                      width: 20,
                                      height: 20,
                                      child: CircularProgressIndicator(
                                        color: Colors.white,
                                        strokeWidth: 2,
                                      ),
                                    ),
                                    SizedBox(width: 12),
                                    Text(
                                      'Placing Order...',
                                      style: TextStyle(fontSize: 16),
                                    ),
                                  ],
                                )
                                : const Text(
                                  'Proceed to Checkout',
                                  style: TextStyle(fontSize: 16),
                                ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

// ─── Cart Item Card Widget ───────────────────────────────────

class _CartItemCard extends StatelessWidget {
  final CartItem item;
  final VoidCallback onRemove;
  final VoidCallback onIncrease;
  final VoidCallback onDecrease;

  const _CartItemCard({
    required this.item,
    required this.onRemove,
    required this.onIncrease,
    required this.onDecrease,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            // ─── Product image placeholder ───────────────────
            Container(
              width: 70,
              height: 70,
              decoration: BoxDecoration(
                color: Colors.deepPurple.shade50,
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(
                Icons.shopping_bag,
                color: Colors.deepPurple,
                size: 32,
              ),
            ),
            const SizedBox(width: 12),

            // ─── Product info ────────────────────────────────
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item.product.name,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 15,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '₹${item.product.price.toStringAsFixed(0)} each',
                    style: const TextStyle(color: Colors.grey, fontSize: 13),
                  ),
                  const SizedBox(height: 8),

                  // ─── Quantity controls + subtotal ────────────
                  Row(
                    children: [
                      // Decrease
                      InkWell(
                        onTap: onDecrease,
                        borderRadius: BorderRadius.circular(20),
                        child: Container(
                          padding: const EdgeInsets.all(4),
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            border: Border.all(color: Colors.deepPurple),
                          ),
                          child: const Icon(
                            Icons.remove,
                            size: 16,
                            color: Colors.deepPurple,
                          ),
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        child: Text(
                          '${item.quantity}',
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      // Increase
                      InkWell(
                        onTap:
                            item.quantity < item.product.stock
                                ? onIncrease
                                : null,
                        borderRadius: BorderRadius.circular(20),
                        child: Container(
                          padding: const EdgeInsets.all(4),
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            border: Border.all(
                              color:
                                  item.quantity < item.product.stock
                                      ? Colors.deepPurple
                                      : Colors.grey,
                            ),
                          ),
                          child: Icon(
                            Icons.add,
                            size: 16,
                            color:
                                item.quantity < item.product.stock
                                    ? Colors.deepPurple
                                    : Colors.grey,
                          ),
                        ),
                      ),
                      const Spacer(),
                      // Subtotal
                      Text(
                        '₹${item.subtotal.toStringAsFixed(0)}',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 15,
                          color: Colors.deepPurple,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            // ─── Remove button ───────────────────────────────
            IconButton(
              onPressed: onRemove,
              icon: const Icon(Icons.delete_outline, color: Colors.red),
            ),
          ],
        ),
      ),
    );
  }
}
