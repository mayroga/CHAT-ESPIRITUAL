import os
import base64
from io import BytesIO
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from gtts import gTTS
import openai
import stripe
from .models import db, Message, Intention

# Configuración de Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
SITE_URL = os.environ.get("URL_SITE", "https://chat-espiritual.onrender.com")

# Configuración de OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")


def tts_cache_base64(text, lang="es"):
    try:
        tts = gTTS(text=text, lang=lang)
        buf = BytesIO()
        tts.write_to_fp(buf)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception:
        return ""


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.environ.get('SECRET_KEY', 'dev')

    # CORS
    CORS(app, origins=[SITE_URL, "https://checkout.stripe.com"])

    # Inicializar DB
    db.init_app(app)

    @app.route("/")
    def home():
        return render_template(
            "index.html",
            stripe_pub_key=STRIPE_PUBLISHABLE_KEY,
            site_url=SITE_URL,
            app_name="Embajador de la Unidad Espiritual"
        )

    @app.route("/chat", methods=["POST"])
    def chat():
        data = request.json or {}
        user_msg = (data.get("message") or "").strip()
        user_id = data.get("user_id")

        if not user_msg:
            return jsonify({"reply": "Escribe algo, por favor.", "audio": ""}), 400

        # Detectar idioma y moderación
        lang = "es"  # Siempre español para simplificar, puedes usar detect_lang(user_msg) si quieres
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres el Embajador de la Unidad Espiritual, un guía inclusivo y universal que promueve paz, amor y respeto sin imponer religión."},
                    {"role": "user", "content": user_msg}
                ]
            )
            reply = response.choices[0].message['content']
        except Exception:
            reply = "No se pudo conectar con el servidor espiritual en este momento."

        # Generar audio
        audio_b64 = tts_cache_base64(reply, lang)

        # Guardar en DB
        try:
            msg = Message(user_id=user_id, text=user_msg, reply=reply, language=lang)
            db.session.add(msg)
            db.session.commit()
        except Exception as e:
            print("DB error:", e)

        return jsonify({"reply": reply, "audio": audio_b64}), 200

    @app.route("/intention", methods=["POST"])
    def add_intention():
        data = request.json or {}
        text = (data.get("text") or "").strip()
        user_id = data.get("user_id")

        if not text:
            return jsonify({"error": "Texto vacío"}), 400

        it = Intention(user_id=user_id, text=text)
        db.session.add(it)
        db.session.commit()
        return jsonify({"ok": True, "id": it.id}), 201

    @app.route("/donate", methods=["POST"])
    def create_donation_session():
        data = request.json or {}
        amount = int(data.get("amount", 5))
        if amount < 5:
            amount = 5  # mínimo $5
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": "Donación Embajador de la Unidad Espiritual"},
                        "unit_amount": amount * 100
                    },
                    "quantity": 1
                }],
                mode="payment",
                success_url=f"{SITE_URL}?success=true",
                cancel_url=f"{SITE_URL}?canceled=true"
            )
            return jsonify({"url": session.url})
        except Exception as e:
            print("Stripe error:", e)
            return jsonify({"error": "No se pudo crear la sesión de pago"}), 500

    return app
