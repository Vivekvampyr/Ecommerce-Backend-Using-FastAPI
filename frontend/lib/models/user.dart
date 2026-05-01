class User {
  final int id;
  final String email;
  final bool isAdmin;
  final String? avatar;

  User({
    required this.id,
    required this.email,
    required this.isAdmin,
    this.avatar,
  });

  factory User.fromJson(Map<String, dynamic> json) => User(
    id: json['id'],
    email: json['email'],
    isAdmin: json['is_admin'],
    avatar: json['avatar'],
  );
}
