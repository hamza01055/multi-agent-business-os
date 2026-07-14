import 'package:flutter/material.dart';
import '../chat/chat_screen.dart';
import '../voice/voice_screen.dart';
import '../files/files_screen.dart';
import '../workspaces/workspaces_screen.dart';
import '../profile/profile_screen.dart';

/// Bottom-nav shell: Chat · Voice · Files · Workspaces · Profile
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _index = 0;
  static const _screens = [
    ChatScreen(),
    VoiceScreen(),
    FilesScreen(),
    WorkspacesScreen(),
    ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.chat_bubble_outline), label: 'Chat'),
          NavigationDestination(icon: Icon(Icons.mic_none), label: 'Voice'),
          NavigationDestination(icon: Icon(Icons.upload_file), label: 'Files'),
          NavigationDestination(icon: Icon(Icons.groups_outlined), label: 'Teams'),
          NavigationDestination(icon: Icon(Icons.person_outline), label: 'Profile'),
        ],
      ),
    );
  }
}
