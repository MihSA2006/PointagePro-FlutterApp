import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String host = "192.168.88.239";
  static const String baseUrl = "http://$host:8000/api";
  
  static final Dio _dio = Dio(BaseOptions(
    baseUrl: baseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  ));

  // Singleton pattern if needed, but static methods are fine for a simple service
  
  static Future<void> _initInterceptors() async {
    _dio.interceptors.clear();
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final prefs = await SharedPreferences.getInstance();
        final token = prefs.getString('access_token');
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (DioException e, handler) async {
        if (e.response?.statusCode == 401) {
          // Handle token refresh logic here if implemented in backend
          // For now, we'll just let it fail
        }
        return handler.next(e);
      },
    ));
  }

  // --- Auth Endpoints ---

  static Future<Response> register(Map<String, dynamic> data) async {
    return await _dio.post('/auth/register/', data: data);
  }

  static Future<Response> login(String email, String password) async {
    final response = await _dio.post('/auth/login/', data: {
      'email': email,
      'password': password,
    });
    
    if (response.statusCode == 200) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('access_token', response.data['access']);
      await prefs.setString('refresh_token', response.data['refresh']);
    }
    
    return response;
  }

  static Future<Response> logout() async {
    await _initInterceptors();
    final prefs = await SharedPreferences.getInstance();
    final refreshToken = prefs.getString('refresh_token');
    
    final response = await _dio.post('/auth/logout/', data: {
      'refresh': refreshToken,
    });
    
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
    
    return response;
  }

  static Future<Response> getProfile() async {
    await _initInterceptors();
    return await _dio.get('/auth/me/');
  }

  // --- Employee Endpoints ---

  static Future<Response> updateProfile(Map<String, dynamic> data) async {
    await _initInterceptors();
    return await _dio.patch('/employees/me/update/', data: data);
  }

  static Future<Response> getDepartments() async {
    await _initInterceptors();
    return await _dio.get('/employees/departments/');
  }

  // --- Attendance Endpoints ---

  static Future<Response> scanQRCode(String token) async {
    await _initInterceptors();
    return await _dio.post('/attendance/scan/', data: {
      'token': token,
    });
  }

  static Future<Response> getAttendanceHistory({String? dateFrom, String? dateTo, String? status}) async {
    await _initInterceptors();
    final Map<String, dynamic> queryParameters = {};
    if (dateFrom != null) queryParameters['date_from'] = dateFrom;
    if (dateTo != null) queryParameters['date_to'] = dateTo;
    if (status != null) queryParameters['status'] = status;
    
    return await _dio.get('/attendance/history/', queryParameters: queryParameters);
  }
}
