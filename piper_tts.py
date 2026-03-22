import subprocess
import os
from threading import Thread
import time

class PiperTTS:
    """Piper TTS - Türkçe Ses Sentezi (Offline)"""
    
    def __init__(self):
        self.model_path = os.path.expanduser("~/.local/share/piper/voices/tr_TR-dfki-medium/tr_TR-dfki-medium.onnx")
        self.output_file = "piper_output.wav"
        self.player = "aplay"
        
    def speak(self, text, async_mode=False):
        """Piper ile konuştur"""
        def _run():
            try:
                text_clean = text.replace('"', '\\"').replace('\n', ' ')
                cmd = f'echo "{text_clean}" | piper --model {self.model_path} --output-file {self.output_file}'
                
                print(f"[🎤] Konuşuluyor: {text[:50]}...")
                result = os.system(cmd)
                
                if result == 0:
                    os.system(f"{self.player} {self.output_file} 2>/dev/null")
                    print(f"[✅] Tamamlandı!")
                else:
                    print(f"[❌] Hata: {result}")
                    
            except Exception as e:
                print(f"[❌] Piper Hatası: {e}")
        
        if async_mode:
            Thread(target=_run, daemon=True).start()
        else:
            _run()
