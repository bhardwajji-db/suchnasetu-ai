"""
Text-to-Speech (TTS) and Accessibility Read-Aloud Engine for SuchnaSetu AI.
Provides audio read-aloud in English and Hindi for vision-impaired and accessibility users.
Supports both gTTS audio generation and browser-native Web Speech API.
"""

from __future__ import annotations

import io
from typing import Optional
from gtts import gTTS


def generate_audio_bytes(text: str, lang: str = "en") -> Optional[bytes]:
    """
    Generates MP3 audio bytes using gTTS.
    lang: 'en' for English, 'hi' for Hindi.
    Returns bytes or None if offline/error.
    """
    if not text or not text.strip():
        return None

    try:
        clean_text = text.replace("#", "").replace("*", "").replace("`", "")[:2000]
        tts = gTTS(text=clean_text, lang=lang, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception:
        # If gTTS fails (e.g. offline mode), return None so UI can use Web Speech API fallback
        return None


def get_web_speech_js(text: str, lang_code: str = "en-US") -> str:
    """
    Returns an HTML/JavaScript snippet that uses the browser's built-in
    Web Speech Synthesis API for instant, offline-capable read-aloud.
    """
    safe_text = text.replace("`", "'").replace('"', '\\"').replace("\n", " ")[:1500]
    return f"""
    <div style="margin-top: 10px;">
        <button onclick="speakText()" style="
            background-color: #2563eb;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        ">
            🔊 Listen to Summary (Read Aloud)
        </button>
        <button onclick="window.speechSynthesis.cancel()" style="
            background-color: #475569;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            margin-left: 8px;
        ">
            ⏹ Stop
        </button>
        <script>
            function speakText() {{
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance("{safe_text}");
                msg.lang = "{lang_code}";
                msg.rate = 0.95;
                window.speechSynthesis.speak(msg);
            }}
        </script>
    </div>
    """
