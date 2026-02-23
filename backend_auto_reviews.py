"""
Flask Backend Server with Automatic Review Generation
Generates reviews every 2-9 hours using Gemini AI + Firebase
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
import os
import json
import random
import threading
import time

# Import product and name databases
from products_database import PRODUCTS
from names_database import CUSTOMER_NAMES

app = Flask(__name__)
CORS(app)

# ============================================
# CONFIGURATION
# ============================================

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY_HERE')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Initialize Firebase
try:
    cred = credentials.Certificate('firebase-credentials.json')
    firebase_admin.initialize_app(cred)
except:
    firebase_creds = os.environ.get('FIREBASE_CREDENTIALS')
    if firebase_creds:
        cred_dict = json.loads(firebase_creds)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_random_name():
    """Get a random name from database (no Gemini needed)"""
    return random.choice(CUSTOMER_NAMES)

def generate_review_with_gemini(product_name, product_price, currency, rating, user_name):
    """Generate realistic, casual review using Gemini"""
    
    # Determine product category from name
    category = "product"
    if "RTX" in product_name or "Radeon" in product_name or "GeForce" in product_name:
        category = "GPU"
        product_type = "graphics card"
    elif "Ryzen" in product_name or "Core i" in product_name:
        category = "CPU"
        product_type = "processor"
    elif "SSD" in product_name or "NVMe" in product_name or "PCIe" in product_name:
        category = "SSD"
        product_type = "SSD"
    elif "Monitor" in product_name or '"' in product_name or "OLED" in product_name:
        category = "Monitor"
        product_type = "monitor"
    elif "DDR" in product_name or "RAM" in product_name:
        category = "RAM"
        product_type = "RAM"
    else:
        product_type = "component"
    
    # Create different prompt styles based on rating
    if rating == 5:
        tone = "very satisfied and enthusiastic"
        style = random.choice([
            "Use casual language like 'honestly', 'pretty much', 'no issues', 'runs great'",
            "Mention specific games or software that work well",
            "Talk about how it exceeded expectations",
            "Mention upgrading from older hardware"
        ])
    elif rating == 4:
        tone = "satisfied but with minor concerns"
        style = random.choice([
            "Mention one small issue but overall positive",
            "Say it's good for the price",
            "Compare to similar products briefly",
            "Mention it does what's needed"
        ])
    elif rating == 3:
        tone = "neutral, it's okay but not amazing"
        style = random.choice([
            "Say it works but nothing special",
            "Mention it's average for the price",
            "Note some disappointments",
            "Say it gets the job done"
        ])
    elif rating == 2:
        tone = "disappointed"
        style = random.choice([
            "Mention specific problems encountered",
            "Say it didn't meet expectations",
            "Compare unfavorably to alternatives",
            "Note quality issues"
        ])
    else:  # rating == 1
        tone = "very dissatisfied"
        style = random.choice([
            "Describe major issues or failures",
            "Express frustration with quality",
            "Warn others to avoid",
            "Mention considering returning"
        ])
    
    prompt = f"""Write a short, casual customer review for a PC {product_type}.

