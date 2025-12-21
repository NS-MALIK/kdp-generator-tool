# app.py
import random
import os
import sys

from flask import Flask, render_template, request,Response
import requests
# --- PATH CORRECTION FOR VERCEL ---
# This adds the root directory to the Python path so it can find data.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can safely import from the root directory
from data import NICHES, THEMES, MODIFIERS 

# Tell Flask where to find templates and static files relative to this file
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

@app.route('/sitemap.xml')
def sitemap():
    # Ensure the XML is served with the correct header
    return Response(render_template('sitemap.xml'), mimetype='text/xml')


@app.route('/.well-known/security.txt')
@app.route('/security.txt')
def security_txt():
    content = (
        "Contact: mailto:contact@alphacoder.com\n"
        "Expires: 2026-12-31T23:59:59.000Z\n"
        "Preferred-Languages: en\n"
        "Policy: https://kdp-generator-tool.vercel.app/privacy\n"
        "Hiring: https://kdp-generator-tool.vercel.app/about\n"
    )
    return Response(content, mimetype='text/plain')
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')



@app.route('/api/cron/ping-google')
def ping_google():
    if request.headers.get('Authorization') != f"Bearer {os.environ.get('CRON_SECRET')}":
     return "Unauthorized", 401
    # This is the standard Google Sitemap ping URL
    sitemap_url = "https://kdp-generator-tool.vercel.app/sitemap.xml"
    google_ping = f"https://www.google.com/ping?sitemap={sitemap_url}"
    
    try:
        response = requests.get(google_ping)
        if response.status_code == 200:
            return {"status": "success", "message": "Google notified"}, 200
        else:
            return {"status": "error", "message": "Failed to notify Google"}, 500
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500
@app.route('/blog')
def blog_home():
   return render_template('blog_home.html')

@app.route('/blog/low-content-book-ideas-2025')
def blog_post_one():
    # This matches the folder structure we planned earlier
    return render_template('blog/low-content-ideas-2025.html')
@app.route('/', methods=['GET', 'POST'])
def index():
    generated_ideas = []
    error = None # Initialize error as None
    niches_list = NICHES 
    
    if request.method == 'POST':
        # 2. VERIFY RECAPTCHA
        secret_key = os.getenv('RECAPTCHA_SECRET_KEY') # Get from Vercel Environment Variables
        recaptcha_response = request.form.get('g-recaptcha-response')
        
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        payload = {
            'secret': secret_key,
            'response': recaptcha_response
        }
        
        verification = requests.post(verify_url, data=payload).json()
        
        if not verification.get('success'):
            # If the check fails, set the error message
            error = "Please complete the 'I am human' check to proceed."
        else:
            # 3. PROCEED WITH GENERATION IF HUMAN
            selected_niche = request.form.get('niche_input')
            
            if selected_niche:
                user_niche = selected_niche.strip() 
                for _ in range(15):
                    modifier = random.choice(MODIFIERS)
                    theme = random.choice(THEMES)
                    idea = f"{modifier} {theme} for {user_niche}"
                    generated_ideas.append(idea)
        
    # 4. PASS THE ERROR TO THE TEMPLATE
    return render_template('index.html', niches=niches_list, ideas=generated_ideas, error=error)

