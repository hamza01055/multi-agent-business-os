import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api/api_client.dart';
import '../../core/theme/app_theme.dart';

/// User profile + settings: account info, dark mode toggle.
class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});
  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  String _email = '';
  String _name = '';

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final resp = await ApiClient.instance.dio.get('/auth/me');
    if (!mounted) return;
    setState(() {
      _email = resp.data['email'] ?? '';
      _name = resp.data['full_name'] ?? '';
    });
  }

  @override
  Widget build(BuildContext context) {
    final mode = ref.watch(themeModeProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: ListView(children: [
        const SizedBox(height: 24),
        const CircleAvatar(radius: 40, child: Icon(Icons.person, size: 40)),
        const SizedBox(height: 8),
        Center(child: Text(_name,
            style: Theme.of(context).textTheme.titleLarge)),
        Center(child: Text(_email)),
        const Divider(height: 32),
        SwitchListTile(
          title: const Text('Dark mode'),
          secondary: const Icon(Icons.dark_mode_outlined),
          value: mode == ThemeMode.dark,
          onChanged: (on) => ref.read(themeModeProvider.notifier).state =
              on ? ThemeMode.dark : ThemeMode.light,
        ),
        const ListTile(
          leading: Icon(Icons.notifications_outlined),
          title: Text('Push notifications'),
          subtitle: Text('Job completions arrive as push notifications'),
        ),
      ]),
    );
  }
}
