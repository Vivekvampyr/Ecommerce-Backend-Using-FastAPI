import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user.dart';
import '../services/auth_service.dart';

final authServiceProvider = Provider((ref) => AuthService());

final userProvider = StateNotifierProvider<UserNotifier, AsyncValue<User?>>(
  (ref) => UserNotifier(ref.read(authServiceProvider)),
);

class UserNotifier extends StateNotifier<AsyncValue<User?>> {
  final AuthService _service;

  UserNotifier(this._service) : super(const AsyncValue.loading()) {
    loadUser();
  }

  Future<void> loadUser() async {
    try {
      final user = await _service.getMe();
      state = AsyncValue.data(user);
    } catch (_) {
      state = const AsyncValue.data(null);
    }
  }

  Future<void> login(String email, String password) async {
    state = const AsyncValue.loading();
    try {
      await _service.login(email, password);
      await loadUser();
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
      rethrow;
    }
  }

  Future<void> logout() async {
    await _service.logout();
    state = const AsyncValue.data(null);
  }
}
