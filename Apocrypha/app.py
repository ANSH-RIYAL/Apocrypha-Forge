from flask import Flask, render_template, request, redirect, flash, session
import os
import json
from datetime import datetime
import threading
import time
import subprocess

app = Flask(__name__, template_folder='templates')
print('>>> TEMPLATE FOLDER:', os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates')))
app.secret_key = 'apocrypha_secret_key'  # Needed for flash messages

# Always use the project root for interest_data.json
DATA_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'interest_data.json'))

# Ensure the data file exists at startup
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

# Helper to load and save JSON data
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except Exception:
            return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Save a submission to the JSON file
def save_submission(form_type, entry):
    data = load_data()
    if form_type not in data:
        data[form_type] = []
    entry['timestamp'] = datetime.utcnow().isoformat()
    data[form_type].append(entry)
    save_data(data)

# Git sync logic
def git_sync():
    try:
        github_id = os.environ.get('GITHUB_ID')
        github_email = os.environ.get('GITHUB_EMAIL')
        github_token = os.environ.get('GITHUB_TOKEN')
        if github_id and github_email and github_token:
            # Set git user config
            subprocess.run(['git', 'config', 'user.name', github_id], check=True)
            subprocess.run(['git', 'config', 'user.email', github_email], check=True)
            # Set remote url with token for authentication
            subprocess.run([
                'git', 'remote', 'set-url', 'origin',
                f'https://{github_id}:{github_token}@github.com/{github_id}/Apocrypha.git'
            ], check=True)
        subprocess.run(['git', 'add', DATA_FILE], check=True)
        subprocess.run(['git', 'commit', '-m', 'Sync interest data', '--allow-empty'], check=True)
        subprocess.run(['git', 'push'], check=True)
        print('Interest data synced to git.')
    except Exception as e:
        print(f'Git sync error: {e}')

def start_git_sync_thread():
    pass  # Remove threading logic

def get_email():
    return session.get('email', '')

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html', email=get_email())

@app.route('/vision')
def vision():
    return render_template('vision.html', email=get_email())

@app.route('/join')
def join():
    return render_template('join.html', email=get_email())

@app.route('/invest')
def invest():
    return render_template('invest.html', email=get_email())

@app.route('/karma')
def karma():
    return render_template('karma.html', email=get_email())

@app.route('/blog')
def blog():
    return render_template('blog.html', email=get_email())

@app.route('/faq')
def faq():
    return render_template('faq.html', email=get_email())

@app.route('/contact')
def contact():
    return render_template('contact.html', email=get_email())

# Form handlers
@app.route('/submit_suggestion', methods=['POST'])
def submit_suggestion():
    suggestion = request.form.get('suggestion')
    email = request.form.get('email')
    if email:
        session['email'] = email
    save_submission('suggestion', {'suggestion': suggestion, 'email': email})
    flash('Thank you for your suggestion!')
    return redirect('/')

@app.route('/submit_manifesto_feedback', methods=['POST'])
def submit_manifesto_feedback():
    feedback = request.form.get('feedback')
    email = request.form.get('email')
    if email:
        session['email'] = email
    save_submission('manifesto_feedback', {'feedback': feedback, 'email': email})
    flash('Thank you for your feedback!')
    return redirect('/vision')

@app.route('/submit_join', methods=['POST'])
def submit_join():
    interest = request.form.get('interest')
    email = request.form.get('email')
    if email:
        session['email'] = email
    save_submission('join', {'interest': interest, 'email': email})
    flash('Thank you for joining! We will be in touch.')
    return redirect('/join')

@app.route('/submit_micro_investor', methods=['POST'])
def submit_micro_investor():
    amount = request.form.get('amount')
    email = request.form.get('email')
    if email:
        session['email'] = email
    save_submission('micro_investor', {'amount': amount, 'email': email})
    flash('Thank you for your interest!')
    return redirect('/invest')

@app.route('/submit_institutional_investor', methods=['POST'])
def submit_institutional_investor():
    org = request.form.get('org')
    email = request.form.get('email')
    message = request.form.get('message')
    if email:
        session['email'] = email
    save_submission('institutional_investor', {'org': org, 'email': email, 'message': message})
    flash('Thank you for reaching out!')
    return redirect('/invest')

@app.route('/submit_karma_suggestion', methods=['POST'])
def submit_karma_suggestion():
    suggestion = request.form.get('karma_suggestion')
    email = request.form.get('email')
    if email:
        session['email'] = email
    save_submission('karma_suggestion', {'suggestion': suggestion, 'email': email})
    flash('Thank you for your suggestion!')
    return redirect('/karma')

@app.route('/submit_blog', methods=['POST'])
def submit_blog():
    content = request.form.get('blog_content')
    email = request.form.get('email')
    if email:
        session['email'] = email
    save_submission('blog', {'content': content, 'email': email})
    flash('Thank you for your submission!')
    return redirect('/blog')

@app.route('/submit_faq', methods=['POST'])
def submit_faq():
    question = request.form.get('faq_question')
    email = request.form.get('email')
    if email:
        session['email'] = email
    save_submission('faq', {'question': question, 'email': email})
    flash('Thank you for your question!')
    return redirect('/faq')

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    message = request.form.get('message')
    email = request.form.get('email')
    if email:
        session['email'] = email
    save_submission('contact', {'message': message, 'email': email})
    flash('Thank you for reaching out!')
    return redirect('/contact')

@app.route('/test')
def test():
    return 'Flask is working!'

@app.route('/sync_interest_data', methods=['POST'])
def sync_interest_data():
    git_sync()
    return 'Interest data synced to git.', 200

if __name__ == '__main__':
    print(">>> RUNNING FROM:", os.path.abspath(__file__))
    git_sync()  # Sync once at startup
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 