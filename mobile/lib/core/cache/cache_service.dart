import 'package:hive_flutter/hive_flutter.dart';

/// Offline cache: conversations and messages survive restarts and no-network.
class CacheService {
  static late Box _box;

  static Future<void> init() async {
    _box = await Hive.openBox('aibos_cache');
  }

  static Future<void> put(String key, dynamic value) => _box.put(key, value);
  static T? get<T>(String key) => _box.get(key) as T?;

  static Future<void> cacheMessages(String conversationId, List<Map> messages) =>
      _box.put('msgs:$conversationId', messages);

  static List<Map> cachedMessages(String conversationId) =>
      (_box.get('msgs:$conversationId') as List?)?.cast<Map>() ?? [];
}
