import os
import stripe
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from .models import db, Message, Intention, User
from .ai_utils import detect_lang, check_moderation, generate_reply, tts_cache_base64

# Configuración de Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = "pk_live_51NqPxQBOA5mT4t0PEoRVRc0Sj7DugiHvxhozC3BYh0q0hAx1N3HCLJe4xEp3MSuNMA6mQ7fAO4mvtppqLodrtqEn00pgJNQaxz"
SITE_URL = os.environ.get("URL_SITE", "https://chat-espiritual.onrender.com")

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
        return render_template("index.html", stripe_pub_key=STRIPE_PUBLISHABLE_KEY, site_url=SITE_URL)

    @app.route("/chat", methods=["POST"])
    def chat():
        data = request.json or {}
        user_msg = (data.get("message") or "").strip()
        user_id = data.get("user_id")

        if not user_msg:
            return jsonify({"reply": "Escribe algo, por favor.", "audio": ""}), 400

        lang = detect_lang(user_msg)
        mod = check_moderation(user_msg)
        if mod.get("flagged"):
            return jsonify({"reply": "Tu mensaje requiere revisión. Si estás en riesgo, busca ayuda local.", "audio": ""}), 200

        reply = generate_reply(user_msg, language=lang)
        if check_moderation(reply).get("flagged"):
            reply = "Se generó un contenido que requiere revisión. Intenta reformular tu mensaje."

        audio_b64 = tts_cache_base64(reply, lang)

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
        text = data.get("text", "").strip()
        user_id = data.get("user_id")

        if not text:
            return jsonify({"error": "Texto vacío"}), 400
        if check_moderation(text).get("flagged"):
            return jsonify({"error": "Contenido no permitido"}), 400

        it = Intention(user_id=user_id, text=text)
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
                        "product_data": {"name": "Donación Chat Espiritual"},
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
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
