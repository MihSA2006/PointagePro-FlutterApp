import 'package:flutter/material.dart';
import 'main_screen.dart';
import '../services/api_service.dart';
import 'package:dio/dio.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  String? _selectedDepartmentId;
  bool _isPasswordVisible = false;
  bool _isLoading = false;
  bool _isFetchingDepartments = true;
  List<dynamic> _departments = [];

  @override
  void initState() {
    super.initState();
    _fetchDepartments();
  }

  Future<void> _fetchDepartments() async {
    try {
      final response = await ApiService.getDepartments();
      setState(() {
        _departments = response.data;
        _isFetchingDepartments = false;
      });
    } catch (e) {
      setState(() {
        _isFetchingDepartments = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load departments: $e')),
        );
      }
    }
  }

  Future<void> _handleRegister() async {
    final firstName = _firstNameController.text.trim();
    final lastName = _lastNameController.text.trim();
    final email = _emailController.text.trim();
    final password = _passwordController.text.trim();

    if (firstName.isEmpty || lastName.isEmpty || email.isEmpty || password.isEmpty || _selectedDepartmentId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please fill all fields')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      await ApiService.register({
        'first_name': firstName,
        'last_name': lastName,
        'email': email,
        'password': password,
        'department': int.parse(_selectedDepartmentId!),
        'role': 'employee',
      });
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Account created successfully! Please login.')),
        );
        Navigator.pop(context); // Go back to login
      }
    } on DioException catch (e) {
      String message = 'An error occurred';
      if (e.response?.data != null && e.response?.data is Map) {
        final data = e.response?.data;
        if (data is Map) {
          // Flatten error messages from Django REST Framework
          List<String> errors = [];
          data.forEach((key, value) {
            if (value is List) {
              errors.add('$key: ${value.join(", ")}');
            } else {
              errors.add('$key: $value');
            }
          });
          message = errors.join('\n');
        }
      }
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(message)),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
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
          
          SafeArea(
            child: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 40),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 40),
                  decoration: BoxDecoration(
                    color: const Color(0xFF03294E).withOpacity(0.4),
                    borderRadius: BorderRadius.circular(30),
                    border: Border.all(
                      color: const Color(0xFF256B97).withOpacity(0.2),
                      width: 1.5,
                    ),
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // Logo / Title
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Text(
                            'jacklyn',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 28,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(width: 4),
                          Text(
                            'employee',
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.7),
                              fontSize: 24,
                              fontWeight: FontWeight.w300,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Create your account to get started',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.6),
                          fontSize: 16,
                        ),
                      ),
                      const SizedBox(height: 40),
                      
                      // First Name Field
                      _buildTextField(
                        label: 'First Name',
                        hint: 'John',
                        controller: _firstNameController,
                        icon: Icons.person_outline,
                      ),
                      const SizedBox(height: 16),

                      // Last Name Field
                      _buildTextField(
                        label: 'Last Name',
                        hint: 'Doe',
                        controller: _lastNameController,
                        icon: Icons.person_outline,
                      ),
                      const SizedBox(height: 16),
                      
                      // Email Field
                      _buildTextField(
                        label: 'Email',
                        hint: 'john.doe@company.com',
                        controller: _emailController,
                        icon: Icons.email_outlined,
                      ),
                      const SizedBox(height: 16),
                      
                      // Password Field
                      _buildTextField(
                        label: 'Password',
                        hint: '********',
                        controller: _passwordController,
                        icon: Icons.lock_outline,
                        isPassword: true,
                        isPasswordVisible: _isPasswordVisible,
                        onToggleVisibility: () {
                          setState(() {
                            _isPasswordVisible = !_isPasswordVisible;
                          });
                        },
                      ),
                      const SizedBox(height: 16),

                      // Department Field
                      _buildDropdownField(
                        label: 'Department',
                        value: _selectedDepartmentId,
                        items: _departments,
                        isLoading: _isFetchingDepartments,
                        onChanged: (val) {
                          setState(() {
                            _selectedDepartmentId = val;
                          });
                        },
                      ),
                      
                      const SizedBox(height: 32),
                      
                      // Register Button
                      SizedBox(
                        width: double.infinity,
                        height: 60,
                        child: ElevatedButton(
                          onPressed: _isLoading || _isFetchingDepartments ? null : _handleRegister,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFFEB721B),
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(20),
                            ),
                            disabledBackgroundColor: const Color(0xFFEB721B).withOpacity(0.5),
                            elevation: 0,
                          ),
                          child: _isLoading
                              ? const SizedBox(
                                  height: 24,
                                  width: 24,
                                  child: CircularProgressIndicator(
                                    color: Colors.white,
                                    strokeWidth: 2,
                                  ),
                                )
                              : Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: const [
                                    Icon(Icons.person_add_outlined, size: 20),
                                    SizedBox(width: 12),
                                    Text(
                                      'Register',
                                      style: TextStyle(
                                        fontSize: 18,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ],
                                ),
                        ),
                      ),
                      
                      const SizedBox(height: 24),
                      
                      // Login Link
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            "Already have an account?",
                            style: TextStyle(color: Colors.white.withOpacity(0.6)),
                          ),
                          TextButton(
                            onPressed: () {
                              Navigator.pop(context);
                            },
                            child: const Text(
                              'Login',
                              style: TextStyle(
                                color: Color(0xFFC89664),
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
          
          // Back Button
          Positioned(
            top: 50,
            left: 20,
            child: IconButton(
              icon: const Icon(Icons.arrow_back, color: Colors.white),
              onPressed: () => Navigator.pop(context),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTextField({
    required String label,
    required String hint,
    required TextEditingController controller,
    required IconData icon,
    bool isPassword = false,
    bool isPasswordVisible = false,
    VoidCallback? onToggleVisibility,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            color: Colors.white.withOpacity(0.7),
            fontSize: 14,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          decoration: BoxDecoration(
            color: const Color(0xFF010E22).withOpacity(0.5),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: Colors.white.withOpacity(0.1),
              width: 1,
            ),
          ),
          child: TextField(
            controller: controller,
            obscureText: isPassword && !isPasswordVisible,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              hintText: hint,
              hintStyle: TextStyle(color: Colors.white.withOpacity(0.3)),
              prefixIcon: Icon(icon, color: Colors.white.withOpacity(0.5), size: 20),
              suffixIcon: isPassword
                  ? IconButton(
                      icon: Icon(
                        isPasswordVisible ? Icons.visibility : Icons.visibility_off,
                        color: Colors.white.withOpacity(0.5),
                        size: 20,
                      ),
                      onPressed: onToggleVisibility,
                    )
                  : null,
              border: InputBorder.none,
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDropdownField({
    required String label,
    required String? value,
    required List<dynamic> items,
    required bool isLoading,
    required ValueChanged<String?> onChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            color: Colors.white.withOpacity(0.7),
            fontSize: 14,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          decoration: BoxDecoration(
            color: const Color(0xFF010E22).withOpacity(0.5),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: Colors.white.withOpacity(0.1),
              width: 1,
            ),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              value: value,
              hint: Text(
                isLoading ? 'Loading...' : 'Select Department',
                style: TextStyle(color: Colors.white.withOpacity(0.3), fontSize: 16),
              ),
              dropdownColor: const Color(0xFF021C3B),
              icon: isLoading 
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.arrow_drop_down, color: Colors.white),
              isExpanded: true,
              style: const TextStyle(color: Colors.white, fontSize: 16),
              items: items.map((dynamic item) {
                return DropdownMenuItem<String>(
                  value: item['id'].toString(),
                  child: Text(item['name']),
                );
              }).toList(),
              onChanged: onChanged,
            ),
          ),
        ),
      ],
    );
  }
}
