# AI Business OS — Flutter App

Features: AI chat (SSE streaming), voice assistant (STT→LLM→TTS), file upload
(documents / meetings / invoices), team workspaces, push notifications,
offline cache (Hive), dark mode, user profile.

## Run
```bash
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8080/api/v1   # Android emulator
```

## Structure
```
lib/
├── main.dart
├── core/
│   ├── api/api_client.dart      Dio + JWT refresh + SSE streaming
│   ├── cache/cache_service.dart Hive offline cache
│   ├── config/app_config.dart   --dart-define config
│   └── theme/app_theme.dart     Material 3, dark mode provider
├── models/models.dart
└── features/
    ├── auth/          login & register
    ├── chat/          home shell + streaming chat
    ├── voice/         speech_to_text + flutter_tts assistant
    ├── files/         upload → document chat / meetings / invoices
    ├── workspaces/    team workspace switcher
    ├── profile/       account + dark mode
    └── notifications/ FCM registration
```

Push requires adding your Firebase config (google-services.json /
GoogleService-Info.plist); the app degrades gracefully without it.
