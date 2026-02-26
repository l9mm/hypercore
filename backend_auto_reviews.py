"""
Flask Backend Server with Automatic Review Generation
Generates reviews every 2-9 hours using Gemini AI + Firebase
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
import json
import random
import threading
import time
import requests

# Import product and name databases
from products_database import PRODUCTS
from names_database import CUSTOMER_NAMES

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ============================================
# CONFIGURATION
# ============================================

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

print(f"[STARTUP] GEMINI_API_KEY present: {bool(GEMINI_API_KEY)}")
print(f"[STARTUP] GEMINI_API_KEY length: {len(GEMINI_API_KEY)}")

# ============================================
# FIREBASE INIT
# ============================================

print("[STARTUP] Initializing Firebase...")
try:
    cred = credentials.Certificate('firebase-credentials.json')
    firebase_admin.initialize_app(cred)
    print("[STARTUP] Firebase initialized from local credentials file")
except Exception as e:
    print(f"[STARTUP] Local credentials failed: {e}")
    firebase_creds = os.environ.get('FIREBASE_CREDENTIALS')
    if firebase_creds:
        print("[STARTUP] Trying FIREBASE_CREDENTIALS env var...")
        try:
            cred_dict = json.loads(firebase_creds)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("[STARTUP] Firebase initialized from env var")
        except Exception as e2:
            print(f"[STARTUP] CRITICAL: Firebase env var also failed: {e2}")
            raise
    else:
        print("[STARTUP] CRITICAL: No Firebase credentials found anywhere")
        raise RuntimeError("No Firebase credentials available")

try:
    db = firestore.client()
    print("[STARTUP] Firestore client created successfully")
except Exception as e:
    print(f"[STARTUP] CRITICAL: Firestore client failed: {e}")
    raise

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_random_name():
    return random.choice(CUSTOMER_NAMES)

def call_gemini(prompt):
    """Call Gemini via plain REST - no gRPC, no SDK crashes"""
    print("[GEMINI] Sending request to Gemini 1.5 Flash...")
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 200,
            "temperature": 0.9
        }
    }
    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=30)
        print(f"[GEMINI] Response status: {response.status_code}")

        if response.status_code == 429:
            print("[GEMINI] Rate limit hit (429) - will use fallback")
            return None
        if response.status_code == 400:
            print(f"[GEMINI] Bad request (400): {response.text}")
            return None
        if response.status_code != 200:
            print(f"[GEMINI] Unexpected status {response.status_code}: {response.text}")
            return None

        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        print(f"[GEMINI] Success, review length: {len(text)} chars")
        return text

    except requests.exceptions.Timeout:
        print("[GEMINI] Request timed out after 30s")
        return None
    except Exception as e:
        print(f"[GEMINI] Exception during request: {e}")
        return None

def generate_review_with_gemini(product_name, product_price, currency, rating, user_name):
    if "RTX" in product_name or "Radeon" in product_name or "GeForce" in product_name:
        product_type = "graphics card"
    elif "Ryzen" in product_name or "Core i" in product_name:
        product_type = "processor"
    elif "SSD" in product_name or "NVMe" in product_name or "PCIe" in product_name:
        product_type = "SSD"
    elif "Monitor" in product_name or '"' in product_name or "OLED" in product_name:
        product_type = "monitor"
    elif "DDR" in product_name or "RAM" in product_name:
        product_type = "RAM"
    else:
        product_type = "component"

    tone_map = {
        5: ("very satisfied and enthusiastic", ["Use casual language like 'honestly', 'runs great'", "Mention specific games that work well", "Talk about exceeding expectations", "Mention upgrading from older hardware"]),
        4: ("satisfied but with minor concerns", ["Mention one small issue but overall positive", "Say it's good for the price", "Compare to similar products briefly", "Mention it does what's needed"]),
        3: ("neutral, it's okay but not amazing", ["Say it works but nothing special", "Mention it's average for the price", "Note some disappointments", "Say it gets the job done"]),
        2: ("disappointed", ["Mention specific problems", "Say it didn't meet expectations", "Compare unfavorably to alternatives", "Note quality issues"]),
        1: ("very dissatisfied", ["Describe major issues or failures", "Express frustration with quality", "Warn others to avoid", "Mention considering returning"])
    }
    tone, styles = tone_map[rating]
    style = random.choice(styles)

    prompt = f"""Write a short, casual customer review for a PC {product_type}.

RULES:
- DO NOT mention the product name or brand
- Write like a real person texting, NOT a formal review
- Use casual language: "pretty good", "works fine", "no complaints"
- Be brief: 40-100 words MAX
- Sound natural and conversational

Context:
- Product type: {product_type}
- Price: {currency}{product_price}
- Rating: {rating}/5 stars
- Tone: {tone}
- Style hint: {style}

