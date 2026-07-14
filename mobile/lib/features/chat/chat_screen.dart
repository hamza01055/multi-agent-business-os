import 'package:flutter/material.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../../core/api/api_client.dart';
import '../../core/cache/cache_service.dart';
import '../../models/models.dart';

/// AI chat with SSE token streaming and offline history cache.
class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});
  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _controller = TextEditingController();
  final _scroll = ScrollController();
  final List<ChatMessage> _messages = [];
  String? _conversationId;
  bool _sending = false;
  bool _offline = false;

  @override
  void initState() {
    super.initState();
    _restoreCache();
    Connectivity().onConnectivityChanged.listen((results) {
      setState(() => _offline = results.contains(ConnectivityResult.none));
    });
  }

  void _restoreCache() {
    final id = CacheService.get<String>('last_conversation');
    if (id != null) {
      _conversationId = id;
      _messages.addAll(
          CacheService.cachedMessages(id).map((m) => ChatMessage.fromJson(m)));
      setState(() {});
    }
  }

  Future<void> _ensureConversation() async {
    if (_conversationId != null) return;
    final ws = CacheService.get<String>('workspace_id');
    final resp = await ApiClient.instance.dio.post('/chat/conversations',
        data: {'workspace_id': ws, 'title': 'Mobile chat'});
    _conversationId = resp.data['id'];
    await CacheService.put('last_conversation', _conversationId);
  }

  Future<void> _send() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _sending) return;
    _controller.clear();
    setState(() {
      _sending = true;
      _messages.add(ChatMessage(role: 'user', content: text));
      _messages.add(ChatMessage(role: 'assistant', content: ''));
    });
    try {
      await _ensureConversation();
      final stream = ApiClient.instance.sseStream(
          '/chat/conversations/$_conversationId/messages',
          {'content': text, 'stream': true});
      await for (final token in stream) {
        if (!mounted) return;
        setState(() => _messages.last.content += token);
        if (_scroll.hasClients) {
          _scroll.jumpTo(_scroll.position.maxScrollExtent);
        }
      }
    } catch (_) {
      if (!mounted) return;
      setState(() => _messages.last.content =
          _offline ? 'You are offline. Message saved locally.' : 'Something went wrong. Try again.');
    } finally {
      if (mounted) setState(() => _sending = false);
      if (_conversationId != null) {
        CacheService.cacheMessages(
            _conversationId!, _messages.map((m) => m.toJson()).toList());
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Chat'),
        actions: [if (_offline) const Padding(
          padding: EdgeInsets.only(right: 16),
          child: Icon(Icons.cloud_off),
        )],
      ),
      body: Column(children: [
        Expanded(
          child: ListView.builder(
            controller: _scroll,
            padding: const EdgeInsets.all(12),
            itemCount: _messages.length,
            itemBuilder: (_, i) {
              final m = _messages[i];
              final isUser = m.role == 'user';
              return Align(
                alignment:
                    isUser ? Alignment.centerRight : Alignment.centerLeft,
                child: Container(
                  margin: const EdgeInsets.symmetric(vertical: 4),
                  padding: const EdgeInsets.all(12),
                  constraints: const BoxConstraints(maxWidth: 320),
                  decoration: BoxDecoration(
                    color: isUser
                        ? Theme.of(context).colorScheme.primaryContainer
                        : Theme.of(context).colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: isUser
                      ? Text(m.content)
                      : MarkdownBody(data: m.content.isEmpty ? '…' : m.content),
                ),
              );
            },
          ),
        ),
        SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(12, 0, 12, 8),
            child: Row(children: [
              Expanded(
                child: TextField(
                  controller: _controller,
                  decoration:
                      const InputDecoration(hintText: 'Ask anything…'),
                  onSubmitted: (_) => _send(),
                ),
              ),
              IconButton.filled(
                onPressed: _sending ? null : _send,
                icon: const Icon(Icons.arrow_upward),
              ),
            ]),
          ),
        ),
      ]),
    );
  }
}
