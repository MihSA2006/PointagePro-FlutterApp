import 'package:flutter/material.dart';

import 'dart:async';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';
import 'attendance_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Map<String, dynamic>? _userData;
  List<dynamic> _recentHistory = [];
  bool _isLoading = true;
  
  Timer? _timer;
  int _elapsedSeconds = 0;
  bool _isWorking = false;

  @override
  void initState() {
    super.initState();
    _fetchData();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _fetchData() async {
    try {
      final responses = await Future.wait([
        ApiService.getProfile(),
        ApiService.getAttendanceHistory(),
      ]);

      final userProfile = responses[0].data;
      final attendanceData = responses[1].data;
      
      List<dynamic> history = [];
      if (attendanceData is Map && attendanceData.containsKey('results')) {
        history = attendanceData['results'];
      } else if (attendanceData is List) {
        history = attendanceData;
      }

      setState(() {
        _userData = userProfile;
        _recentHistory = history.take(3).toList();
        _isLoading = false;
      });

      _checkTimerState(history);

    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        debugPrint('Error fetching home data: $e');
      }
    }
  }

  void _checkTimerState(List<dynamic> history) {
    // Find if there's an active session today
    final today = DateFormat('yyyy-MM-dd').format(DateTime.now());
    final todayRecord = history.firstWhere(
      (record) => record['date'] == today && record['status'] == 'active',
      orElse: () => null,
    );

    if (todayRecord != null && todayRecord['check_in_time'] != null) {
      final checkInTime = DateTime.parse(todayRecord['check_in_time']).toLocal();
      final now = DateTime.now();
      _elapsedSeconds = now.difference(checkInTime).inSeconds;
      _startTimer();
    } else {
      _timer?.cancel();
      setState(() {
        _isWorking = false;
        _elapsedSeconds = 0;
      });
    }
  }

  void _startTimer() {
    _timer?.cancel();
    _isWorking = true;
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (mounted) {
        setState(() {
          _elapsedSeconds++;
        });
      }
    });
  }

  String _formatDuration(int seconds) {
    final hours = seconds ~/ 3600;
    final minutes = (seconds % 3600) ~/ 60;
    final remainingSeconds = seconds % 60;
    return '${hours.toString().padLeft(2, '0')}:${minutes.toString().padLeft(2, '0')}:${remainingSeconds.toString().padLeft(2, '0')}';
  }

  String _getTimeGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'Bonjour';
    if (hour < 18) return 'Bon après-midi';
    return 'Bonsoir';
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator(color: Color(0xFFC89664)));
    }

    final user = _userData ?? {};
    final fullName = user['full_name'] ?? 'Utilisateur';
    final firstName = user['first_name'] ?? (fullName.split(' ').first);
    final initials = (user['first_name'] != null && user['last_name'] != null)
        ? '${user['first_name'][0]}${user['last_name'][0]}'.toUpperCase()
        : fullName.substring(0, 2).toUpperCase();

    return Stack(
      children: [
        // Background Image
        Positioned.fill(
          child: Image.asset(
            'assets/images/bg.png',
            fit: BoxFit.cover,
          ),
        ),
        // Dark Overlay
        Positioned.fill(
          child: Container(
            color: const Color(0xFF010E22).withOpacity(0.85),
          ),
        ),
        
        SafeArea(
          bottom: false,
          child: RefreshIndicator(
            onRefresh: _fetchData,
            color: const Color(0xFFC89664),
            backgroundColor: const Color(0xFF03294E),
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // --- HEADER ---
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                DateTime.now().hour < 18 ? Icons.wb_sunny_outlined : Icons.nightlight_round,
                                color: const Color(0xFFC89664),
                                size: 16,
                              ),
                              const SizedBox(width: 8),
                              Text(
                                _getTimeGreeting(),
                                style: TextStyle(
                                  color: Colors.white.withOpacity(0.7),
                                  fontSize: 16,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 4),
                          Text(
                            firstName,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 28,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            user['department_name'] ?? 'Département non spécifié',
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.5),
                              fontSize: 14,
                            ),
                          ),
                        ],
                      ),
                      Container(
                        width: 45,
                        height: 45,
                        decoration: const BoxDecoration(
                          color: Color(0xFFC89664),
                          shape: BoxShape.circle,
                        ),
                        child: Center(
                          child: Text(
                            initials,
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                  
                  const SizedBox(height: 30),
                  
                  // --- POINTER MAINTENANT SECTION ---
                  GestureDetector(
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => const AttendanceScreen()),
                      );
                    },
                    child: Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            const Color(0xFF256B97).withOpacity(0.8),
                            const Color(0xFF03294E).withOpacity(0.9),
                          ],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(24),
                        border: Border.all(
                          color: const Color(0xFF256B97).withOpacity(0.3),
                          width: 1.5,
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFF256B97).withOpacity(0.2),
                            blurRadius: 20,
                            offset: const Offset(0, 10),
                          ),
                        ],
                      ),
                      child: Row(
                        children: [
                          Container(
                            width: 60,
                            height: 60,
                            decoration: BoxDecoration(
                              color: const Color(0xFFEB721B),
                              borderRadius: BorderRadius.circular(16),
                              boxShadow: [
                                BoxShadow(
                                  color: const Color(0xFFEB721B).withOpacity(0.3),
                                  blurRadius: 10,
                                  offset: const Offset(0, 4),
                                ),
                              ],
                            ),
                            child: const Icon(Icons.qr_code_scanner_rounded, color: Colors.white, size: 35),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  _isWorking ? 'Session en cours' : 'Prêt à commencer',
                                  style: TextStyle(
                                    color: Colors.white.withOpacity(0.7),
                                    fontSize: 14,
                                  ),
                                ),
                                const Text(
                                  'Pointer maintenant',
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 20,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          Icon(
                            Icons.arrow_forward_ios_rounded,
                            color: Colors.white.withOpacity(0.5),
                            size: 18,
                          ),
                        ],
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 25),
                  
                  // --- STATS ROW ---
                  Row(
                    children: [
                      // Status card (Replacing Congés restants)
                      Expanded(
                        child: _buildStatCard(
                          icon: _isWorking ? Icons.work_outline : Icons.work_off_outlined,
                          iconColor: _isWorking ? Colors.greenAccent : Colors.grey,
                          title: 'Statut',
                          value: _isWorking ? 'En poste' : 'Inactif',
                          unit: '',
                        ),
                      ),
                      const SizedBox(width: 16),
                      // Chrono heure de travail
                      Expanded(
                        child: _buildStatCard(
                          icon: Icons.timer_outlined,
                          iconColor: const Color(0xFFEB721B),
                          title: 'Heures de travail',
                          value: _formatDuration(_elapsedSeconds),
                          unit: '',
                        ),
                      ),
                    ],
                  ),
                  
                  const SizedBox(height: 25),
                  
                  // --- HISTORY SECTION ---
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Historique récent',
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.8),
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      if (_recentHistory.isNotEmpty)
                        Text(
                          'Les 3 derniers',
                          style: TextStyle(
                            color: Colors.white.withOpacity(0.4),
                            fontSize: 12,
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 15),
                  
                  if (_recentHistory.isEmpty)
                    Container(
                      padding: const EdgeInsets.symmetric(vertical: 40),
                      width: double.infinity,
                      decoration: BoxDecoration(
                        color: const Color(0xFF233E5C).withOpacity(0.1),
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Column(
                        children: [
                          Icon(Icons.history, color: Colors.white.withOpacity(0.2), size: 40),
                          const SizedBox(height: 12),
                          Text(
                            'Aucun historique récent',
                            style: TextStyle(color: Colors.white.withOpacity(0.3)),
                          ),
                        ],
                      ),
                    )
                  else
                    ..._recentHistory.map((item) {
                      final isCheckIn = item['check_out_time'] == null && item['status'] == 'active';
                      final time = item['check_in_time'] != null 
                          ? DateFormat('hh:mm a').format(DateTime.parse(item['check_in_time']).toLocal())
                          : '--:--';
                      final dateStr = item['date'] == DateFormat('yyyy-MM-dd').format(DateTime.now())
                          ? 'Aujourd\'hui'
                          : item['date'];
                      
                      return _buildHistoryItem(
                        title: item['status'] == 'active' ? 'Entrée (En cours)' : 'Session complète',
                        time: time,
                        date: dateStr,
                        icon: item['status'] == 'active' ? Icons.login_rounded : Icons.check_circle_outline,
                        color: item['status'] == 'active' ? Colors.greenAccent : const Color(0xFFC89664),
                        duration: item['work_duration_display'],
                      );
                    }).toList(),
                  
                  const SizedBox(height: 100), // Height for BottomNav
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String value,
    required String unit,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF03294E).withOpacity(0.4),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: const Color(0xFF256B97).withOpacity(0.1),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: iconColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: iconColor, size: 20),
          ),
          const SizedBox(height: 16),
          Text(
            title,
            style: TextStyle(
              color: Colors.white.withOpacity(0.5),
              fontSize: 13,
            ),
          ),
          const SizedBox(height: 4),
          Row(
            crossAxisAlignment: CrossAxisAlignment.baseline,
            textBaseline: TextBaseline.alphabetic,
            children: [
              Text(
                value,
                style: TextStyle(
                  color: Colors.white,
                  fontSize: value.length > 8 ? 16 : 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
              if (unit.isNotEmpty) ...[
                const SizedBox(width: 4),
                Text(
                  unit,
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.5),
                    fontSize: 12,
                  ),
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildHistoryItem({
    required String title,
    required String time,
    required String date,
    required IconData icon,
    required Color color,
    String? duration,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF233E5C).withOpacity(0.2),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: const Color(0xFF256B97).withOpacity(0.1),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 15,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                Text(
                  date,
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.4),
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                time,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
              if (duration != null && duration != '0 min' && duration != '0')
                Text(
                  duration,
                  style: TextStyle(
                    color: const Color(0xFFC89664).withOpacity(0.8),
                    fontSize: 11,
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }
}