Write one casual review (40-100 words):"""

    review = call_gemini(prompt)

    if review is None:
        print("[GEMINI] Using fallback review")
        fallbacks = [
            "works great, no complaints. been using it for a few weeks and its solid for the price",
            "pretty happy with this purchase. does what i need and runs smooth",
            f"good value for {currency}{product_price}. would recommend",
            "been running fine since i got it. no issues so far",
            "honestly works better than expected. happy with it"
        ]
        return random.choice(fallbacks)

    # Clean up response
    review = review.replace(product_name, "it")
    if review.startswith('"') and review.endswith('"'):
        review = review[1:-1]

    return review

def save_review_to_firebase(review_data):
    print("[FIREBASE] Saving review...")
    try:
        doc_ref = db.collection('reviews').document()
        doc_ref.set(review_data)
        print(f"[FIREBASE] Saved with ID: {doc_ref.id}")
        return doc_ref.id
    except Exception as e:
        print(f"[FIREBASE] Save failed: {e}")
        return None

def get_reviews_from_firebase():
    print("[FIREBASE] Fetching reviews...")
    try:
        reviews_ref = db.collection('reviews').order_by('date', direction=firestore.Query.DESCENDING)
        reviews = reviews_ref.stream()
        review_list = []
        for review in reviews:
            review_data = review.to_dict()
            review_data['id'] = review.id
            review_list.append(review_data)
        print(f"[FIREBASE] Fetched {len(review_list)} reviews")
        return review_list
    except Exception as e:
        print(f"[FIREBASE] Fetch failed: {e}")
        return []

def generate_auto_review():
    print("[SCHEDULER] Starting review generation...")
    try:
        product = random.choice(PRODUCTS)
        print(f"[SCHEDULER] Selected product: {product['name']}")

        use_usd = random.random() < 0.68
        currency = "$" if use_usd else "€"
        price = product['priceUSD'] if use_usd else product['priceEUR']

        rating = random.choices([1, 2, 3, 4, 5], weights=[2, 3, 8, 22, 65])[0]
        user_name = get_random_name()
        print(f"[SCHEDULER] Rating: {rating}, User: {user_name}, Currency: {currency}{price}")

        review_text = generate_review_with_gemini(product['name'], price, currency, rating, user_name)

        review_data = {
            'userName': user_name,
            'productName': product['name'],
            'productCategory': product['category'],
            'price': price,
            'currency': currency,
            'rating': rating,
            'review': review_text,
            'date': datetime.now().isoformat(),
            'timestamp': firestore.SERVER_TIMESTAMP,
            'auto_generated': True
        }

        review_id = save_review_to_firebase(review_data)

        if review_id:
            print(f"[SCHEDULER] Done: {user_name} reviewed {product['name']} ({rating} stars)")
            return review_data
        else:
            print("[SCHEDULER] Failed: could not save to Firebase")
            return None

    except Exception as e:
        print(f"[SCHEDULER] Exception in generate_auto_review: {e}")
        return None

def auto_review_scheduler():
    print("[SCHEDULER] Thread started, waiting 2 minutes before first review...")
    time.sleep(120)  # give the server time to fully start

    while True:
        try:
            print("[SCHEDULER] Triggering auto review generation...")
            generate_auto_review()
            hours = random.uniform(19, 36)  # Generate review every 19-36 hours
            print(f"[SCHEDULER] Next review in {hours:.1f} hours")
            time.sleep(hours * 3600)
        except Exception as e:
            print(f"[SCHEDULER] Outer exception: {e}")
            print("[SCHEDULER] Waiting 1 hour before retry...")
            time.sleep(3600)

# ============================================
# API ROUTES
# ============================================

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    print("[API] GET /api/reviews called")
    try:
        reviews = get_reviews_from_firebase()
        return jsonify({'success': True, 'reviews': reviews, 'count': len(reviews)})
    except Exception as e:
        print(f"[API] /api/reviews error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reviews/generate', methods=['POST'])
def manual_generate_review():
    print("[API] POST /api/reviews/generate called")
    try:
        review = generate_auto_review()
        if review:
            return jsonify({'success': True, 'message': 'Review generated successfully', 'review': review}), 201
        else:
            return jsonify({'success': False, 'error': 'Failed to generate review'}), 500
    except Exception as e:
        print(f"[API] /api/reviews/generate error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test():
    print("[API] GET /api/test called")
    return jsonify({
        'success': True,
        'message': 'Backend running!',
        'gemini_configured': bool(GEMINI_API_KEY),
        'gemini_key_length': len(GEMINI_API_KEY),
        'firebase_initialized': firebase_admin._apps != {},
        'products_loaded': len(PRODUCTS)
    })

@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({'success': True, 'message': 'pong', 'timestamp': datetime.now().isoformat()})

# ============================================
# STARTUP
# ============================================

print("[STARTUP] Starting scheduler thread...")
scheduler_thread = threading.Thread(target=auto_review_scheduler, daemon=True)
scheduler_thread.start()
print("[STARTUP] Scheduler thread started")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[STARTUP] Server starting on port {port}")
    print(f"[STARTUP] Products loaded: {len(PRODUCTS)}")
    app.run(host='0.0.0.0', port=port, debug=False)