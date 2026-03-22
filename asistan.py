from piper_tts import PiperTTS

class YusufAsistan:
    """Yusuf Sesli Asistan"""
    
    def __init__(self):
        self.tts = PiperTTS()
        self.name = "Yusuf"
    
    def greet(self):
        """Selamla"""
        messages = [
            f"Merhaba ben {self.name}",
            "Hoş geldiniz",
            "Size nasıl yardımcı olabilirim?"
        ]
        for msg in messages:
            self.tts.speak(msg)

if __name__ == "__main__":
    asistan = YusufAsistan()
    asistan.greet()
