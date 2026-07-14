class Workspace {
  final String id;
  final String name;
  Workspace({required this.id, required this.name});
  factory Workspace.fromJson(Map<String, dynamic> j) =>
      Workspace(id: j['id'], name: j['name']);
}

class ChatMessage {
  final String role; // user | assistant
  String content;
  ChatMessage({required this.role, required this.content});
  Map<String, dynamic> toJson() => {'role': role, 'content': content};
  factory ChatMessage.fromJson(Map j) =>
      ChatMessage(role: j['role'], content: j['content']);
}
