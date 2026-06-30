#!/usr/bin/env python3.11
"""
Local Kokoro TTS server for Pebble's Spanish conversation mode.
Start it with:  /opt/homebrew/bin/python3.11 kokoro-tts-server.py
Then it serves the Dora voice at http://127.0.0.1:7070/tts?text=...
The Spanish app auto-uses it when running; if it's off, the app falls back to the device voice.
"""
import os, tempfile, subprocess, inspect
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

MODEL = os.path.expanduser('~/.cache/hyperframes/tts/models/kokoro-v1.0.onnx')
VOICES = os.path.expanduser('~/.cache/hyperframes/tts/voices/voices-v1.0.bin')
VOICE = 'ef_dora'
LANG = 'es'
PORT = 7070

print('Loading Kokoro (Dora)...')
import kokoro_onnx, soundfile as sf
model = kokoro_onnx.Kokoro(MODEL, VOICES)
SUPPORTS_LANG = 'lang' in inspect.signature(model.create).parameters
print('Ready. Serving Dora at http://127.0.0.1:%d/tts?text=...' % PORT)

def synth(text, speed):
    kw = {'voice': VOICE, 'speed': speed}
    if SUPPORTS_LANG:
        kw['lang'] = LANG
    samples, sr = model.create(text, **kw)
    d = tempfile.mkdtemp()
    wav, mp3 = d + '/a.wav', d + '/a.mp3'
    sf.write(wav, samples, sr)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-ac', '1', '-ar', '24000', '-b:a', '64k', mp3], check=True)
    return open(mp3, 'rb').read()

class H(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()
    def do_GET(self):
        u = urlparse(self.path)
        if u.path == '/health':
            self.send_response(200); self._cors(); self.send_header('Content-Type', 'text/plain'); self.end_headers()
            self.wfile.write(b'ok'); return
        if u.path != '/tts':
            self.send_response(404); self._cors(); self.end_headers(); return
        q = parse_qs(u.query)
        text = (q.get('text', [''])[0]).strip()
        try:
            speed = float(q.get('speed', ['0.95'])[0])
        except Exception:
            speed = 0.95
        if not text:
            self.send_response(400); self._cors(); self.end_headers(); return
        try:
            audio = synth(text[:600], speed)
            self.send_response(200)
            self.send_header('Content-Type', 'audio/mpeg')
            self.send_header('Cache-Control', 'no-store')
            self._cors()
            self.end_headers()
            self.wfile.write(audio)
        except Exception as e:
            print('synth error:', e)
            self.send_response(500); self._cors(); self.end_headers()
    def log_message(self, *a):
        pass

ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
