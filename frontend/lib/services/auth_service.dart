import 'package:dio/dio.dart';
import '../core/dio_client.dart';
import '../core/storage.dart';
import '../models/user.dart';

class AuthService {
  final _dio = DioClient.instance;

  Future<String> login(String email, String password) async {
    final response = await _dio.post(
      '/users/token',
      data: FormData.fromMap({'username': email, 'password': password}),
      options: Options(contentType: 'application/x-www-form-urlencoded'),
    );
    final token = response.data['access_token'];
    await AppStorage.saveToken(token);
    return token;
  }

  Future<User> register(String email, String password) async {
    final response = await _dio.post(
      '/users/register',
      data: {'email': email, 'password': password},
    );
    return User.fromJson(response.data);
  }

  Future<User> getMe() async {
    final response = await _dio.get('/users/me');
    return User.fromJson(response.data);
  }

  Future<void> logout() async {
    await AppStorage.deleteToken();
  }
}
