import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/auth_provider.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final userState = ref.watch(userProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: userState.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, __) => const Center(child: Text('Failed to load profile')),
        data: (user) {
          if (user == null) return const Center(child: Text('Not logged in'));

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                // ─── Avatar ────────────────────────────────
                CircleAvatar(
                  radius: 50,
                  backgroundColor: Colors.deepPurple.shade100,
                  backgroundImage:
                      user.avatar != null ? NetworkImage(user.avatar!) : null,
                  child:
                      user.avatar == null
                          ? Text(
                            user.email[0].toUpperCase(),
                            style: const TextStyle(
                              fontSize: 36,
                              color: Colors.deepPurple,
                            ),
                          )
                          : null,
                ),
                const SizedBox(height: 16),
                Text(
                  user.email,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                if (user.isAdmin)
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.deepPurple.shade50,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const Text(
                      'Admin',
                      style: TextStyle(
                        color: Colors.deepPurple,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                const SizedBox(height: 32),

                // ─── Menu items ─────────────────────────────
                _ProfileTile(
                  icon: Icons.list_alt,
                  title: 'My Orders',
                  onTap: () => context.go('/orders'),
                ),
                _ProfileTile(
                  icon: Icons.shopping_cart,
                  title: 'My Cart',
                  onTap: () => context.go('/cart'),
                ),
                _ProfileTile(
                  icon: Icons.store,
                  title: 'Browse Products',
                  onTap: () => context.go('/products'),
                ),

                const Divider(height: 32),

                _ProfileTile(
                  icon: Icons.logout,
                  title: 'Logout',
                  color: Colors.red,
                  onTap: () async {
                    await ref.read(userProvider.notifier).logout();
                    if (context.mounted) context.go('/auth/login');
                  },
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _ProfileTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final VoidCallback onTap;
  final Color? color;
  const _ProfileTile({
    required this.icon,
    required this.title,
    required this.onTap,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(icon, color: color ?? Colors.deepPurple),
        title: Text(title, style: TextStyle(color: color)),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }
}
