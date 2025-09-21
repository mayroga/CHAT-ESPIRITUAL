import os, hashlib, base64
from gtts import gTTS
import openai
from langdetect import detect

openai.api_key = os.environ.get("OPENAI_API_KEY")  # secreto en Render

TTS_CACHE_DIR = "/tmp/tts_cache"
os.makedirs(TTS_CACHE_DIR, exist_ok=True)

SYSTEM_PROMPT = (
    "Eres un guía espiritual universal cuyo objetivo es ofrecer consuelo, esperanza y orientación "
    "con lenguaje inclusivo, neutral y sin doctrinas específicas. Responde con empatía y respeto. "
    "Si detectas señales de riesgo, di un mensaje de apoyo y sugiere buscar ayuda profesional y recursos locales."
)

def detect_lang(text):
    try:
        return detect(text)[:2]
    except:
        return "es"

def check_moderation(text):
    try:
        resp = openai.Moderation.create(input=text)
        results = resp["results"][0]
        return {"flagged": results.get("flagged", False), "raw": results}
    except Exception as e:
        print("Moderation error:", e)
        return {"flagged": False, "error": str(e)}

def generate_reply(user_text, language="es"):
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role":"system", "content": SYSTEM_PROMPT},
                {"role":"user", "content": user_text}
            ],
            max_tokens=300, temperature=0.8
        )
        text = resp.choices[0].message.get("content","").strip()
        return text
    except Exception as e:
        print("OpenAI error:", e)
        return "Lo siento, no puedo conectar con el guía espiritual ahora."

def tts_cache_base64(text, lang="es"):
    key = hashlib.sha256((text + "|" + lang).encode("utf-8")).hexdigest()
    filename = os.path.join(TTS_CACHE_DIR, f"{key}.mp3")
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(filename)
        with open(filename, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print("TTS error:", e)
        return ""
