import '../core/dio_client.dart';
import '../models/review.dart';

class ReviewService {
  final _dio = DioClient.instance;

  Future<List<Review>> getProductReviews(int productId) async {
    final response = await _dio.get('/reviews/product/$productId');
    return (response.data as List).map((r) => Review.fromJson(r)).toList();
  }

  Future<Review> createReview(
    int productId, {
    required int rating,
    String? title,
    String? body,
  }) async {
    final response = await _dio.post(
      '/reviews/product/$productId',
      data: {
        'rating': rating,
        if (title != null && title.isNotEmpty) 'title': title,
        if (body != null && body.isNotEmpty) 'body': body,
      },
    );
    return Review.fromJson(response.data);
  }

  Future<void> deleteReview(int reviewId) async {
    await _dio.delete('/reviews/$reviewId');
  }
}
