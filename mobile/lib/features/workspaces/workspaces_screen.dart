import 'package:flutter/material.dart';
import '../../core/api/api_client.dart';
import '../../core/cache/cache_service.dart';
import '../../models/models.dart';

/// Team workspaces: list, create, and select the active workspace.
class WorkspacesScreen extends StatefulWidget {
  const WorkspacesScreen({super.key});
  @override
  State<WorkspacesScreen> createState() => _WorkspacesScreenState();
}

class _WorkspacesScreenState extends State<WorkspacesScreen> {
  List<Workspace> _workspaces = [];
  String? _active;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final resp = await ApiClient.instance.dio.get('/workspaces');
    if (!mounted) return;
    setState(() {
      _workspaces = (resp.data as List)
          .map((j) => Workspace.fromJson(j))
          .toList();
      _active = CacheService.get<String>('workspace_id') ??
          (_workspaces.isNotEmpty ? _workspaces.first.id : null);
    });
    if (_active != null) await CacheService.put('workspace_id', _active);
  }

  Future<void> _create() async {
    final controller = TextEditingController();
    final name = await showDialog<String>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('New workspace'),
        content: TextField(controller: controller,
            decoration: const InputDecoration(labelText: 'Name')),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel')),
          FilledButton(
              onPressed: () => Navigator.pop(context, controller.text),
              child: const Text('Create')),
        ],
      ),
    );
    if (name == null || name.isEmpty) return;
    await ApiClient.instance.dio
        .post('/workspaces', queryParameters: {'name': name});
    _load();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Team Workspaces')),
      floatingActionButton:
          FloatingActionButton(onPressed: _create, child: const Icon(Icons.add)),
      body: ListView(
        children: _workspaces
            .map((w) => RadioListTile<String>(
                  value: w.id,
                  groupValue: _active,
                  title: Text(w.name),
                  onChanged: (v) async {
                    setState(() => _active = v);
                    await CacheService.put('workspace_id', v);
                  },
                ))
            .toList(),
      ),
    );
  }
}
