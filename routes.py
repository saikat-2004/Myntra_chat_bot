import uuid
import traceback

from flask import Blueprint, render_template, request, jsonify
from app.config import Config
from app.models import log_conversation, search_products
from app.utils import classify_query

from groq import Groq

main = Blueprint('main', __name__)

# ── Lazy client ────────────────────────────────────────────────────────────────
_client = None

def get_client():
    global _client
    if _client is None:
        api_key = Config.GROQ_API_KEY
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. "
                "Get a free key at https://console.groq.com and add it to your .env file."
            )
        _client = Groq(api_key=api_key)
    return _client


SYSTEM_PROMPT = (
    "You are a friendly and knowledgeable lipstick and personal care "
    "shopping assistant for Myntra. Help users find the right products, "
    "compare options, and make confident purchase decisions. "
    "Keep answers concise, warm, and helpful."
)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"response": "Invalid request — expected JSON."}), 400

        user_message = (data.get('message') or '').strip()
        session_id   = data.get('session_id') or str(uuid.uuid4())

        if not user_message:
            return jsonify({"response": "Please type a message.", "session_id": session_id})

        query_type = classify_query(user_message)

        # ── Redirect sensitive queries to customer care ────────────────────────
        if query_type == "redirect":
            bot_response = (
                "For queries related to offers, returns, refunds, cancellations, "
                "or delivery issues, please contact Myntra Customer Care at "
                "<strong>+91-80-61561999</strong> or visit the Help Center on the Myntra website."
            )

        # ── Answer product / general queries via Groq ──────────────────────────
        else:
            # Build product context from DB (safe even if table is empty)
            context_lines = []
            try:
                products = search_products(user_message)
                for p in products[:5]:
                    context_lines.append(
                        f"- {p['brand']} {p['product_name']} "
                        f"| ₹{p['discounted_price']} | Rating: {p['rating']}"
                    )
            except Exception as db_err:
                print(f"[DB WARNING] search_products failed: {db_err}")

            if context_lines:
                context_block = "Relevant products from our catalogue:\n" + "\n".join(context_lines)
            else:
                context_block = "No specific products found in the catalogue for this query."

            response = get_client().chat.completions.create(
                model="llama-3.3-70b-versatile",   # free, fast, high quality
                messages=[
                    {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{context_block}"},
                    {"role": "user",   "content": user_message},
                ],
                temperature=0.7,
                max_tokens=1024,
            )
            bot_response = response.choices[0].message.content

        # ── Log to DB (non-fatal) ──────────────────────────────────────────────
        try:
            log_conversation(session_id, user_message, bot_response, query_type)
        except Exception as log_err:
            print(f"[DB WARNING] log_conversation failed: {log_err}")

        return jsonify({"response": bot_response, "session_id": session_id})

    except RuntimeError as e:
        print(f"[CONFIG ERROR] {e}")
        return jsonify({"response": f"Server configuration error: {e}"}), 500

    except Exception as e:
        print(f"[ERROR] /chat endpoint failed:\n{traceback.format_exc()}")
        return jsonify({"response": "Sorry, something went wrong. Please try again."}), 500