IMPORTANT RULES:
- DO NOT mention the product name or brand at all
- Write like a real person texting, NOT like a formal review
- Use casual language: "pretty good", "works fine", "no complaints", etc.
- Be brief: 40-100 words MAX
- Sound natural and conversational
- Vary your writing style (some use punctuation, some don't, mix it up)

Context:
- Product type: {product_type}
- Price: {currency}{product_price}
- Rating: {rating}/5 stars
- Tone: {tone}
- Style: {style}

Examples of GOOD reviews (don't copy these, just match the style):
- "been using it for a month now, works great for gaming. no issues so far and the price was decent"
- "honestly expected more for the price. its okay but not amazing, does what i need though"
- "super happy with this upgrade! runs everything smoothly, definitely worth it"
- "meh, its alright. nothing special but gets the job done i guess"
- "had some issues at first but working fine now. would recommend for the price"

Write one casual review (40-100 words):"""
    
    try:
        response = model.generate_content(prompt)
        review = response.text.strip()
        
        # Remove any accidental product name mentions
        review = review.replace(product_name, "it")
        
        # Remove quotes if Gemini added them
        if review.startswith('"') and review.endswith('"'):
            review = review[1:-1]
        
        return review
    except Exception as e:
        print(f"Gemini Error: {e}")
        # Fallback casual reviews
        fallback_reviews = [
            f"works great, no complaints. been using it for a few weeks and its solid for the price",
            f"pretty happy with this purchase. does what i need and runs smooth",
            f"good value for {currency}{product_price}. would recommend",
            f"been running fine since i got it. no issues so far",
            f"honestly works better than expected. happy with it"
        ]
        return random.choice(fallback_reviews)

def save_review_to_firebase(review_data):
    """Save review to Firebase"""
    try:
        doc_ref = db.collection('reviews').document()
        doc_ref.set(review_data)
        return doc_ref.id
    except Exception as e:
        print(f"Firebase Error: {e}")
        return None

def get_reviews_from_firebase():
    """Get all reviews from Firebase"""
    try:
        reviews_ref = db.collection('reviews').order_by('date', direction=firestore.Query.DESCENDING).limit(50)
        reviews = reviews_ref.stream()
        
        review_list = []
        for review in reviews:
            review_data = review.to_dict()
            review_data['id'] = review.id
            review_list.append(review_data)
        
        return review_list
    except Exception as e:
        print(f"Firebase Fetch Error: {e}")
        return []

def generate_auto_review():
    """Generate one automatic review"""
    try:
        # Pick random product
        product = random.choice(PRODUCTS)
        
        # Decide currency (68% USD, 32% EUR)
        use_usd = random.random() < 0.68
        currency = "$" if use_usd else "€"
        price = product['priceUSD'] if use_usd else product['priceEUR']
        
        # Generate random rating (weighted towards positive)
        rating_weights = [2, 3, 8, 22, 65]  # 1-star: 2%, 2-star: 3%, 3: 8%, 4: 22%, 5: 65%
        rating = random.choices([1, 2, 3, 4, 5], weights=rating_weights)[0]
        
        # Get random name from database (no Gemini API call needed)
        user_name = get_random_name()
        
        # Generate review text
        review_text = generate_review_with_gemini(
            product['name'],
            price,
            currency,
            rating,
            user_name
        )
        
        # Create review object
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
        
        # Save to Firebase
        review_id = save_review_to_firebase(review_data)
        
        if review_id:
            print(f"✅ Auto-generated review: {user_name} reviewed {product['name']} ({rating}★)")
            return review_data
        else:
            print("❌ Failed to save auto-generated review")
            return None
            
    except Exception as e:
        print(f"Error generating auto review: {e}")
        return None

def auto_review_scheduler():
    """Background thread that generates reviews every 2-9 hours"""
    print("🤖 Auto-review scheduler started!")
    
    while True:
        try:
            # Generate one review
            generate_auto_review()
            
            # Wait random time between 2-9 hours
            hours = random.uniform(2, 9)
            seconds = hours * 3600
            
            print(f"⏰ Next review in {hours:.1f} hours")
            time.sleep(seconds)
            
        except Exception as e:
            print(f"Scheduler error: {e}")
            # If error, wait 1 hour and try again
            time.sleep(3600)

# ============================================
# API ROUTES
# ============================================

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    """Fetch all reviews"""
    try:
        reviews = get_reviews_from_firebase()
        return jsonify({
            'success': True,
            'reviews': reviews,
            'count': len(reviews)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reviews/generate', methods=['POST'])
def manual_generate_review():
    """Manually trigger review generation (for testing)"""
    try:
        review = generate_auto_review()
        if review:
            return jsonify({
                'success': True,
                'message': 'Review generated successfully',
                'review': review
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate review'
            }), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({
        'success': True,
        'message': 'Backend running!',
        'gemini_configured': GEMINI_API_KEY != 'YOUR_GEMINI_API_KEY_HERE',
        'firebase_initialized': firebase_admin._apps != {},
        'products_loaded': len(PRODUCTS)
    })

# ============================================
# STARTUP
# ============================================

# Start auto-review scheduler in background thread
scheduler_thread = threading.Thread(target=auto_review_scheduler, daemon=True)
scheduler_thread.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Server starting on port {port}")
    print(f"📦 Loaded {len(PRODUCTS)} products")
    print(f"🤖 Auto-review scheduler active (2-9 hour intervals)")
    app.run(host='0.0.0.0', port=port, debug=False)
