import 'dart:async';
import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/app_config.dart';

/// Central HTTP client: attaches JWT, refreshes on 401, exposes SSE streaming.
class ApiClient {
  ApiClient._();
  static final ApiClient instance = ApiClient._();

  static const _storage = FlutterSecureStorage();
  Future<bool>? _refreshing;

  late final Dio dio = Dio(BaseOptions(baseUrl: AppConfig.apiBaseUrl))
    ..interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _storage.read(key: 'access_token');
        if (token != null) options.headers['Authorization'] = 'Bearer $token';
        handler.next(options);
      },
      onError: (err, handler) async {
        if (err.response?.statusCode == 401 && await _refresh()) {
          try {
            final retry = await dio.fetch(err.requestOptions);
            return handler.resolve(retry);
          } catch (e) {
            return handler.next(err);
          }
        }
        handler.next(err);
      },
    ));

  Future<void> saveTokens(String access, String refresh) async {
    await _storage.write(key: 'access_token', value: access);
    await _storage.write(key: 'refresh_token', value: refresh);
  }

  /// Refreshes the access token. Concurrent callers share a single in-flight
  /// request instead of each firing their own refresh (which would race and
  /// overwrite each other's tokens).
  Future<bool> _refresh() {
    return _refreshing ??= _doRefresh().whenComplete(() => _refreshing = null);
  }

  Future<bool> _doRefresh() async {
    final refresh = await _storage.read(key: 'refresh_token');
    if (refresh == null) return false;
    try {
      final resp = await Dio(BaseOptions(baseUrl: AppConfig.apiBaseUrl))
          .post('/auth/refresh', queryParameters: {'refresh_token': refresh});
      final access = resp.data['access_token'];
      final newRefresh = resp.data['refresh_token'];
      if (access == null || newRefresh == null) return false;
      await saveTokens(access, newRefresh);
      return true;
    } catch (_) {
      return false;
    }
  }

  /// Stream Server-Sent-Event tokens from an LLM endpoint.
  Stream<String> sseStream(String path, Map<String, dynamic> body) async* {
    final token = await _storage.read(key: 'access_token');
    final resp = await dio.post<ResponseBody>(
      path,
      data: body,
      options: Options(
        responseType: ResponseType.stream,
        headers: {'Accept': 'text/event-stream', 'Authorization': 'Bearer $token'},
      ),
    );
    final responseBody = resp.data;
    if (responseBody == null) {
      throw DioException(
          requestOptions: resp.requestOptions,
          error: 'Empty response stream');
    }
    var buffer = '';
    await for (final chunk in responseBody.stream) {
      buffer += utf8.decode(chunk, allowMalformed: true);
      final events = buffer.split('\n\n');
      buffer = events.removeLast();
      for (final event in events) {
        String? name;
        final data = StringBuffer();
        for (final line in event.split('\n')) {
          if (line.startsWith('event:')) name = line.substring(6).trim();
          if (line.startsWith('data:')) data.write(line.substring(5).trimLeft());
        }
        if (name == 'done') return;
        if (name == 'token') yield data.toString();
      }
    }
  }
}
