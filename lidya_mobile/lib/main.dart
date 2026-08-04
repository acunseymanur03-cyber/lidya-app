import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const LidyaApp());
}

class LidyaApp extends StatelessWidget {
  const LidyaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Lidya - Canlı Sohbet',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0D1117),
        primaryColor: const Color(0xFF58A6FF),
      ),
      home: const NameScreen(),
    );
  }
}

// 1. İsim Giriş Ekranı
class NameScreen extends StatefulWidget {
  const NameScreen({super.key});

  @override
  State<NameScreen> createState() => _NameScreenState();
}

class _NameScreenState extends State<NameScreen> {
  final TextEditingController _nameController = TextEditingController();

  void _startChat() {
    if (_nameController.text.trim().isNotEmpty) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => ChatScreen(userName: _nameController.text.trim()),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: const Color(0xFF161B22),
              borderRadius: BorderRadius.circular(15),
              border: Border.all(color: const Color(0xFF30363D)),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  "🧠 Lidya - Laboratuvar",
                  style: TextStyle(
                    color: Color(0xFF58A6FF),
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 10),
                const Text(
                  "Zihnim aktif, bugün hangi fikir üzerinde çalışıyoruz?",
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Color(0xFF8B949E)),
                ),
                const SizedBox(height: 20),
                TextField(
                  controller: _nameController,
                  decoration: InputDecoration(
                    hintText: "Adını yaz...",
                    filled: true,
                    fillColor: const Color(0xFF0D1117),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10),
                      borderSide: const BorderSide(color: Color(0xFF30363D)),
                    ),
                  ),
                ),
                const SizedBox(height: 20),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF238636),
                      padding: const EdgeInsets.all(15),
                    ),
                    onPressed: _startChat,
                    child: const Text("Sohbete Başla 🚀", style: TextStyle(fontSize: 16, color: Colors.white)),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// 2. Sohbet Ekranı
class ChatScreen extends StatefulWidget {
  final String userName;
  const ChatScreen({super.key, required this.userName});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final List<Map<String, String>> _messages = [];
  bool _isLoading = false;

  // BURAYA GROQ API ANAHTARINI YAPIŞTIRACAKSIN
  final String _groqApiKey = "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";

  Future<void> _sendMessage() async {
    String text = _messageController.text.trim();
    if (text.isEmpty) return;

    setState(() {
      _messages.add({"role": "user", "content": text});
      _messageController.clear();
      _isLoading = true;
    });

    try {
      final response = await http.post(
        Uri.parse("https://api.groq.com/openai/v1/chat/completions"),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $_groqApiKey",
        },
        body: jsonEncode({
          "model": "llama-3.3-70b-versatile",
          "messages": [
            {
              "role": "system",
              "content": "Senin adın Lidya. Enerjik, bilim odaklı bir yapay zekasın. Kullanıcının adı: ${widget.userName}. Ona ismiyle hitap et, kısa ve samimi konuş."
            },
            ..._messages.map((m) => {"role": m["role"], "content": m["content"]})
          ]
        }),
      );

      if (response.statusCode == 200) {
        var data = jsonDecode(utf8.decode(response.bodyBytes));
        String botReply = data["choices"][0]["message"]["content"];
        setState(() {
          _messages.add({"role": "assistant", "content": botReply});
        });
      } else {
        setState(() {
          _messages.add({"role": "assistant", "content": "Bir hata oluştu: ${response.statusCode}"});
        });
      }
    } catch (e) {
      setState(() {
        _messages.add({"role": "assistant", "content": "Bağlantı hatası: $e"});
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Lidya - Merhaba ${widget.userName}"),
        backgroundColor: const Color(0xFF161B22),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(10),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                var msg = _messages[index];
                bool isUser = msg["role"] == "user";
                return Align(
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  Container(
                    margin: const EdgeInsets.symmetric(vertical: 5),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: isUser ? const Color(0xFF1f6feb) : const Color(0xFF21262d),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      msg["content"]!,
                      style: const TextStyle(color: Colors.white),
                    ),
                  ),
                );
              },
            ),
          ),
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(8.0),
              child: CircularProgressIndicator(color: Color(0xFF58A6FF)),
            ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    decoration: InputDecoration(
                      hintText: "Lidya'ya mesaj yaz...",
                      filled: true,
                      fillColor: const Color(0xFF161B22),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(color: Color(0xFF30363D)),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  icon: const Icon(Icons.send, color: Color(0xFF58A6FF)),
                  onPressed: _sendMessage,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}