import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import '../../core/api/api_client.dart';

/// FCM push notifications. Registers the device token with the backend so
/// Celery workers can notify when long jobs (transcription, reports) finish.
class PushService {
  static Future<void> init() async {
    try {
      await Firebase.initializeApp();
      final messaging = FirebaseMessaging.instance;
      await messaging.requestPermission();
      final token = await messaging.getToken();
      if (token != null) {
        await ApiClient.instance.dio
            .post('/auth/fcm-token', queryParameters: {'token': token});
      }
    } catch (_) {
      // Firebase not configured (e.g. local dev) — push is optional.
    }
  }
}
