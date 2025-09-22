import os
import stripe
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from gtts import gTTS
import base64
from io import BytesIO
from .models import db, Message, Intention

# Configuración de Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
SITE_URL = os.environ.get("URL_SITE", "https://chat-espiritual.onrender.com")

# Configuración de OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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

    # Base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.environ.get('SECRET_KEY', 'dev')

    CORS(app, origins=[SITE_URL, "https://checkout.stripe.com"])
    db.init_app(app)

    # ✅ Crear tablas si no existen
    with app.app_context():
        db.create_all()

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/chat", methods=["POST"])
    def chat():
        data = request.json or {}
        user_msg = (data.get("message") or "").strip()
        if not user_msg:
            return jsonify({"reply": "Por favor escribe algo.", "audio": ""}), 400

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres el Embajador de la Unidad Espiritual, un guía inclusivo y universal que promueve paz, amor y respeto sin imponer religión."},
                    {"role": "user", "content": user_msg}
                ]
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = "No se pudo conectar con el servidor espiritual en este momento."

        audio_b64 = tts_cache_base64(reply, "es")

        try:
            msg = Message(text=user_msg, reply=reply, language="es")
            db.session.add(msg)
            db.session.commit()
        except Exception as e:
            print("DB error:", e)

        return jsonify({"reply": reply, "audio": audio_b64})

    @app.route("/intention", methods=["POST"])
    def add_intention():
        data = request.json or {}
        text = (data.get("text") or "").strip()
        if not text:
            return jsonify({"error": "Texto vacío"}), 400

        it = Intention(text=text)
        db.session.add(it)
        db.session.commit()
        return jsonify({"ok": True, "id": it.id}), 201

    @app.route("/intentions", methods=["GET"])
    def get_intentions():
        items = Intention.query.order_by(Intention.created_at.desc()).limit(100).all()
        return jsonify([{"id": i.id, "text": i.text, "amen_count": i.amen_count} for i in items]), 200

    @app.route("/intention/<int:int_id>/amen", methods=["POST"])
    def amen(int_id):
        it = Intention.query.get_or_404(int_id)
        it.amen_count += 1
        db.session.commit()
        return jsonify({"ok": True, "amen_count": it.amen_count})

    @app.route("/create-donation-session", methods=["POST"])
    def create_donation_session():
        data = request.json or {}
        amount = int(data.get("amount", 5))
        if amount < 5:
            amount = 5
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                mode="payment",
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": "Donación Embajador de la Unidad Espiritual"},
                        "unit_amount": amount * 100
                    },
                    "quantity": 1
                }],
                success_url=f"{SITE_URL}?success=true",
                cancel_url=f"{SITE_URL}?canceled=true"
            )
            return jsonify({"url": session.url})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
