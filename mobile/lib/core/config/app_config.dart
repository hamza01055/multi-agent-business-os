/// Compile-time configuration.
/// Run with: flutter run --dart-define=API_BASE_URL=https://host/api/v1
///
/// TODO(physical-device): 10.0.2.2 only resolves to the host machine from the
/// Android EMULATOR's virtual network — a real phone cannot reach it at all.
/// When running on a physical device (over USB or the same Wi-Fi/LAN as the
/// dev machine), you MUST override this at launch, e.g.:
///   flutter run --dart-define=API_BASE_URL=http://<your-lan-ip>:8080/api/v1
/// Find <your-lan-ip> via `ipconfig` (Windows) — look for the Wi-Fi adapter's
/// IPv4 address (e.g. 192.168.1.42). Also ensure the backend server binds to
/// 0.0.0.0 (not 127.0.0.1) and that the phone + dev machine are on the same
/// network with no firewall blocking the port.
class AppConfig {
  static const apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8080/api/v1', // Android emulator → host
  );
}
