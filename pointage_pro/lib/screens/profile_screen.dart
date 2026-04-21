import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'login_screen.dart';
import 'edit_profile_screen.dart';
import 'change_password_screen.dart';
import 'package:dio/dio.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Map<String, dynamic>? _userData;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchProfile();
  }

  Future<void> _fetchProfile() async {
    try {
      final response = await ApiService.getProfile();
      setState(() {
        _userData = response.data;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load profile: $e')),
        );
      }
    }
  }

  Future<void> _handleLogout() async {
    try {
      await ApiService.logout();
      if (mounted) {
        Navigator.pushAndRemoveUntil(
          context,
          MaterialPageRoute(builder: (context) => const LoginScreen()),
          (route) => false,
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Logout failed: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator(color: Color(0xFFEB721B)));
    }

    final user = _userData ?? {};

    return Stack(
      children: [
        // Background
        Positioned.fill(
          child: Image.asset(
            'assets/images/bg.png',
            fit: BoxFit.cover,
          ),
        ),
        Positioned.fill(
          child: Container(
            color: const Color(0xFF010E22).withOpacity(0.85),
          ),
        ),
        
        Column(
          children: [
            // Header Section
            Container(
              padding: const EdgeInsets.only(top: 60, bottom: 40),
              width: double.infinity,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    const Color(0xFF256B97).withOpacity(0.4),
                    const Color(0xFF03294E).withOpacity(0.6),
                  ],
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                ),
                borderRadius: const BorderRadius.vertical(bottom: Radius.circular(30)),
              ),
              child: Column(
                children: [
                  const Text(
                    'Profile',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 24),
                  // Profile Image
                  Stack(
                    children: [
                      Container(
                        width: 110,
                        height: 110,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.white, width: 3),
                          image: DecorationImage(
                            image: NetworkImage('https://api.dicebear.com/7.x/avataaars/png?seed=${user['full_name'] ?? 'User'}'),
                            fit: BoxFit.cover,
                          ),
                        ),
                      ),
                      Positioned(
                        bottom: 0,
                        right: 0,
                        child: Container(
                          padding: const EdgeInsets.all(4),
                          decoration: const BoxDecoration(
                            color: Color(0xFFC89664),
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(Icons.camera_alt, color: Colors.white, size: 18),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    user['full_name'] ?? 'User Name',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    user['role']?.toString().toUpperCase() ?? 'EMPLOYEE',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.6),
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
            
            // Content Section
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
                child: Column(
                  children: [
                    // Info Card
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: const Color(0xFF03294E).withOpacity(0.4),
                        borderRadius: BorderRadius.circular(24),
                        border: Border.all(
                          color: const Color(0xFF256B97).withOpacity(0.2),
                          width: 1,
                        ),
                      ),
                      child: Column(
                        children: [
                          _buildInfoRow('Full Name', user['full_name'] ?? '-'),
                          _buildDivider(),
                          _buildInfoRow('Email', user['email'] ?? '-'),
                          _buildDivider(),
                          _buildInfoRow('Department', user['department']?.toString() ?? '-'),
                          _buildDivider(),
                          _buildInfoRow('Status', (user['is_active'] ?? false) ? 'Active' : 'Inactive'),
                        ],
                      ),
                    ),
                    
                    const SizedBox(height: 24),
                    
                    // Actions
                    _buildActionItem(
                      icon: Icons.person_outline,
                      title: 'Edit Profile',
                      color: Colors.tealAccent,
                      onTap: () async {
                        final result = await Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => EditProfileScreen(userData: _userData!),
                          ),
                        );
                        if (result == true) {
                          _fetchProfile(); // Refresh profile after edit
                        }
                      },
                    ),
                    const SizedBox(height: 12),
                    _buildActionItem(
                      icon: Icons.lock_outline,
                      title: 'Change Password',
                      color: Colors.orangeAccent,
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const ChangePasswordScreen(),
                          ),
                        );
                      },
                    ),
                    const SizedBox(height: 12),
                    _buildActionItem(
                      icon: Icons.logout,
                      title: 'Logout',
                      color: Colors.redAccent,
                      onTap: _handleLogout,
                    ),
                    
                    const SizedBox(height: 100), // Height for BottomNav
                  ],
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              color: Colors.white.withOpacity(0.5),
              fontSize: 15,
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 15,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDivider() {
    return Divider(
      color: Colors.white.withOpacity(0.05),
      height: 1,
    );
  }

  Widget _buildActionItem({
    required IconData icon,
    required String title,
    required Color color,
    VoidCallback? onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFF03294E).withOpacity(0.2),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: Colors.white.withOpacity(0.05),
            width: 1,
          ),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: color, size: 20),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Text(
                title,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
            Icon(
              Icons.arrow_forward_ios_rounded,
              color: Colors.white.withOpacity(0.3),
              size: 16,
            ),
          ],
        ),
      ),
    );
  }
}
