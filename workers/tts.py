import os
from gtts import gTTS

def generate_audio(script_text, output_path):
    print("🎙 GENERATING REAL AUDIO:", output_path)
    # create audio using gTTS
    tts = gTTS(text=script_text, lang='en')
    tts.save(output_path)
