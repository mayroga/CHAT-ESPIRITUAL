CHAT ESPIRITUAL – Guía Virtual y Comunidad






Descripción

CHAT ESPIRITUAL es una aplicación web interactiva que permite a los usuarios comunicarse con un guía espiritual virtual, compartir intenciones con la comunidad y realizar donaciones para apoyar el proyecto. La app combina inteligencia artificial, texto a voz y pagos mediante Stripe, ofreciendo una experiencia profesional, inclusiva y segura, sin contenido ofensivo ni doctrinas específicas.

Características principales

Chat espiritual: Envía mensajes y recibe respuestas empáticas del guía virtual, con detección automática de idioma.

TTS (Texto a voz): Escucha las respuestas mediante gTTS; cache local para rapidez.

Comunidad de intenciones: Publica tus intenciones, ve las de otros y da “Amén” para mostrar apoyo.

Donaciones seguras: Integración con Stripe Checkout; las claves secretas se manejan únicamente en Render.

Moderación de contenido: Todos los mensajes y respuestas son revisados automáticamente.

Tecnologías

Backend: Flask, SQLAlchemy, PostgreSQL

IA: OpenAI GPT-4o

TTS: gTTS

Frontend: HTML, TailwindCSS, React (JSX)

Pagos: Stripe Checkout

Hosting: Render

Instalación y despliegue

Clonar el repositorio.

Configurar variables secretas en Render:

OPENAI_API_KEY

STRIPE_SECRET_KEY

STRIPE_PUBLISHABLE_KEY

STRIPE_WEBHOOK_SECRET

DATABASE_URL

SECRET_KEY

URL_SITE

Instalar dependencias:

pip install -r requirements.txt


Crear la base de datos:

python migrate_db.py


Desplegar en Render y abrir la URL asignada.

Uso

Ingresar al chat para recibir orientación espiritual.

Publicar intenciones y apoyar las de otros.

Realizar donaciones para mantener y mejorar el proyecto.

Notas

Todo el contenido generado es moderado automáticamente.

Optimizado para accesibilidad, privacidad y estabilidad en producción.
