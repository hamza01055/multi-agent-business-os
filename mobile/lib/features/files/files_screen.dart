import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import '../../core/api/api_client.dart';
import '../../core/cache/cache_service.dart';

/// Upload PDF/DOCX/PPTX for Document Chat, audio for Meeting Summarizer,
/// or invoices for OCR — then track processing status.
class FilesScreen extends StatefulWidget {
  const FilesScreen({super.key});
  @override
  State<FilesScreen> createState() => _FilesScreenState();
}

class _FilesScreenState extends State<FilesScreen> {
  final List<Map<String, String>> _uploads = [];

  Future<void> _pick(String endpoint, List<String> extensions, String label) async {
    final result = await FilePicker.platform
        .pickFiles(type: FileType.custom, allowedExtensions: extensions);
    if (result == null || result.files.single.path == null) return;
    final ws = CacheService.get<String>('workspace_id') ?? '';
    final form = FormData.fromMap({
      'workspace_id': ws,
      'file': await MultipartFile.fromFile(result.files.single.path!),
    });
    final resp = await ApiClient.instance.dio.post(endpoint, data: form);
    if (!mounted) return;
    setState(() => _uploads.insert(0, {
          'id': resp.data['id'],
          'name': result.files.single.name,
          'kind': label,
          'status': resp.data['status'] ?? 'PENDING',
          'endpoint': endpoint,
        }));
  }

  Future<void> _refresh(int index) async {
    final u = _uploads[index];
    final resp =
        await ApiClient.instance.dio.get('${u['endpoint']}/${u['id']}');
    if (!mounted) return;
    setState(() => _uploads[index]['status'] = resp.data['status']);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Files & Processing')),
      body: ListView(padding: const EdgeInsets.all(12), children: [
        Wrap(spacing: 8, runSpacing: 8, children: [
          FilledButton.icon(
              onPressed: () =>
                  _pick('/documents', ['pdf', 'docx', 'pptx'], 'Document'),
              icon: const Icon(Icons.description),
              label: const Text('Document chat')),
          FilledButton.tonalIcon(
              onPressed: () =>
                  _pick('/meetings', ['mp3', 'wav', 'm4a'], 'Meeting'),
              icon: const Icon(Icons.record_voice_over),
              label: const Text('Meeting audio')),
          FilledButton.tonalIcon(
              onPressed: () =>
                  _pick('/invoices', ['pdf', 'png', 'jpg'], 'Invoice'),
              icon: const Icon(Icons.receipt_long),
              label: const Text('Invoice OCR')),
        ]),
        const SizedBox(height: 16),
        if (_uploads.isEmpty)
          const Center(child: Padding(
            padding: EdgeInsets.all(32),
            child: Text('Upload a file to start processing.'),
          )),
        ..._uploads.asMap().entries.map((e) => Card(
              child: ListTile(
                leading: const Icon(Icons.insert_drive_file),
                title: Text(e.value['name']!),
                subtitle: Text('${e.value['kind']} · ${e.value['status']}'),
                trailing: IconButton(
                    icon: const Icon(Icons.refresh),
                    onPressed: () => _refresh(e.key)),
              ),
            )),
      ]),
    );
  }
}
