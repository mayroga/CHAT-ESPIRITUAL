import os
import openai
from gtts import gTTS
from io import BytesIO
import base64
from langdetect import detect

# La clave API de OpenAI se carga desde las variables de entorno de Render.
openai.api_key = os.environ.get("OPENAI_API_KEY")

def detect_lang(text):
    try:
        return detect(text)
    except:
        return "es"

def check_moderation(text):
    try:
        response = openai.moderations.create(input=text)
        return response.results[0]
    except Exception as e:
        print(f"Error en moderación: {e}")
        return {"flagged": False}

def generate_reply(text, language="es"):
    try:
        messages = [
            {"role": "system", "content": "Eres un ser espiritual y sabio. Respondes con mensajes de paz, esperanza y sabiduría, como si fueras una entidad divina. Mantén un tono compasivo y reflexivo."},
            {"role": "user", "content": text}
        ]
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error al generar respuesta: {e}")
        return "Disculpa, no puedo responder en este momento. Por favor, inténtalo de nuevo más tarde."

def tts_cache_base64(text, language="es"):
    try:
        mp3_fp = BytesIO()
        tts = gTTS(text=text, lang=language)
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return base64.b64encode(mp3_fp.read()).decode('utf-8')
    except Exception as e:
        print(f"Error en TTS: {e}")
        return ""
