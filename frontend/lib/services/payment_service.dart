import 'package:flutter/material.dart';
import 'package:razorpay_flutter/razorpay_flutter.dart';
import '../core/dio_client.dart';

class PaymentService {
  final _dio = DioClient.instance;

  Future<void> initiateAndPay({
    required BuildContext context,
    required int orderId,
    required VoidCallback onSuccess,
    required Function(String) onError,
  }) async {
    // Step 1 — create Razorpay order on backend
    final initResponse = await _dio.post('/payments/initiate/$orderId');
    final data = initResponse.data;

    final razorpay = Razorpay();

    razorpay.on(Razorpay.EVENT_PAYMENT_SUCCESS, (
      PaymentSuccessResponse response,
    ) async {
      try {
        // Step 2 — verify with backend
        await _dio.post(
          '/payments/verify/$orderId',
          data: {
            'razorpay_order_id': response.orderId,
            'razorpay_payment_id': response.paymentId,
            'razorpay_signature': response.signature,
          },
        );
        onSuccess();
      } catch (e) {
        onError('Verification failed: $e');
      } finally {
        razorpay.clear();
      }
    });

    razorpay.on(Razorpay.EVENT_PAYMENT_ERROR, (
      PaymentFailureResponse response,
    ) {
      onError(response.message ?? 'Payment failed');
      razorpay.clear();
    });

    razorpay.on(Razorpay.EVENT_EXTERNAL_WALLET, (
      ExternalWalletResponse response,
    ) {
      razorpay.clear();
    });

    // Step 3 — open Razorpay checkout
    razorpay.open({
      'key': data['key_id'],
      'amount': data['amount'],
      'currency': data['currency'],
      'name': 'E-Commerce App',
      'order_id': data['razorpay_order_id'],
      'description': 'Order #$orderId',
      'prefill': {'contact': '', 'email': ''},
    });
  }
}
