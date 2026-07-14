import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import '../../core/api/api_client.dart';
import '../chat/home_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _loading = false;
  bool _registerMode = false;
  String? _error;

  Future<void> _submit() async {
    setState(() { _loading = true; _error = null; });
    try {
      final api = ApiClient.instance;
      if (_registerMode) {
        await api.dio.post('/auth/register', data: {
          'email': _email.text.trim(),
          'password': _password.text,
          'full_name': _email.text.split('@').first,
        });
      }
      final resp = await api.dio.post('/auth/login',
          data: {'username': _email.text.trim(), 'password': _password.text},
          options: Options(contentType: Headers.formUrlEncodedContentType));
      await api.saveTokens(
          resp.data['access_token'], resp.data['refresh_token']);
      if (mounted) {
        Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (_) => const HomeScreen()));
      }
    } catch (e) {
      setState(() => _error = 'Sign in failed. Check your details and try again.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 380),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.hub, size: 56),
                const SizedBox(height: 8),
                Text('AI Business OS',
                    style: Theme.of(context).textTheme.headlineSmall),
                const SizedBox(height: 24),
                TextField(
                    controller: _email,
                    decoration: const InputDecoration(labelText: 'Email'),
                    keyboardType: TextInputType.emailAddress),
                TextField(
                    controller: _password,
                    decoration: const InputDecoration(labelText: 'Password'),
                    obscureText: true),
                const SizedBox(height: 16),
                if (_error != null)
                  Text(_error!, style: const TextStyle(color: Colors.red)),
                FilledButton(
                  onPressed: _loading ? null : _submit,
                  child: Text(_registerMode ? 'Create account' : 'Sign in'),
                ),
                TextButton(
                  onPressed: () =>
                      setState(() => _registerMode = !_registerMode),
                  child: Text(_registerMode
                      ? 'Have an account? Sign in'
                      : 'New here? Create account'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
