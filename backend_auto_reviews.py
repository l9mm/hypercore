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

db = firestore.client()

# ============================================
# PRODUCT DATABASE (Your 60 Products)
# ============================================

PRODUCTS = [
    # GPUs - Budget
    {"name": "GIGABYTE Radeon RX 9060 XT Gaming OC 16GB", "priceUSD": 378.99, "priceEUR": 349.99, "category": "GPU"},
    {"name": "Gigabyte GeForce RTX 3050 8GB", "priceUSD": 319.55, "priceEUR": 295.50, "category": "GPU"},
    {"name": "Sapphire Pulse Radeon RX 7600 8GB", "priceUSD": 247.99, "priceEUR": 229.00, "category": "GPU"},
    {"name": "ZOTAC GeForce RTX 5050 TWIN EDGE OC 8GB", "priceUSD": 238.99, "priceEUR": 220.99, "category": "GPU"},
    {"name": "MSI GeForce RTX 4060 VENTUS 2X BLACK 8G OC", "priceUSD": 292.00, "priceEUR": 270.00, "category": "GPU"},
    {"name": "PowerColor Fighter Radeon RX 7600 8GB", "priceUSD": 239.99, "priceEUR": 221.99, "category": "GPU"},
    
    # GPUs - Performance
    {"name": "ASUS ROG Strix GeForce RTX 4090 OC 24GB", "priceUSD": 1999.99, "priceEUR": 1849.00, "category": "GPU"},
    {"name": "MSI GeForce RTX 4080 SUPER 16G GAMING X SLIM", "priceUSD": 1199.99, "priceEUR": 1109.00, "category": "GPU"},
    {"name": "ASUS TUF Gaming Radeon RX 7900 XTX OC 24GB", "priceUSD": 949.99, "priceEUR": 879.00, "category": "GPU"},
    {"name": "Gigabyte GeForce RTX 4070 Ti SUPER GAMING OC 16G", "priceUSD": 849.99, "priceEUR": 785.99, "category": "GPU"},
    {"name": "Sapphire PULSE Radeon RX 6600 8GB", "priceUSD": 263.99, "priceEUR": 244.00, "category": "GPU"},
    {"name": "XFX Speedster MERC 310 Radeon RX 7900 XT 20GB", "priceUSD": 799.99, "priceEUR": 739.99, "category": "GPU"},
    
    # CPUs - Budget
    {"name": "AMD Ryzen 5 5600X", "priceUSD": 149.99, "priceEUR": 138.99, "category": "CPU"},
    {"name": "Intel Core i5-12400F", "priceUSD": 159.99, "priceEUR": 147.99, "category": "CPU"},
    {"name": "AMD Ryzen 5 7600", "priceUSD": 229.00, "priceEUR": 211.99, "category": "CPU"},
    {"name": "Intel Core i5-13400F", "priceUSD": 219.99, "priceEUR": 203.49, "category": "CPU"},
    {"name": "AMD Ryzen 7 5700X", "priceUSD": 179.99, "priceEUR": 166.49, "category": "CPU"},
    {"name": "Intel Core i5-14400F", "priceUSD": 209.99, "priceEUR": 194.00, "category": "CPU"},
    
    # CPUs - Performance
    {"name": "AMD Ryzen 9 7950X", "priceUSD": 549.99, "priceEUR": 508.49, "category": "CPU"},
    {"name": "Intel Core i9-14900K", "priceUSD": 589.99, "priceEUR": 545.49, "category": "CPU"},
    {"name": "AMD Ryzen 9 7900X", "priceUSD": 449.99, "priceEUR": 416.00, "category": "CPU"},
    {"name": "Intel Core i7-14700K", "priceUSD": 419.99, "priceEUR": 388.49, "category": "CPU"},
    {"name": "AMD Ryzen 7 7800X3D", "priceUSD": 449.00, "priceEUR": 415.00, "category": "CPU"},
    {"name": "Intel Core i9-13900KS", "priceUSD": 699.99, "priceEUR": 647.00, "category": "CPU"},
    
    # SSDs - Budget
    {"name": "WD Blue SN580 500GB PCIe 4.0 NVMe", "priceUSD": 52.99, "priceEUR": 48.99, "category": "SSD"},
    {"name": "Crucial T500 1TB PCIe 4.0 NVMe", "priceUSD": 89.99, "priceEUR": 83.19, "category": "SSD"},
    {"name": "Samsung 990 PRO 1TB PCIe 4.0 NVMe", "priceUSD": 119.99, "priceEUR": 110.99, "category": "SSD"},
    {"name": "Kingston NV2 1TB PCIe 4.0 NVMe", "priceUSD": 64.99, "priceEUR": 60.10, "category": "SSD"},
    {"name": "TeamGroup MP33 1TB PCIe 3.0 NVMe", "priceUSD": 54.99, "priceEUR": 50.85, "category": "SSD"},
    {"name": "Lexar NM790 1TB PCIe 4.0 NVMe", "priceUSD": 74.99, "priceEUR": 69.35, "category": "SSD"},
    
    # SSDs - Mainstream
    {"name": "Samsung 990 EVO Plus 2TB PCIe 4.0 NVMe", "priceUSD": 209.99, "priceEUR": 194.23, "category": "SSD"},
    {"name": "WD_BLACK SN850X 2TB PCIe 4.0 NVMe", "priceUSD": 179.99, "priceEUR": 166.49, "category": "SSD"},
    {"name": "Seagate FireCuda 530 2TB PCIe 4.0 NVMe", "priceUSD": 189.99, "priceEUR": 175.74, "category": "SSD"},
    {"name": "Crucial T705 2TB PCIe 5.0 NVMe", "priceUSD": 299.99, "priceEUR": 277.49, "category": "SSD"},
    {"name": "Kingston KC3000 2TB PCIe 4.0 NVMe", "priceUSD": 164.99, "priceEUR": 152.61, "category": "SSD"},
    {"name": "Corsair MP600 PRO LPX 2TB PCIe 4.0 NVMe", "priceUSD": 159.99, "priceEUR": 147.99, "category": "SSD"},
    {"name": "Silicon Power US75 4TB PCIe 4.0 NVMe", "priceUSD": 279.99, "priceEUR": 258.99, "category": "SSD"},
    
    # Monitors - VA
    {"name": "AOC CU34G2X 34\" Curved VA 144Hz", "priceUSD": 379.99, "priceEUR": 351.49, "category": "Monitor"},
    {"name": "Samsung Odyssey G5 32\" Curved VA 165Hz", "priceUSD": 299.99, "priceEUR": 277.49, "category": "Monitor"},
    {"name": "MSI MAG274QRF-QD 27\" Rapid VA 165Hz", "priceUSD": 329.99, "priceEUR": 305.24, "category": "Monitor"},
    {"name": "Gigabyte M32UC 32\" 4K VA 144Hz", "priceUSD": 549.99, "priceEUR": 508.49, "category": "Monitor"},
    {"name": "ASUS TUF Gaming VG27AQ 27\" IPS 165Hz", "priceUSD": 299.00, "priceEUR": 276.57, "category": "Monitor"},
    
    # Monitors - OLED
    {"name": "ASUS ROG Swift OLED PG27AQDM 27\" QHD 240Hz", "priceUSD": 899.99, "priceEUR": 832.49, "category": "Monitor"},
    {"name": "LG UltraGear 27GR95QE-B 27\" OLED 240Hz", "priceUSD": 999.99, "priceEUR": 924.99, "category": "Monitor"},
    {"name": "Alienware AW3423DWF 34\" QD-OLED 165Hz", "priceUSD": 899.99, "priceEUR": 832.49, "category": "Monitor"},
    {"name": "Samsung Odyssey OLED G9 49\" Dual QHD 240Hz", "priceUSD": 1799.99, "priceEUR": 1664.99, "category": "Monitor"},
    {"name": "MSI MEG 342C QD-OLED 34\" Curved 175Hz", "priceUSD": 949.99, "priceEUR": 878.74, "category": "Monitor"},
    {"name": "ASUS ROG Swift OLED PG42UQ 42\" 4K 138Hz", "priceUSD": 1299.99, "priceEUR": 1202.49, "category": "Monitor"},
    
    # RAM - DDR4
    {"name": "Corsair Vengeance LPX 16GB (2x8GB) DDR4-3200", "priceUSD": 39.99, "priceEUR": 36.99, "category": "RAM"},
    {"name": "G.Skill Ripjaws V 32GB (2x16GB) DDR4-3600", "priceUSD": 79.99, "priceEUR": 73.99, "category": "RAM"},
    {"name": "Kingston FURY Beast 16GB (2x8GB) DDR4-3200", "priceUSD": 42.99, "priceEUR": 39.76, "category": "RAM"},
    {"name": "Crucial Ballistix 32GB (2x16GB) DDR4-3600", "priceUSD": 89.99, "priceEUR": 83.24, "category": "RAM"},
    {"name": "TeamGroup T-Force Delta RGB 16GB (2x8GB) DDR4-3200", "priceUSD": 44.99, "priceEUR": 41.61, "category": "RAM"},
    {"name": "Patriot Viper Steel 32GB (2x16GB) DDR4-3600", "priceUSD": 84.99, "priceEUR": 78.61, "category": "RAM"},
    
    # RAM - DDR5
    {"name": "Corsair Vengeance 32GB (2x16GB) DDR5-5600", "priceUSD": 119.99, "priceEUR": 110.99, "category": "RAM"},
    {"name": "G.Skill Trident Z5 RGB 32GB (2x16GB) DDR5-6000", "priceUSD": 139.99, "priceEUR": 129.49, "category": "RAM"},
    {"name": "Kingston FURY Beast 32GB (2x16GB) DDR5-5600", "priceUSD": 114.99, "priceEUR": 106.36, "category": "RAM"},
    {"name": "Crucial 32GB (2x16GB) DDR5-5600", "priceUSD": 109.99, "priceEUR": 101.74, "category": "RAM"},
    {"name": "TeamGroup T-Force Delta RGB 32GB (2x16GB) DDR5-6000", "priceUSD": 129.99, "priceEUR": 120.24, "category": "RAM"},
    {"name": "Corsair Dominator Platinum RGB 32GB (2x16GB) DDR5-6400", "priceUSD": 179.99, "priceEUR": 166.49, "category": "RAM"}
]

# ============================================
# HELPER FUNCTIONS
# ============================================

def generate_name_with_gemini():
    """Generate a random realistic customer name using Gemini"""
    prompt = """Generate a single realistic customer name for product reviews. 
    Requirements:
    - First name and last name
    - Mix of common names from different countries
    - Sound natural and believable
    - Return ONLY the name, nothing else
    
    Example format: "Sarah Johnson" or "Alex Rodriguez"
    
    Generate one name:"""
    
    try:
        response = model.generate_content(prompt)
        name = response.text.strip().replace('"', '').replace("'", '')
        # If Gemini returns multiple lines, take first line
        name = name.split('\n')[0].strip()
        return name if name else "John Smith"
    except:
        # Fallback names if API fails
        fallback_names = [
            "Alex Johnson", "Sarah Chen", "Michael Rodriguez", "Emma Williams",
            "James Anderson", "Olivia Martinez", "Daniel Kim", "Sophia Taylor",
            "Ryan O'Connor", "Isabella Garcia", "Tyler Brown", "Ava Wilson",
            "Lucas Davis", "Mia Thompson", "Jordan Lee", "Zoe Martinez"
        ]
        return random.choice(fallback_names)

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
        
        # Generate name
        user_name = generate_name_with_gemini()
        
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
