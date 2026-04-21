import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import '../services/api_service.dart';
import 'package:dio/dio.dart';
import 'dart:ui';

class AttendanceScreen extends StatefulWidget {
  const AttendanceScreen({super.key});

  @override
  State<AttendanceScreen> createState() => _AttendanceScreenState();
}

class _AttendanceScreenState extends State<AttendanceScreen> {
  bool _isScannerActive = false;
  final MobileScannerController _controller = MobileScannerController(
    detectionSpeed: DetectionSpeed.normal,
    facing: CameraFacing.back,
    torchEnabled: false,
  );

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _toggleScanner() {
    setState(() {
      _isScannerActive = !_isScannerActive;
    });
  }

  @override
  Widget build(BuildContext context) {
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
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 30),
            child: Column(
              children: [
                const SizedBox(height: 40),
                // Title
                const Text(
                  'QR Check',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1.2,
                  ),
                ),
                const SizedBox(height: 12),
                // Description
                const Text(
                  'Effortless attendance starts here. One scan for quick and secure check-in or check-out.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 16,
                    height: 1.5,
                  ),
                ),
                
                const Spacer(),
                
                if (!_isScannerActive)
                  // Illustration when scanner is not active
                  Image.asset(
                    'assets/images/check_img.png',
                    width: MediaQuery.of(context).size.width * 0.8,
                    fit: BoxFit.contain,
                  )
                else
                  // Live Scanner
                  _buildScannerView(),
                
                const Spacer(),
                
                // Toggle Button
                SizedBox(
                  width: double.infinity,
                  height: 60,
                  child: ElevatedButton(
                    onPressed: _toggleScanner,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _isScannerActive ? Colors.red.withOpacity(0.8) : const Color(0xFFEB721B),
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(30),
                      ),
                      elevation: 8,
                      shadowColor: ( _isScannerActive ? Colors.red : const Color(0xFFEB721B)).withOpacity(0.4),
                    ),
                    child: Text(
                      _isScannerActive ? 'Cancel' : 'Check',
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 100), // Space for bottom nav
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildScannerView() {
    return Container(
      width: double.infinity,
      height: 300,
      decoration: BoxDecoration(
        color: Colors.black,
        borderRadius: BorderRadius.circular(30),
        border: Border.all(color: const Color(0xFF256B97), width: 2),
      ),
      clipBehavior: Clip.antiAlias,
      child: Stack(
        children: [
          MobileScanner(
            controller: _controller,
            onDetect: (capture) {
              final List<Barcode> barcodes = capture.barcodes;
              if (barcodes.isNotEmpty) {
                final String? code = barcodes.first.rawValue;
                if (code != null) {
                  _onQRCodeScanned(code);
                }
              }
            },
          ),
          // Scanner Overlay
          _buildScannerOverlay(),
        ],
      ),
    );
  }

  Widget _buildScannerOverlay() {
    return Stack(
      children: [
        // Focus Box (Visual only)
        Center(
          child: Container(
            width: 200,
            height: 200,
            decoration: BoxDecoration(
              border: Border.all(color: const Color(0xFFC89664), width: 3),
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
        // Scanner Line Animation Placeholder
        // (You could add a moving line here for better effect)
      ],
    );
  }

  void _onQRCodeScanned(String code) async {
    // Stop scanner preview effectively
    _controller.stop();
    setState(() {
      _isScannerActive = false;
    });

    // Show loading dialog
    _showLoadingDialog();

    try {
      final response = await ApiService.scanQRCode(code);
      final data = response.data;

      // Close loading dialog
      if (mounted) Navigator.pop(context);

      if (mounted) {
        _showSuccessDialog(
          message: data['message'] ?? 'Check-in successful!',
          isCheckIn: data['message'].toString().toLowerCase().contains('check-in'),
          details: data['data'],
        );
      }
    } on DioException catch (e) {
      // Close loading dialog
      if (mounted) Navigator.pop(context);

      String message = 'Scanning failed';
      if (e.response?.data != null && e.response?.data is Map) {
        message = e.response?.data['detail'] ?? e.response?.data['message'] ?? message;
      }
      
      if (mounted) {
        _showErrorDialog(message);
      }
    } catch (e) {
      // Close loading dialog
      if (mounted) Navigator.pop(context);
      if (mounted) _showErrorDialog('Error: $e');
    }
  }

  void _showLoadingDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 5, sigmaY: 5),
        child: Center(
          child: Container(
            padding: const EdgeInsets.all(32),
            decoration: BoxDecoration(
              color: const Color(0xFF03294E).withOpacity(0.8),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: Colors.white.withOpacity(0.1)),
            ),
            child: const CircularProgressIndicator(color: Color(0xFFEB721B)),
          ),
        ),
      ),
    );
  }

  void _showSuccessDialog({required String message, required bool isCheckIn, Map<String, dynamic>? details}) {
    showDialog(
      context: context,
      builder: (context) => BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 5, sigmaY: 5),
        child: AlertDialog(
          backgroundColor: const Color(0xFF03294E).withOpacity(0.9),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                isCheckIn ? Icons.check_circle_outline : Icons.exit_to_app,
                color: const Color(0xFFEB721B),
                size: 64,
              ),
              const SizedBox(height: 24),
              Text(
                message,
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
              ),
              if (details != null) ...[
                const SizedBox(height: 16),
                Text(
                  isCheckIn ? 'Time: ${details['check_in_time_display'] ?? ""}' : 'Duration: ${details['work_duration_display'] ?? ""}',
                  style: TextStyle(color: Colors.white.withOpacity(0.7), fontSize: 14),
                ),
              ],
              const SizedBox(height: 32),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () => Navigator.pop(context),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFEB721B),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: const Text('Great!'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: AlertDialog(
          backgroundColor: const Color(0xFF010E22).withOpacity(0.9),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline, color: Colors.red, size: 64),
              const SizedBox(height: 24),
              Text(
                message,
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.white, fontSize: 16),
              ),
              const SizedBox(height: 32),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () => Navigator.pop(context),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white.withOpacity(0.1),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: const Text('Try Again', style: TextStyle(color: Colors.white)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
