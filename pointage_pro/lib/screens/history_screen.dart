import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'package:dio/dio.dart';
import 'package:intl/intl.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  List<dynamic> _history = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchHistory();
  }

  Future<void> _fetchHistory() async {
    try {
      final response = await ApiService.getAttendanceHistory();
      setState(() {
        _history = response.data['results'] ?? [];
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Échec du chargement de l\'historique : $e')),
        );
      }
    }
  }

  String _formatTime(String? timeStr) {
    if (timeStr == null) return '--:--';
    try {
      final dateTime = DateTime.parse(timeStr).toLocal();
      return DateFormat('hh:mm a').format(dateTime);
    } catch (e) {
      return '--:--';
    }
  }

  String _formatDate(String? dateStr) {
    if (dateStr == null) return 'Date inconnue';
    try {
      final date = DateTime.parse(dateStr);
      return DateFormat('EEEE, MMM d').format(date);
    } catch (e) {
      return dateStr;
    }
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'completed':
        return Colors.greenAccent;
      case 'active':
        return Colors.blueAccent;
      case 'absent':
        return Colors.redAccent;
      default:
        return const Color(0xFFEB721B);
    }
  }

  String _getStatusLabel(String status, bool isLate) {
    if (status.toLowerCase() == 'completed' && isLate) return 'Retard';
    if (status.toLowerCase() == 'completed') return 'À l\'heure';
    if (status.toLowerCase() == 'active') return 'En cours';
    if (status.toLowerCase() == 'absent') return 'Absent';
    return status.toUpperCase();
  }

  @override
  Widget build(BuildContext context) {

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
        
        SafeArea(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Pointages',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      'Votre journal d\'activité',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.5),
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 8),
              
              // List
              Expanded(
                child: _isLoading
                    ? const Center(child: CircularProgressIndicator(color: Color(0xFFEB721B)))
                    : _history.isEmpty
                        ? const Center(child: Text('Aucun historique trouvé', style: TextStyle(color: Colors.white70)))
                        : ListView.builder(
                            padding: const EdgeInsets.symmetric(horizontal: 20),
                            itemCount: _history.length,
                            itemBuilder: (context, index) {
                              final item = _history[index];
                              return _buildHistoryCard(item);
                            },
                          ),
              ),
              const SizedBox(height: 80), // Space for bottom nav
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildHistoryCard(dynamic item) {
    final statusColor = _getStatusColor(item['status'] ?? '');
    final isLate = item['is_late'] ?? false;
    final statusLabel = _getStatusLabel(item['status'] ?? '', isLate);

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF03294E).withOpacity(0.4),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(
          color: const Color(0xFF256B97).withOpacity(0.1),
          width: 1,
        ),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                _formatDate(item['date']),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  statusLabel,
                  style: TextStyle(
                    color: statusColor,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _buildDivider(),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              // Check In
              _buildTimeInfo('Entrée', _formatTime(item['check_in_time']), Icons.login_rounded, Colors.greenAccent),
              // Check Out
              _buildTimeInfo('Sortie', _formatTime(item['check_out_time']), Icons.logout_rounded, Colors.redAccent),
              // Duration
              _buildTimeInfo('Durée', item['work_duration_display'] ?? '0h 00', Icons.timer_outlined, const Color(0xFFC89664)),
            ],
          ),
          if (isLate && item['status']?.toLowerCase() != 'absent')
            Padding(
              padding: const EdgeInsets.only(top: 12),
              child: Row(
                children: [
                  const Icon(Icons.warning_amber_rounded, color: Color(0xFFEB721B), size: 14),
                  const SizedBox(width: 4),
                  Text(
                    'Retard de ${item['late_minutes'] ?? 0}m',
                    style: const TextStyle(
                      color: Color(0xFFEB721B),
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildTimeInfo(String label, String time, IconData icon, Color iconColor) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 12, color: iconColor),
            const SizedBox(width: 4),
            Text(
              label,
              style: TextStyle(
                color: Colors.white.withOpacity(0.4),
                fontSize: 11,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Text(
          time,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 14,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildDivider() {
    return Container(
      height: 1,
      width: double.infinity,
      color: Colors.white.withOpacity(0.05),
    );
  }
}
