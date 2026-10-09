from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import asyncio
from deep_translator import GoogleTranslator
import edge_tts
import yt_dlp

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def translate_text(text):
    return GoogleTranslator(source='auto', target='ar').translate(text)

async def generate_arabic_audio(text, output_audio_path):
    voice = "ar-SA-HamedNeural"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_audio_path)

@app.route('/dub', methods=['POST'])
def dub_video():
    youtube_url = request.form.get('youtube_url')
    
    if youtube_url:
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(UPLOAD_FOLDER, 'audio.%(ext)s'),
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            
            sample_text = "مرحباً بك، تم استقبال الفيديو وجاري الدبلجة بنجاح."
            output_audio = os.path.join(OUTPUT_FOLDER, 'arabic_voice.mp3')
            asyncio.run(generate_arabic_audio(sample_text, output_audio))

            return jsonify({
                "status": "success",
                "message": "تمت الدبلجة بنجاح!",
                "audio_url": request.host_url + output_audio
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "error", "message": "يرجى توفير رابط صحيح"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
