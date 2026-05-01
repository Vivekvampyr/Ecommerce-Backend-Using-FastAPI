import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../services/product_service.dart';
import '../../models/product.dart';
import '../../providers/cart_provider.dart';

final productListProvider =
    FutureProvider.family<List<Product>, Map<String, dynamic>>((
      ref,
      params,
    ) async {
      return ProductService().getProducts(
        search: params['search'],
        categoryId: params['category_id'],
        minPrice: params['min_price'],
        maxPrice: params['max_price'],
        inStock: params['in_stock'],
        sortBy: params['sort_by'] ?? 'id',
        order: params['order'] ?? 'asc',
        page: params['page'] ?? 1,
      );
    });

class ProductListScreen extends ConsumerStatefulWidget {
  final int productID;
  const ProductListScreen({super.key, required this.productID});
  @override
  ConsumerState<ProductListScreen> createState() => _ProductListScreenState();
}

class _ProductListScreenState extends ConsumerState<ProductListScreen> {
  final _searchCtrl = TextEditingController();
  Map<String, dynamic> _params = {};

  @override
  Widget build(BuildContext context) {
    final products = ref.watch(productListProvider(_params));
    final cartCount = ref.watch(cartProvider.notifier).itemCount;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Shop'),
        actions: [
          Stack(
            children: [
              IconButton(
                icon: const Icon(Icons.shopping_cart),
                onPressed: () => context.go('/cart'),
              ),
              if (cartCount > 0)
                Positioned(
                  right: 6,
                  top: 6,
                  child: CircleAvatar(
                    radius: 9,
                    backgroundColor: Colors.red,
                    child: Text(
                      '$cartCount',
                      style: const TextStyle(fontSize: 11, color: Colors.white),
                    ),
                  ),
                ),
            ],
          ),
        ],
      ),
      body: Column(
        children: [
          // ─── Search bar ────────────────────────────────────
          Padding(
            padding: const EdgeInsets.all(12),
            child: TextField(
              controller: _searchCtrl,
              decoration: InputDecoration(
                hintText: 'Search products...',
                prefixIcon: const Icon(Icons.search),
                border: const OutlineInputBorder(),
                suffixIcon: IconButton(
                  icon: const Icon(Icons.clear),
                  onPressed: () {
                    _searchCtrl.clear();
                    setState(() => _params = {});
                  },
                ),
              ),
              onSubmitted: (value) {
                setState(() => _params = {'search': value});
              },
            ),
          ),

          // ─── Filter chips ──────────────────────────────────
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: Row(
              children: [
                FilterChip(
                  label: const Text('In Stock'),
                  selected: _params['in_stock'] == true,
                  onSelected:
                      (v) => setState(
                        () =>
                            _params = {..._params, 'in_stock': v ? true : null},
                      ),
                ),
                const SizedBox(width: 8),
                FilterChip(
                  label: const Text('Price: Low to High'),
                  selected:
                      _params['sort_by'] == 'price' &&
                      _params['order'] == 'asc',
                  onSelected:
                      (v) => setState(
                        () =>
                            _params = {
                              ..._params,
                              'sort_by': 'price',
                              'order': 'asc',
                            },
                      ),
                ),
                const SizedBox(width: 8),
                FilterChip(
                  label: const Text('Price: High to Low'),
                  selected:
                      _params['sort_by'] == 'price' &&
                      _params['order'] == 'desc',
                  onSelected:
                      (v) => setState(
                        () =>
                            _params = {
                              ..._params,
                              'sort_by': 'price',
                              'order': 'desc',
                            },
                      ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 8),

          // ─── Product grid ──────────────────────────────────
          Expanded(
            child: products.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Center(child: Text('Error: $e')),
              data:
                  (list) => GridView.builder(
                    padding: const EdgeInsets.all(12),
                    gridDelegate:
                        const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 2,
                          childAspectRatio: 0.75,
                          crossAxisSpacing: 12,
                          mainAxisSpacing: 12,
                        ),
                    itemCount: list.length,
                    itemBuilder: (_, i) => _ProductCard(product: list[i]),
                  ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ProductCard extends ConsumerWidget {
  final Product product;
  const _ProductCard({required this.product});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return GestureDetector(
      onTap: () => context.go('/products/${product.id}'),
      child: Card(
        elevation: 3,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Product image placeholder
            Container(
              height: 130,
              decoration: BoxDecoration(
                color: Colors.deepPurple.shade50,
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(12),
                ),
              ),
              child: const Center(
                child: Icon(Icons.image, size: 50, color: Colors.deepPurple),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    product.name,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '₹${product.price.toStringAsFixed(0)}',
                    style: const TextStyle(
                      color: Colors.deepPurple,
                      fontWeight: FontWeight.w600,
                      fontSize: 15,
                    ),
                  ),
                  const SizedBox(height: 4),
                  if (product.averageRating != null &&
                      product.averageRating! > 0)
                    Row(
                      children: [
                        const Icon(Icons.star, size: 14, color: Colors.amber),
                        Text(
                          ' ${product.averageRating} (${product.totalReviews})',
                          style: const TextStyle(fontSize: 12),
                        ),
                      ],
                    ),
                  if (product.stock == 0)
                    const Text(
                      'Out of Stock',
                      style: TextStyle(color: Colors.red, fontSize: 11),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
