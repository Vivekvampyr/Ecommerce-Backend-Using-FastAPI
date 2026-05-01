import '../core/dio_client.dart';
import '../models/product.dart';

class ProductService {
  final _dio = DioClient.instance;

  Future<List<Product>> getProducts({
    String? search,
    int? categoryId,
    double? minPrice,
    double? maxPrice,
    bool? inStock,
    String sortBy = 'id',
    String order = 'asc',
    int page = 1,
    int limit = 10,
  }) async {
    final response = await _dio.get(
      '/shopping/products',
      queryParameters: {
        if (search != null) 'search': search,
        if (categoryId != null) 'category_id': categoryId,
        if (minPrice != null) 'min_price': minPrice,
        if (maxPrice != null) 'max_price': maxPrice,
        if (inStock != null) 'in_stock': inStock,
        'sort_by': sortBy,
        'order': order,
        'page': page,
        'limit': limit,
      },
    );
    return (response.data as List).map((p) => Product.fromJson(p)).toList();
  }

  Future<Product> getProduct(int id) async {
    final response = await _dio.get('/shopping/products/$id');
    return Product.fromJson(response.data);
  }
}
