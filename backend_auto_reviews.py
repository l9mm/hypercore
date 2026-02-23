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
    """Generate realistic review using Gemini"""
    
    prompt = f"""Generate a realistic, detailed customer review for a PC component.

Product: {product_name}
Price: {currency}{product_price}
Rating: {rating}/5 stars
Customer: {user_name}

Requirements:
- Write from customer's perspective ({user_name} is reviewing this)
- Mention the price and whether it's good value
- Be specific about performance, quality, and features
- Mention real use cases (gaming, streaming, productivity, content creation)
- Include pros and cons if rating is 3-4 stars
- Be enthusiastic if 5 stars, balanced if 3-4 stars, critical if 1-2 stars
- Compare to alternatives if relevant
- 80-200 words
- Sound natural and human
- Don't mention AI generation

Write only the review text:"""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini Error: {e}")
        return f"Excellent product! The {product_name} at {currency}{product_price} is fantastic value. Highly recommended!"

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
