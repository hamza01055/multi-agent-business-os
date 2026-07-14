import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:flutter_tts/flutter_tts.dart';
import '../../core/api/api_client.dart';
import '../../core/cache/cache_service.dart';

/// Voice assistant: speech-to-text → AI chat → text-to-speech reply.
class VoiceScreen extends StatefulWidget {
  const VoiceScreen({super.key});
  @override
  State<VoiceScreen> createState() => _VoiceScreenState();
}

class _VoiceScreenState extends State<VoiceScreen> {
  final _speech = SpeechToText();
  final _tts = FlutterTts();
  bool _listening = false;
  String _heard = '';
  String _answer = '';

  Future<void> _toggle() async {
    if (_listening) {
      await _speech.stop();
      setState(() => _listening = false);
      if (_heard.isNotEmpty) await _ask(_heard);
      return;
    }
    final available = await _speech.initialize();
    if (!available) return;
    setState(() { _listening = true; _heard = ''; _answer = ''; });
    _speech.listen(onResult: (r) => setState(() => _heard = r.recognizedWords));
  }

  Future<void> _ask(String question) async {
    final ws = CacheService.get<String>('workspace_id');
    final conv = await ApiClient.instance.dio.post('/chat/conversations',
        data: {'workspace_id': ws, 'title': 'Voice', 'kind': 'chat'});
    final stream = ApiClient.instance.sseStream(
        '/chat/conversations/${conv.data['id']}/messages',
        {'content': question, 'stream': true});
    await for (final token in stream) {
      if (!mounted) return;
      setState(() => _answer += token);
    }
    if (!mounted) return;
    await _tts.speak(_answer);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Voice Assistant')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(children: [
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  if (_heard.isNotEmpty)
                    Card(child: ListTile(
                        leading: const Icon(Icons.person),
                        title: Text(_heard))),
                  if (_answer.isNotEmpty)
                    Card(child: ListTile(
                        leading: const Icon(Icons.smart_toy),
                        title: Text(_answer))),
                ],
              ),
            ),
          ),
          GestureDetector(
            onTap: _toggle,
            child: CircleAvatar(
              radius: 44,
              backgroundColor: _listening
                  ? Colors.red
                  : Theme.of(context).colorScheme.primary,
              child: Icon(_listening ? Icons.stop : Icons.mic,
                  size: 40, color: Colors.white),
            ),
          ),
          const SizedBox(height: 12),
          Text(_listening ? 'Listening… tap to send' : 'Tap to speak'),
        ]),
      ),
    );
  }
}
